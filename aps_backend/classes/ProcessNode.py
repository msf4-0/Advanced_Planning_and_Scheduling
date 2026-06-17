from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SupplyNode import SupplyNode
    from ResourceNode import ResourceNode

class ProcessNode:
    def __init__(self, operation_id: str, duration: int, job_id: str = ""):
        # Base Properties
        self.id: str = operation_id                # Unique ID
        self.job_id: str = job_id        # Parent Work Order ID
        self.duration: int = duration              # Processing time
        
        # Graph Edges (Pointers to other objects in RAM)
        self.input_materials: list[SupplyNode] = []             # List of SupplyNode objects required
        self.output_materials: list[SupplyNode] = []            # List of SupplyNode objects generated
        self.next_operations: list[ProcessNode] = []             # Sequential downstream ProcessNodes (DAG)
        self.previous_operations: list[ProcessNode] = []         # Sequential upstream ProcessNodes (DAG)
        self.compatible_resources: list[ResourceNode] = []        # Eligible ResourceNode objects (Bipartite)

        self.optimized_start: int = -1
        self.optimized_end: int = -1

    def add_next_operation(self, next_node):
        """Creates a sequential directional edge to a downstream task (DAG)."""
        if next_node not in self.next_operations:
            self.next_operations.append(next_node)
            next_node.previous_operations.append(self)

    def add_compatible_resource(self, resource_node):
        """Binds a machine/workstation that is capable of running this operation (Bipartite)."""
        if resource_node not in self.compatible_resources:
            self.compatible_resources.append(resource_node)
            resource_node.register_operation(self)

    def get_earliest_material_date(self) -> int:
        """Returns the absolute earliest time this step can start based on its inventory dependencies."""
        if not self.input_materials:
            return 0
        return max(material.available_date for material in self.input_materials)
