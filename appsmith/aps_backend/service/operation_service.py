from typing_extensions import Optional

from models import OperationRead
from repository.db_repository import DBTable

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

        if material_needed:
            material = self.db.fetch_material(material_name=material_needed)
            if material:
                material_id = material['material_id']
            else:
                material_id = self.db.add_material(material_needed)
        
        operation_id = self.db.add_operation(
            name=name, 
            required_machine_type=required_machine_type, 
            duration=duration,
            material_id=material_id
        )

        if operation_id is None:
            raise ValueError("Failed to create operation.")
        
        row = self.db.fetch_operations(operation_id=operation_id)
        
        if not row:
            raise ValueError("Operation not found after creation.")

        operation = OperationRead(
            operation_id=row[0]['operation_id'],
            name=row[0]['operation_name'],
            duration=row[0]['duration'],
            machine_type=row[0]['machine_type'],
            material_id=row[0].get('material_id')
        )

        return operation