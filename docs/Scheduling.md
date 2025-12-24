ERD (Facts / Master Data)                  Graph (Process / Sequences)
------------------------                  ---------------------------
+----------------+                        +----------------+
|   Orders       |                        |   Product Node |
|----------------|                        |----------------|
| order_id       |<-----------------------| product_id     |
| product_id     |                        +----------------+
| priority       |                               |
| due_date       |                               |
| quantity       |                               |
+----------------+                               |
                                                 |
+----------------+                               |
|   Products     |-------------------------------+
|----------------|   (anchor node for OpSteps)
| product_id     |
| name           |
+----------------+

+----------------+                        +--------------------------------+
|   Machines     |                        |   OpStep Node                  |
|----------------|                        |--------------------------------|
| machine_id     |<-----------------------| op_step_id                     |
| name           |                        | product_id                     |
| type           |                        | sequence                       |
| capacity       |                        | operation_id -> Operation Node |
+----------------+                        +--------------------------------+
                                                 |
+----------------+                               |
|   Operations   |<------------------------------+
|----------------|   (referenced by OpStep)
| operation_id   |
| name           |
| duration       |
| machine_type   |
+----------------+

+----------------+                        +-------------------+
|  Inventory     |                        |  (optional)       |
|----------------|                        |  linked to        |
| item_id        |                        |  OpStep/Operation |
| item_name      |                        |  for consumption  |
| quantity       |                        +-------------------+
| min_required   |
| max_capacity   |
| last_updated   |
| received_at    |
| material_id    |
+----------------+

+----------------+                        +--------------------+
|  Materials     |                        |  (optional)        |
|----------------|                        |  linked to         |
| material_id    |------------------------|  OpStep/Operation  |
| name           |                        +--------------------+
| unit_cost      |
+----------------+
