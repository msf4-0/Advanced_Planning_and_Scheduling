-- =========================================================================
-- ADVANCED PLANNING & SCHEDULING (APS) MOCK DATA SEED SCRIPT
-- =========================================================================

-- Clean out existing data before seeding to prevent primary key duplicates
-- Tables are truncated in reverse dependency order
TRUNCATE TABLE scheduling_runs RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
TRUNCATE TABLE routing_templates RESTART IDENTITY CASCADE;
TRUNCATE TABLE items CASCADE;
TRUNCATE TABLE factory_holidays RESTART IDENTITY CASCADE;
TRUNCATE TABLE factory_shifts RESTART IDENTITY CASCADE;
TRUNCATE TABLE operation_materials CASCADE;
TRUNCATE TABLE operation_dependencies CASCADE;
TRUNCATE TABLE operations CASCADE;
TRUNCATE TABLE work_orders CASCADE;
TRUNCATE TABLE materials CASCADE;
TRUNCATE TABLE resources CASCADE;

-- =========================================================================
-- 1. SEED RESOURCES / WORK CENTERS (Table: resources)
-- =========================================================================
INSERT INTO resources (id, name, resource_type, is_active) VALUES
('machine_cnc_01',  'CNC Lathe Alpha',      'Machine', TRUE),
('machine_cnc_02',  'CNC Milling Beta',     'Machine', TRUE),
('machine_laser_01','Laser Cutter Gamma',   'Machine', TRUE),
('station_assem_01','Assembly Station 1',   'Human',   TRUE),
('station_qc_01',   'Quality Control Bench','Human',   TRUE);

-- =========================================================================
-- 2. SEED MATERIAL INVENTORY BALANCE (Table: materials)
-- =========================================================================
INSERT INTO materials (id, name, quantity_available, available_date_minutes) VALUES
('mat_steel_bar',   '10mm Stainless Steel Bar', 150.0000, 0),   -- Available immediately
('mat_aluminum_plt','6mm Aluminum Sheet Plate',  85.0000, 0),   -- Available immediately
('mat_microchip_a1','Logic Controller Unit A1',  12.0000, 180), -- Arrives at Minute 180 (3 hours out)
('mat_copper_wire', 'Industrial Copper Wiring', 500.0000, 0);   -- Available immediately

-- =========================================================================
-- 3. SEED PRODUCT ITEM MASTER CATALOG (Table: items)
-- =========================================================================
INSERT INTO items (id, name, sku) VALUES
('prod_servo_motor', 'High-Torque Servo Motor V2', 'SKU-SERVO-002'),
('prod_metal_encl',  'Custom Aluminum Enclosure',  'SKU-ENCL-991');

-- =========================================================================
-- 4. SEED ROUTING BLUEPRINT TEMPLATES (Table: routing_templates)
-- =========================================================================
-- Blueprint for Servo Motor (Requires CNC -> Assembly -> Quality Control)
INSERT INTO routing_templates (target_item_id, step_sequence, required_resource_type, standard_duration_minutes) VALUES
('prod_servo_motor', 10, 'Machine', 45), -- CNC Step
('prod_servo_motor', 20, 'Human',   30), -- Assembly Step
('prod_servo_motor', 30, 'Human',   15); -- QC Step

-- Blueprint for Metal Enclosure (Requires Laser Cutting -> Assembly)
INSERT INTO routing_templates (target_item_id, step_sequence, required_resource_type, standard_duration_minutes) VALUES
('prod_metal_encl',  10, 'Machine', 20), -- Laser Step
('prod_metal_encl',  20, 'Human',   25); -- Assembly Step

-- =========================================================================
-- 5. SEED LIVE DEMAND LIVE MANUFACTURING ORDERS (Table: work_orders)
-- =========================================================================
INSERT INTO work_orders (id, target_item_id, quantity_to_make, due_date, status) VALUES
('WO-2026-001', 'prod_servo_motor', 10, NOW() + INTERVAL '2 days', 'Draft'),
('WO-2026-002', 'prod_metal_encl',  25, NOW() + INTERVAL '3 days', 'Draft'),
('WO-2026-003', 'prod_servo_motor',  5, NOW() + INTERVAL '1 day',  'Draft');

