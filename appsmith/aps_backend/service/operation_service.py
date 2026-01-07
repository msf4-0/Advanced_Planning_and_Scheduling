from typing_extensions import Optional

from models import OperationRead
from repository import DBTable, GraphEditor

class OperationService:
    def __init__(self, db: DBTable):
        self.db = db

    def add_operation(
        self, 
        name: str, 
        required_machine_type: str, 
        duration: int, 
        material_needed: Optional[str] = None
    ) -> OperationRead:
        """
        Add a new operation to the database.

        Args:
            name (str): The name of the operation.
            required_machine_type (str): The type of machine required for the operation.
            duration (int): The duration of the operation in minutes.
            material_id (Optional[int]): The ID of the material needed for the operation.

        Returns:
            int: The ID of the newly created operation.
        """

        material_id = None

        # Check and add material if needed
        if material_needed and material_needed.strip():
            material = self.db.fetch_material(material_name=material_needed)
            if material:
                material_id = material['material_id']
            else:
                material_id, _ = self.db.add_material(material_needed)
        
        # Check machine type existence
        machine_type = self.db.fetch_machine_types(type_name=required_machine_type)

        # Raise error if machine type does not exist
        if not machine_type:
            raise ValueError(f"Machine type '{required_machine_type}' does not exist.")
        else:
            type_id = machine_type[0]['type_id']

        operation_id = self.db.add_operation(
            name=name, 
            type_id=type_id, 
            duration=duration,
            material_id=material_id
        )

        if operation_id is None:
            raise ValueError("Failed to create operation. DB add_operation returned None.")
        
        row = self.db.fetch_operations(operation_id=operation_id)
        
        if not row:
            raise ValueError("Operation not found after creation.")

        operation = OperationRead(
            operation_id=row[0]['operation_id'],
            name=row[0]['name'],
            duration=row[0]['duration'],
            machine_type=row[0]['type_id'],
            material_id=row[0].get('material_id')
        )

        return operation
    
    def generate_operation_node(self, operation_id: int):
        """
        Generate an operation node for the given operation ID.

        Args:
            operation_id (int): The ID of the operation.
        Returns:
            dict: The operation node details.
        """
        operation = self.db.fetch_operations(operation_id=operation_id)
        if not operation:
            raise ValueError(f"Operation with ID {operation_id} does not exist.")
        
        operation_row = operation[0]
        graph_editor = GraphEditor(self.db)

        operation_node = {
            "operation_id": operation_row['operation_id'],
            "duration": operation_row['duration'],
            "machine_type": operation_row['type_id'],
            "material_id": operation_row.get('material_id')
        }

        graph_editor.create_node('Operation', operation_node)
        return operation_node