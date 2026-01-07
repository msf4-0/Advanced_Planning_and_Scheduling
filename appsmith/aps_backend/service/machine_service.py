from typing_extensions import Optional
from repository import DBTable, GraphEditor

class MachineService:
    def __init__(self, db: DBTable):
        self.db = db

    def fetch_machine(
            self, 
            machine_id: Optional[int] = None, 
            machine_name: Optional[str] = None
            ) -> list[dict]:
        
        return self.db.fetch_machines(
            machine_id=machine_id, 
            machine_name=machine_name
        )

    def add_machine(
        self, 
        name: str, 
        machine_type: str, 
        capacity: Optional[int] = None
    ) -> int:
        """
        Add a new machine to the database, ensuring unique naming.

        Args:
            name (str): The name of the machine.
            machine_type (str): The type/category of the machine.
            capacity (Optional[int]): The capacity of the machine.

        Returns:
            int: The ID of the newly created machine.
        """

        machines = self.db.fetch_machines(machine_name=name)
        existing_names = [machine['name'] for machine in machines]

        if name not in existing_names:
            final_name = name
        else:
            max_suffix = 1
            for n in existing_names:
                if n == name:
                    continue
                if n.startswith(f"{name}_"):
                    try:
                        suffix = int(n[len(name) + 1 :])
                        max_suffix = max(max_suffix, suffix + 1)
                    except ValueError:
                        continue
            final_name = f"{name}_{max_suffix}"

        machine_type_id = self.db.fetch_machine_types(type_name=machine_type)

        if not machine_type_id:
            machine_type_id = self.db.add_machine_type(type_name=machine_type)
            if machine_type_id == -1:
                raise ValueError("Failed to input new machine type.")
        else:
            machine_type_id = machine_type_id[0]['type_id']

        machine_id = self.db.add_machine(
            name=final_name,
            type_id=machine_type_id,
            capacity=capacity
        )

        if machine_id is None:
            raise ValueError("Failed to input new machine.")
        
        return machine_id
    
    def generate_machine_node(self, machine_id: int):
        """
        Generate a machine node for the given machine ID.

        Args:
            machine_id (int): The ID of the machine.
        """

        graph_editor = GraphEditor(self.db)
        machine_property = self.db.fetch_machines(machine_id=machine_id)

        if not machine_property:
            raise FileNotFoundError(f"Machine with ID {machine_id} does not exist.")

        success = graph_editor.create_node('Machines', machine_property[0])

        if not success:
            raise ValueError("[MachineService.generate_machine_node] Err: Failed to generate machine node.")