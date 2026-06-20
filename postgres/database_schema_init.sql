-- =========================================================================
-- ADVANCED PLANNING & SCHEDULING (APS) DATABASE INITIALIZATION SCRIPT
-- =========================================================================

-- 1. DROP EXISTING TABLES IN REVERSE ORDER OF FOREIGN KEY DEPENDENCIES
DROP TABLE IF EXISTS scheduling_runs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS routing_templates CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS factory_holidays CASCADE;
DROP TABLE IF EXISTS factory_shifts CASCADE;
DROP TABLE IF EXISTS operation_materials CASCADE;
DROP TABLE IF EXISTS operation_dependencies CASCADE;
DROP TABLE IF EXISTS operations CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS resources CASCADE;

-- =========================================================================
-- ZONE A: CORE FACTORY MODEL (DYNAMIC INPUTS & LIVE STATE)
-- =========================================================================

-- 1. Resources / Work Centers
CREATE TABLE resources (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'Machine', -- 'Machine', 'Human', 'Tooling'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE resources IS 'Physical production assets and shop floor capacities capable of executing factory routing tasks.';
COMMENT ON COLUMN resources.id IS 'Unique identifier for the work center. Maps to ResourceNode.id (e.g., workstation name from ERPNext).';
COMMENT ON COLUMN resources.resource_type IS 'The resource categorization boundary. Acceptable types include: Machine, Human, Tooling.';
COMMENT ON COLUMN resources.is_active IS 'Toggle constraint flag to temporarily remove broken or unavailable assets from the solver view.';

-- 2. Materials / Inventory Items
CREATE TABLE materials (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity_available NUMERIC(12, 4) DEFAULT 0.0,
    available_date_minutes INT DEFAULT 0 -- Earliest available time converted to timeline integer minutes
);

COMMENT ON TABLE materials IS 'Raw raw stock material tracking registry ledger used for bill-of-materials restriction lookups.';
COMMENT ON COLUMN materials.id IS 'Unique material stock keeping code identifier. Maps to the Item Code properties in ERPNext.';
COMMENT ON COLUMN materials.quantity_available IS 'The raw numeric current physical stock level available immediately inside warehouse storage containers.';
COMMENT ON COLUMN materials.available_date_minutes IS 'Calculated timeline arrival offset integer representing when upcoming purchase receipts land on disk.';

-- 3. Manufacturing / Work Orders
CREATE TABLE work_orders (
    id VARCHAR(50) PRIMARY KEY,
    target_item_id VARCHAR(50) NOT NULL,
    quantity_to_make INT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Draft' -- 'Draft', 'Scheduled', 'In Progress', 'Done'
);

COMMENT ON TABLE work_orders IS 'The ultimate parent customer demand orders anchoring manufacturing requirements.';
COMMENT ON COLUMN work_orders.id IS 'Primary Work Order sequence code key (e.g., standard serialized nomenclature MFG-WO-2026-00001).';
COMMENT ON COLUMN work_orders.due_date IS 'The ultimate customer delivery deadline used by the solver objective loop to calculate total system lateness.';
COMMENT ON COLUMN work_orders.status IS 'Transactional state lifecycles: Draft, Approved, Scheduled, In Progress, Done.';

-- =========================================================================
-- ZONE B: THE GRAPH ENGINE & RESULTS (THE TRANSITION LAYER)
-- =========================================================================

-- 4. Operations / Processing Steps
CREATE TABLE operations (
    id VARCHAR(50) PRIMARY KEY,
    work_order_id VARCHAR(50) REFERENCES work_orders(id) ON DELETE CASCADE,
    sequence_number INT NOT NULL,     -- Route hierarchy tracking (10, 20, 30...)
    duration_minutes INT NOT NULL,    
    assigned_resource_id VARCHAR(50) REFERENCES resources(id),
    
    -- OUTPUT SCHEDULE RESULTS COMPUTED BY GOOGLE OR-TOOLS
    optimized_start_minute INT DEFAULT -1, 
    optimized_end_minute INT DEFAULT -1,
    scheduled_start_time TIMESTAMP NULL,
    scheduled_end_time TIMESTAMP NULL
);

COMMENT ON TABLE operations IS 'Individual step-by-step processing tasks that populate active memory as ProcessNode graph objects.';
COMMENT ON COLUMN operations.id IS 'Unique child operation step primary key. Instantiated via ERPNext child table operation row hashes.';
COMMENT ON COLUMN operations.sequence_number IS 'The engineering workflow route processing hierarchy priority order index (e.g., 10, 20, 30).';
COMMENT ON COLUMN operations.duration_minutes IS 'The raw processing runtime capacity window required to execute the job task step block.';
COMMENT ON COLUMN operations.optimized_start_minute IS 'The raw mathematical integer solution output variable calculated by Google OR-Tools CP-SAT solver.';
COMMENT ON COLUMN operations.scheduled_start_time IS 'Real calendar datetime timestamp string calculated by combining current pipeline run execution baseline and optimized minutes.';

-- 5. DAG Edges Matrix (Connects operations as a structural network graph in memory)
CREATE TABLE operation_dependencies (
    upstream_op_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    downstream_op_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    PRIMARY KEY (upstream_op_id, downstream_op_id)
);

COMMENT ON TABLE operation_dependencies IS 'The multi-dependency network adjacency matrix storing directed acyclic graph (DAG) connection pointers.';
COMMENT ON COLUMN operation_dependencies.upstream_op_id IS 'The source operation block task required to finish executing first before unlocking the subsequent child node path.';
COMMENT ON COLUMN operation_dependencies.downstream_op_id IS 'The destination dependent operation step blocked until the preceding parental processing window collapses.';

-- 6. Operation Materials Link (BOM Requirements)
CREATE TABLE operation_materials (
    operation_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    material_id VARCHAR(50) REFERENCES materials(id) ON DELETE CASCADE,
    quantity_required NUMERIC(12, 4) NOT NULL,
    PRIMARY KEY (operation_id, material_id)
);

COMMENT ON TABLE operation_materials IS 'Junction profile link defining specific bill of materials inventory draw demands for particular operations.';

-- =========================================================================
-- ZONE C: CALENDARS, SHIFTS, & ITEM MASTER TEMPLATES
-- =========================================================================

-- 7. Factory Work Shifts
CREATE TABLE factory_shifts (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(50) REFERENCES resources(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7), -- 1 (Monday) to 7 (Sunday)
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

COMMENT ON TABLE factory_shifts IS 'Operational working time parameters defining resource runtime availability ranges across the weekly horizon.';

-- 8. Factory Closures & Holidays
CREATE TABLE factory_holidays (
    id SERIAL PRIMARY KEY,
    holiday_date DATE UNIQUE NOT NULL,
    description VARCHAR(100)
);

COMMENT ON TABLE factory_holidays IS 'Global blackout dates representing factory closures where all processing variables are strictly frozen.';

-- 9. Product Masters (SKU Blueprint Library)
CREATE TABLE items (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL
);

COMMENT ON TABLE items IS 'The item master master definition catalog profile storing finished product templates.';

-- 10. Routing Blueprint Templates (Used to auto-generate operations for new orders)
CREATE TABLE routing_templates (
    id SERIAL PRIMARY KEY,
    target_item_id VARCHAR(50) REFERENCES items(id) ON DELETE CASCADE,
    step_sequence INT NOT NULL,
    required_resource_type VARCHAR(50) NOT NULL,
    standard_duration_minutes INT NOT NULL
);

COMMENT ON TABLE routing_templates IS 'Engineering blueprint masters used to auto-generate baseline operations arrays whenever a fresh manufacturing request arrives.';

-- =========================================================================
-- ZONE D: MANAGEMENT, RUN LOGS, & ACCESS CONTROL
-- =========================================================================

-- 11. System Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Planner' -- 'Admin', 'Planner', 'Viewer'
);

-- 12. Optimization Run History (Auditing Engine Activity)
CREATE TABLE scheduling_runs (
    id SERIAL PRIMARY KEY,
    triggered_by INT REFERENCES users(id) ON DELETE SET NULL,
    run_status VARCHAR(20) NOT NULL,  -- 'Running', 'Success', 'Failed'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    log_messages TEXT                 -- Captures solver stats or data errors
);

COMMENT ON TABLE scheduling_runs IS 'System audit history tracking logs recording calculation run states, duration markers, and solver exceptions.';

-- =========================================================================
-- INDEX OPTIMIZATIONS
-- =========================================================================
CREATE INDEX idx_ops_work_order ON operations(work_order_id);
CREATE INDEX idx_ops_resource ON operations(assigned_resource_id);
CREATE INDEX idx_shifts_resource ON factory_shifts(resource_id);
CREATE INDEX idx_routing_item ON routing_templates(target_item_id);
