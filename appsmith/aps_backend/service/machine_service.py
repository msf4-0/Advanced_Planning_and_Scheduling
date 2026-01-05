from typing_extensions import Optional
from repository.db_repository import DBTable

class MachineService:
    def __init__(self, db: DBTable):
        self.db = db

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