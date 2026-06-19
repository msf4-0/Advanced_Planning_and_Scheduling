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

-- 2. Materials / Inventory Items
CREATE TABLE materials (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity_available NUMERIC(12, 4) DEFAULT 0.0,
    available_date_minutes INT DEFAULT 0 -- Earliest available time converted to timeline integer minutes
);

-- 3. Manufacturing / Work Orders
CREATE TABLE work_orders (
    id VARCHAR(50) PRIMARY KEY,
    target_item_id VARCHAR(50) NOT NULL,
    quantity_to_make INT NOT NULL,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Draft' -- 'Draft', 'Scheduled', 'In Progress', 'Done'
);

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

-- 5. DAG Edges Matrix (Connects operations as a structural network graph in memory)
CREATE TABLE operation_dependencies (
    upstream_op_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    downstream_op_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    PRIMARY KEY (upstream_op_id, downstream_op_id)
);

-- 6. Operation Materials Link (BOM Requirements)
CREATE TABLE operation_materials (
    operation_id VARCHAR(50) REFERENCES operations(id) ON DELETE CASCADE,
    material_id VARCHAR(50) REFERENCES materials(id) ON DELETE CASCADE,
    quantity_required NUMERIC(12, 4) NOT NULL,
    PRIMARY KEY (operation_id, material_id)
);

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

-- 8. Factory Closures & Holidays
CREATE TABLE factory_holidays (
    id SERIAL PRIMARY KEY,
    holiday_date DATE UNIQUE NOT NULL,
    description VARCHAR(100)
);

-- 9. Product Masters (SKU Blueprint Library)
CREATE TABLE items (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL
);

-- 10. Routing Blueprint Templates (Used to auto-generate operations for new orders)
CREATE TABLE routing_templates (
    id SERIAL PRIMARY KEY,
    target_item_id VARCHAR(50) REFERENCES items(id) ON DELETE CASCADE,
    step_sequence INT NOT NULL,
    required_resource_type VARCHAR(50) NOT NULL,
    standard_duration_minutes INT NOT NULL
);

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

-- =========================================================================
-- INDEX OPTIMIZATIONS (Ensures lightning-fast ingestion for your Python RAM loader)
-- =========================================================================
CREATE INDEX idx_ops_work_order ON operations(work_order_id);
CREATE INDEX idx_ops_resource ON operations(assigned_resource_id);
CREATE INDEX idx_shifts_resource ON factory_shifts(resource_id);
CREATE INDEX idx_routing_item ON routing_templates(target_item_id);