-- =========================================================================
-- 6. SEED WORK ORDER OPERATIONS RUNTIME INSTANCES (Table: operations)
-- =========================================================================
-- Target assignments are distributed to test machine constraint resource capacity
INSERT INTO operations (id, work_order_id, sequence_number, duration_minutes, assigned_resource_id, status) VALUES
-- Operations for WO-2026-001 (Servo Motor)
('op_wo1_10', 'WO-2026-001', 10, 45, 'machine_cnc_01',  'Draft'),
('op_wo1_20', 'WO-2026-001', 20, 30, 'station_assem_01', 'Draft'),
('op_wo1_30', 'WO-2026-001', 30, 15, 'station_qc_01',    'Draft'),

-- Operations for WO-2026-002 (Metal Enclosure)
-- Competes with WO1 on the same Assembly Station
('op_wo2_10', 'WO-2026-002', 10, 20, 'machine_laser_01', 'Draft'),
('op_wo2_20', 'WO-2026-002', 20, 25, 'station_assem_01', 'Draft'),

-- Operations for WO-2026-003 (Urgent Servo Motor Batch)
-- Competes with WO1 on the CNC Lathe machine capacity
('op_wo3_10', 'WO-2026-003', 10, 30, 'machine_cnc_01',  'Draft'),
('op_wo3_20', 'WO-2026-003', 20, 20, 'station_assem_01', 'Draft'),
('op_wo3_30', 'WO-2026-003', 30, 10, 'station_qc_01',    'Draft');

-- =========================================================================
-- 7. SEED DIRECTED ACYCLIC GRAPH EDGES (Table: operation_dependencies)
-- =========================================================================
-- This structures the sequential dependencies within each individual job
INSERT INTO operation_dependencies (upstream_op_id, downstream_op_id) VALUES
-- WO1 sequence logic: Step 10 -> Step 20 -> Step 30
('op_wo1_10', 'op_wo1_20'),
('op_wo1_20', 'op_wo1_30'),

-- WO2 sequence logic: Step 10 -> Step 20
('op_wo2_10', 'op_wo2_20'),

-- WO3 sequence logic: Step 10 -> Step 20 -> Step 30
('op_wo3_10', 'op_wo3_20'),
('op_wo3_20', 'op_wo3_30');

-- =========================================================================
-- 8. SEED BILL OF MATERIALS DRAW REQUIREMENTS (Table: operation_materials)
-- =========================================================================
INSERT INTO operation_materials (operation_id, material_id, quantity_required) VALUES
-- WO1 Step 10 draws steel bars, Step 20 draws microchips and copper wires
('op_wo1_10', 'mat_steel_bar',    2.5000),
('op_wo1_20', 'mat_microchip_a1',  1.0000), -- Bound to the delay (Minute 180 arrival)
('op_wo1_20', 'mat_copper_wire',  15.0000),

-- WO2 Step 10 draws aluminum sheets
('op_wo2_10', 'mat_aluminum_plt',  0.7500),

-- WO3 Step 10 draws steel bars, Step 20 draws microchips
('op_wo3_10', 'mat_steel_bar',    1.2500),
('op_wo3_20', 'mat_microchip_a1',  1.0000);

-- =========================================================================
-- 9. SEED STANDARD CAPACITY WORK SHIFTS (Table: factory_shifts)
-- =========================================================================
-- Populates a basic 8:00 AM to 5:00 PM shift structure for Monday (1) through Friday (5)
INSERT INTO factory_shifts (resource_id, day_of_week, start_time, end_time) VALUES
('machine_cnc_01',   1, '08:00:00', '17:00:00'),
('machine_cnc_01',   2, '08:00:00', '17:00:00'),
('machine_cnc_01',   3, '08:00:00', '17:00:00'),
('machine_cnc_01',   4, '08:00:00', '17:00:00'),
('machine_cnc_01',   5, '08:00:00', '17:00:00'),

('station_assem_01', 1, '08:00:00', '17:00:00'),
('station_assem_01', 2, '08:00:00', '17:00:00'),
('station_assem_01', 3, '08:00:00', '17:00:00'),
('station_assem_01', 4, '08:00:00', '17:00:00'),
('station_assem_01', 5, '08:00:00', '17:00:00');

-- =========================================================================
-- 10. SEED ACCESS CONTROL SYSTEM USERS (Table: users)
-- =========================================================================
-- Initializing seed user credentials for administrative logging access control
INSERT INTO users (username, password_hash, role) VALUES
('admin_planner', '$2b$12$K39pX8LAsdfv019234857ulajskdfh12394857ahskdfj', 'Admin');
