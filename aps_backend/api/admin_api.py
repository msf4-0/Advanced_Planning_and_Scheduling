from fastapi import APIRouter, Body
from typing_extensions import List
from typing import Dict
from schema_mapper import SchemaMapper
from repository import DBTable



router = APIRouter()
db = DBTable()


# Schema Discovery Endpoints
@router.get(
		"/admin/tables",
		response_model=List[str],
		tags=["Admin"]
		)
def list_tables():
	'''
	List all tables in the database.

	Location: appsmith/aps_backend/admin_api.py
	'''
	
	schema_mapper = SchemaMapper(db.get_connection())
	tables = schema_mapper.list_tables()
	return tables

@router.get(
		"/admin/columns/{table_name}",
		response_model=List[dict],
		tags=["Admin"]
		)
def list_columns(table_name: str):
	'''
	List all columns for a given table.

	Location: appsmith/aps_backend/admin_api.py
	'''
	
	schema_mapper = SchemaMapper(db.get_connection())
	columns = schema_mapper.list_columns(table_name)
	return [{"column_name": col[0], "data_type": col[1]} for col in columns]

@router.get(
	"/admin/graph/labels",
	response_model=List[Dict],
	tags=["Admin"]
)
def list_graph_labels():
	'''
	List all node labels and their properties in the graph database.

	Location: appsmith/aps_backend/admin_api.py
	'''
	schema_mapper = SchemaMapper(db.get_connection())
	labels = schema_mapper.list_graph_label_with_properties()
	return labels

@router.get(
	"/admin/graph/edge_types",
	response_model=List[Dict],
	tags=["Admin"]
)
def list_graph_edge_types():
	'''
	List all edge types, their properties, and source/target node labels in the graph database.

	Location: appsmith/aps_backend/admin_api.py
	'''
	schema_mapper = SchemaMapper(db.get_connection())
	edge_types = schema_mapper.list_graph_edge_types()
	return edge_types



# Mapping Configuration Endpoints
@router.get(
		"/admin/mapping/",
		response_model=Dict,
		tags=["Admin"]
		)
def get_mapping():
	'''
	Get the current schema mapping configuration.

	Location: appsmith/aps_backend/admin_api.py
	'''
	schema_mapper = SchemaMapper(db.get_connection())
	mapping = schema_mapper.get_mapping()
	return mapping

@router.post(
		"/admin/mapping/",
		response_model=Dict,
		tags=["Admin"]
		)
def set_mapping(mapping: Dict = Body(...)):
	'''
	Set or update the schema mapping configuration.

	Location: appsmith/aps_backend/admin_api.py
	'''
	schema_mapper = SchemaMapper(db.get_connection())
	schema_mapper.update_mapping(mapping)
	return {"status": "Mapping updated successfully."}