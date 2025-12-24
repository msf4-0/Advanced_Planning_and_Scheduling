Tables
- inventory
- machines
- materials
- operations
- orders
- products

Graph-node
- product
- operation
- inventory?
- machine
- materials

Graph-Connections

- (products) - [HAS_STEP] -> (OpStep)
- (OpStep) - [HAS_OPERATION]