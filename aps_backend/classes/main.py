import sys
from APSEngine import APSEngine

def run():
    print("""
        ==========================================\n
          APS OPTIMIZATION ENGINE PIPELINE START  \n
        ==========================================\n
        """)

    # STEP 1: INITIALIZE THE REPOSITORY LAYER
    print("[1/4] Connecting to database repository...")
    # repo = DBRepository()
    
    # STEP 2: EXTRACT DATA & GENERATE THE IN-MEMORY GRAPH
    print("[2/4] Fetching flat records and building the RAM graph twin...")
    
    # The repository will execute SQL queries to build your list of objects.
    # process_nodes, resource_nodes = repo.fetch_and_build_graph()
    
    # --- Dummy Data Setup (Delete this block once your DBRepository is built) ---
    from ProcessNode import ProcessNode
    from ResourceNode import ResourceNode
    
    # Simulate Machine Alpha
    machine_alpha = ResourceNode(resource_id="machine_01", resource_type="Lathe")
    
    # Simulate two jobs that compete for Machine Alpha
    op1 = ProcessNode(operation_id="op_101", duration=45, job_id="job_A")
    op2 = ProcessNode(operation_id="op_102", duration=30, job_id="job_A")
    
    # Link them sequentially (op2 happens after op1)
    op1.next_operations.append(op2)
    op2.previous_operations.append(op1)
    
    # Register both jobs to compete for Machine Alpha's capacity
    machine_alpha.register_operation(op1)
    machine_alpha.register_operation(op2)
    
    process_nodes = [op1, op2]
    resource_nodes = [machine_alpha]
    # -------------------------------------------------------------------------

    print(f"      Graph ready: {len(process_nodes)} operations, {len(resource_nodes)} resources loaded.")

    # STEP 3: EXECUTE MATHEMATICAL OPTIMIZATION
    print("[3/4] Initializing APSEngine (Planning Horizon: 14 Days)...")
    engine = APSEngine(horizon_days=14)
    
    print("      Running Google OR-Tools CP-SAT Solver...")
    result_status = engine.build_and_solve(process_nodes, resource_nodes)

    # STEP 4: EVALUATE RESULTS AND SAVE
    if result_status == "SUCCESS":
        print("\n[4/4] Optimization Successful! Extracting calculated schedule:")
        print("----------------------------------------------------------")
        for op in process_nodes:
            print(f"      Task ID: {op.id:<8} | Job: {op.job_id:<6} | Start Minute: {op.optimized_start:<4} | End Minute: {op.optimized_end:<4}")
        print("----------------------------------------------------------")
        
        print("      Writing optimized timestamps back to the relational database...")
        # repo.save_optimized_schedule(process_nodes)
        print("\n==========================================")
        print("        PIPELINE COMPLETED SUCCESSFULLY   ")
        print("==========================================")
    else:
        print(f"\n[!] Pipeline Failed: {result_status}")
        print("    Please verify resource capacities, calendars, or job links for deadlocks.")
        sys.exit(1)

if __name__ == "__main__":
    run()