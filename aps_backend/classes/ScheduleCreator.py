from datetime import datetime, timedelta
from typing import Dict, List, Any

from APSEngine import APSEngine
from aps_backend.classes.ProcessNode import ProcessNode
from aps_backend.classes.ResourceNode import ResourceNode
from aps_backend.classes.SupplyNode import SupplyNode
from repository import Repository, DatabaseConfig, ConnectionManager

def run() -> dict:
    """
    Orchestrates data extraction, builds the in-memory graph twin,
    executes Google OR-Tools optimization, and saves timestamps back to DB.
    """
    print("""
        ==========================================
          APS OPTIMIZATION ENGINE PIPELINE START  
        ==========================================
        """)

    # STEP 1: INITIALIZE THE REPOSITORY LAYER
    print("[1/4] Connecting to database repository...")
    config = DatabaseConfig()
    conn_manager = ConnectionManager(config)

    resource_repo = Repository("resources", conn_manager)
    material_repo = Repository("materials", conn_manager)
    operation_repo = Repository("operations", conn_manager)
    dependency_repo = Repository("operation_dependencies", conn_manager)
    material_required_repo = Repository("operation_materials", conn_manager)
    work_order_repo = Repository("work_orders", conn_manager)  # ← NEW
    runs_log_repo = Repository("scheduling_runs", conn_manager)

    # STEP 2: EXTRACT DATA & GENERATE THE IN-MEMORY GRAPH
    print("[2/4] Fetching flat records and building the RAM graph twin...")

    # Fetch data from DB
    db_resources = resource_repo.fetch_all()
    db_materials = material_repo.fetch_all()
    db_operations = operation_repo.fetch_all()
    db_dependencies = dependency_repo.fetch_all()
    db_material_requirements = material_required_repo.fetch_all()

    # A. Map the 'resources' table rows into ResourceNode Objects
    resource_nodes = {}
    for resource in db_resources:
        if resource.get("is_active", True):
            resource_nodes[resource["id"]] = ResourceNode(
                resource_id=resource["id"],
                resource_type=resource["resource_type"]
            )

    # B. Map the 'operations' table rows into ProcessNode Objects
    process_nodes = {}
    for operation in db_operations:
        # Ignore completed jobs
        if operation.get("status") == "done":
            continue

        node = ProcessNode(
            operation_id=operation["id"],
            duration=operation["duration_minutes"],
            job_id=operation["work_order_id"]
        )
        process_nodes[operation["id"]] = node

        # Link the capacity: register ProcessNode to its assigned resource
        assigned_resource_id = operation["assigned_resource_id"]
        if assigned_resource_id in resource_nodes:
            resource_nodes[assigned_resource_id].register_operation(node)

    # C. Add the graph edges using the 'operation_dependencies' table
    for edge in db_dependencies:
        upstream_id = edge["upstream_op_id"]
        downstream_id = edge["downstream_op_id"]

        # Connect object pointers if both target nodes exist in the active graph
        if (upstream_id in process_nodes) and (downstream_id in process_nodes):
            upstream_node = process_nodes[upstream_id]
            downstream_node = process_nodes[downstream_id]

            upstream_node.add_next_operation(downstream_node)

    # D1. Map the 'materials' table rows into typed SupplyNode objects
    supply_nodes = {}
    for material in db_materials:
        supply_nodes[material["id"]] = SupplyNode(
            materialId=material["id"],
            name=material["name"],
            quantityAvailable=float(material["quantity_available"]),
            available_date=material["available_date_minutes"]
        )

    # D2. Assign the created SupplyNode objects to ProcessNode.input_materials list
    for required in db_material_requirements:
        operation_id = required["operation_id"]
        material_id = required["material_id"]

        # Verify both nodes exist in memory
        if (operation_id in process_nodes) and (material_id in supply_nodes):
            current_process_node = process_nodes[operation_id]
            current_supply_node = supply_nodes[material_id]

            current_process_node.add_input_material(current_supply_node)

    print(f"      Graph ready: {len(process_nodes)} operations, {len(resource_nodes)} resources, {len(supply_nodes)} inventory items loaded.")

    # STEP 3: EXECUTE MATHEMATICAL OPTIMIZATION
    print("[3/4] Initializing APSEngine (Planning Horizon: 14 Days)...")
    engine = APSEngine(horizon_days=14)

    print("      Running Google OR-Tools CP-SAT Solver...")
    process_node_list = list(process_nodes.values())
    resource_node_list = list(resource_nodes.values())

    result_status = engine.build_and_solve(process_node_list, resource_node_list)

    # STEP 4: EVALUATE RESULTS AND SAVE
    if result_status == "SUCCESS":
        print("\n[4/4] Optimization Successful! Extracting calculated schedule:")
        print("----------------------------------------------------------")
        for operation in process_node_list:
            print(f"      Task ID: {operation.id:<8} | Job: {operation.job_id:<6} | Start Minute: {operation.optimized_start:<4} | End Minute: {operation.optimized_end:<4}")
        print("----------------------------------------------------------")

        print("      Writing optimized timestamps back to the relational database...")

        # Calculate real baseline timestamp for minute 0
        baseline_time = datetime.now()
        output_summary = {}

        updates_batch = []

        # Iterate through solved process node list and prepare update records
        for operation in process_node_list:
            # Convert solved minutes to actual dates
            scheduled_start = baseline_time + timedelta(minutes=int(operation.optimized_start))
            scheduled_end = baseline_time + timedelta(minutes=int(operation.optimized_end))
            
            # Prepare update record (includes the ID to match the record)
            update_record = {
                "id": operation.id,
                "optimized_start_minute": int(operation.optimized_start),
                "optimized_end_minute": int(operation.optimized_end),
                "scheduled_start_time": scheduled_start,
                "scheduled_end_time": scheduled_end
            }
            updates_batch.append(update_record)
            
            # Build output summary
            output_summary[operation.id] = {
                "work_order_id": operation.job_id,
                "start_minute": int(operation.optimized_start),
                "end_minute": int(operation.optimized_end),
                "start_time": scheduled_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": scheduled_end.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Execute batch update for operations
        total_updated = operation_repo.batch_update(updates_batch, id_column="id")
        print(f"      ✓ Batch updated {total_updated} operations with scheduling times")
        
        # Get unique work_order IDs that were scheduled
        work_order_ids = set(op.job_id for op in process_node_list)
        
        work_order_updates = [
            {"id": wo_id, "status": "Scheduled"}
            for wo_id in work_order_ids
        ]
        
        if work_order_updates:
            total_wo_updated = work_order_repo.batch_update(work_order_updates, id_column="id")
            print(f"      ✓ Updated {total_wo_updated} work orders to 'Scheduled' status")
        
        # ========== STEP 4C: Log success ==========
        runs_log_repo.add(data={
            "run_status": "Success",
            "completed_at": datetime.now(),
            "log_messages": f"Engine successfully optimized and processed {len(process_node_list)} shop floor operations. Scheduled {len(work_order_ids)} work orders."
        })

        print("\n==========================================")
        print("        PIPELINE COMPLETED SUCCESSFULLY   ")
        print("==========================================")
        return output_summary
        
    else:
        print(f"\n[!] Pipeline Failed: {result_status}")
        runs_log_repo.add(data={
            "run_status": "Failed",
            "completed_at": datetime.now(),
            "log_messages": f"Solver Engine optimization failed with output token status: {result_status}"
        })
        raise ValueError(f"APS Optimization Pipeline failed with status code token: {result_status}")


if __name__ == "__main__":
    run()