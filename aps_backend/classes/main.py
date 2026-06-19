import sys

from numpy.matlib import require
from APSEngine import APSEngine
from aps_backend.classes.ProcessNode import ProcessNode
from aps_backend.classes.ResourceNode import ResourceNode
from aps_backend.classes.SupplyNode import SupplyNode
from repository import Repository, DatabaseConfig, ConnectionManager

def run():
    print("""
        ==========================================\n
          APS OPTIMIZATION ENGINE PIPELINE START  \n
        ==========================================\n
        """)

    # STEP 1: INITIALIZE THE REPOSITORY LAYER
    print("[1/4] Connecting to database repository...")
    config = DatabaseConfig()
    conn_manager = ConnectionManager(config)

    resourceRepo = Repository("resources", conn_manager)
    materialRepo = Repository("materials", conn_manager)
    operationRepo = Repository("operations", conn_manager)
    depedencyRepo = Repository("operation_dependencies", conn_manager)
    materialRequiredRepo = Repository("operation_materials", conn_manager)

    # STEP 2: EXTRACT DATA & GENERATE THE IN-MEMORY GRAPH
    print("[2/4] Fetching flat records and building the RAM graph twin...")

    # Fetch data from DB
    dbResources = resourceRepo.fetch_all()
    dbMaterials = materialRepo.fetch_all()
    dbOperation = operationRepo.fetch_all()
    dbDepedencies = depedencyRepo.fetch_all()
    dbMaterialRequirement = materialRequiredRepo.fetch_all()

    # A. Map the 'resources' table rows into ResourceNode Objects
    resourceNodes = {}
    for resource in dbResources:
        if resource.get("is_active", True):
            resourceNodes[resource["id"]] = ResourceNode(
                resource_id=resource["id"],
                resource_type=resource["resource_type"]
            )

    # B. Map the 'operations' table rows into ProcessNode Objects
    processNodes = {}
    for operation in dbOperation:
        # ignore completed jobs
        if operation.get("status") == "done":
            continue

        node = ProcessNode(
            operation_id=operation["id"],
            duration=operation["duration_minutes"],
            job_id=operation["work_order_id"]
        )
        processNodes[operation["id"]] = node

        # Link the capacity: register ProcessNode to its assigned resource
        assignedResourceID = operation["assigned_resource_id"]
        if assignedResourceID in resourceNodes:
            resourceNodes[assignedResourceID].register_operation(node)

    # C. add the graph edges using the 'operation_depedencies' table
    for edge in dbDepedencies:
        upstream_id = edge["upstream_op_id"]
        downstream_id = edge["downstream_op_id"]

        # Connect objectpointers if both target nodes exists in the active graph
        if (upstream_id in processNodes) and (downstream_id in processNodes):
            upstreamNode = processNodes[upstream_id]
            downstreamNode = processNodes[downstream_id]

            upstreamNode.add_next_operation(downstreamNode)

    # D1. Map the 'materials' table rows into typed SupplyNode objects
    supplyNodes = {}
    for material in dbMaterials:
        supplyNodes[material["id"]] = SupplyNode(
            materialId=material["id"],
            name=material["name"],
            quantityAvailable=float(material["quantity_available"]),
            available_date=material["available_date_minutes"]
        )

    # D2. Assign the created SupplyNode objects to ProcessNode.input_materials list
    for required in dbMaterialRequirement:
        operationId = required["operation_id"]
        materialId = required["material_id"]

        # Verify both nodes exists in memory
        if (operationId in processNodes) and (materialId in supplyNodes):
            currentProcessNode = processNodes[operationId]
            currentSupplyNode = supplyNodes[materialId]

            currentProcessNode.add_input_material(currentSupplyNode)


    print(f"      Graph ready: {len(processNodes)} operations, {len(resourceNodes)} resources, {len(supplyNodes)} inventory items loaded.")

    # STEP 3: EXECUTE MATHEMATICAL OPTIMIZATION
    print("[3/4] Initializing APSEngine (Planning Horizon: 14 Days)...")
    engine = APSEngine(horizon_days=14)

    print("      Running Google OR-Tools CP-SAT Solver...")
    processNodeList = list(processNodes.values())
    resourceNodeList = list(resourceNodes.values())

    result_status = engine.build_and_solve(processNodeList, resourceNodeList)

    # STEP 4: EVALUATE RESULTS AND SAVE
    if result_status == "SUCCESS":
        print("\n[4/4] Optimization Successful! Extracting calculated schedule:")
        print("----------------------------------------------------------")
        for op in processNodes:
            print(f"      Task ID: {op.id:<8} | Job: {op.job_id:<6} | Start Minute: {op.optimized_start:<4} | End Minute: {op.optimized_end:<4}")
        print("----------------------------------------------------------")

        print("      Writing optimized timestamps back to the relational database...")
        # repo.save_optimized_schedule(processNodes)
        print("\n==========================================")
        print("        PIPELINE COMPLETED SUCCESSFULLY   ")
        print("==========================================")
    else:
        print(f"\n[!] Pipeline Failed: {result_status}")
        print("    Please verify resource capacities, calendars, or job links for deadlocks.")
        sys.exit(1)

if __name__ == "__main__":
    run()
