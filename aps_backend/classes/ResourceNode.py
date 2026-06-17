from ProcessNode import ProcessNode

class ResourceNode:
    def __init__(self, resource_id: str, resource_type: str = "Machine"):
        # Properties
        self.id: str = resource_id                  # Unique ID
        self.type: str = resource_type              # e.g., "Machine", "Human"
        
        # Tracking references
        self.assigned_operations: list[ProcessNode] = []         # List of ProcessNodes that can use this resource
        self.unavailable_windows: list[tuple[int, int]] = []         # List of tuples [(start, end)] for maintenance/down periods

    def register_operation(self, process_node):
        """Keeps track of all operations competing for this resource's capacity."""
        if process_node not in self.assigned_operations:
            self.assigned_operations.append(process_node)

    def add_maintenance_window(self, start_time: int, end_time: int):
        """Registers blackout dates where the machine cannot run."""
        self.unavailable_windows.append((start_time, end_time))

    def get_all_process_nodes(self) -> list['ProcessNode']:
            """Returns the raw list of jobs assigned to this resource."""
            return self.assigned_operations
