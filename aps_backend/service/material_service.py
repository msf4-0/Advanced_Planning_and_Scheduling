from repository import GraphEditor, DBTable
from typing import Optional

class MaterialService:
    def __init__(self, db: DBTable):
        self.db = db

    def fetch_material(
            self, 
            material_id: Optional[int] = None, 
            material_name: Optional[str] = None
            ) -> list[dict]:
        
        return self.db.fetch_material(
            material_id=material_id, 
            material_name=material_name
        )
    
    def add_material(
            self, 
            material_name: str
            ) -> tuple[Optional[int], Optional[bool]]:
        """
        Add a new material to the database.

        Args:
            material_name (str): The name of the material.

        Returns:
            tuple[Optional[int], Optional[bool]]: The ID of the newly created material and a boolean indicating if it already existed.
        """

        return self.db.add_material(material_name=material_name)
    
    def generate_material_node(self, material_id: int) -> dict:
        """
        Generate a material node for the given material ID.

        Args:
            material_id (int): The ID of the material.

        Returns:
            dict: The properties of the generated material node.
        """

        try:
            graph_editor = GraphEditor(self.db)
            material_prop = self.db.fetch_material(material_id=material_id)

            if not material_prop:
                raise ValueError(f"Material with ID {material_id} does not exist.")

            material_node = graph_editor.get_node('Material', {'material_id': material_id})

            if material_node:
                return material_node[0]
            
            material_node = graph_editor.create_node(
                label="Material",
                properties={
                    "material_id": material_prop[0]['material_id'],
                }
            )

            return material_node
        except Exception as e:
            raise ValueError(f"Failed to generate material node [MaterialService.generate_material_node]: {str(e)}")