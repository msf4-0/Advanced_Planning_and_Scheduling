from fastapi import APIRouter, Body
from typing_extensions import List
from typing import Dict
from schema_mapper import SchemaMapper
from repository import DBTable



router = APIRouter()
db = DBTable()
schema_mapper = SchemaMapper(db.get_connection())


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

	labels = schema_mapper.list_graph_label_with_properties()
	return labels

@router.get(
	"/admin/graph/edge-types",
	response_model=List[Dict],
	tags=["Admin"]
)
def list_graph_edge_types():
	'''
	List all edge types, their properties, and source/target node labels in the graph database.

	Location: appsmith/aps_backend/admin_api.py
	'''

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
	
	schema_mapper.update_mapping(mapping)
	return {"status": "Mapping updated successfully."}


# Table Schema Operations Endpoints
@router.put(
		"/admin/new-table/{table_name}",
		response_model=Dict,
		tags=["Admin"]
		)
def get_table_schema(table_name: str, columns: List[tuple] = Body(...)):
	'''
	Get the schema details of a specific table.

	Location: appsmith/aps_backend/admin_api.py
	'''

	created = db.create_table(table_name, columns)
	return {"created": created}

@router.post(
		"/admin/edit-table-column/{table_name}",
		response_model=Dict,
		tags=["Admin"]
		)
def edit_table_column(
	table_name: str, 
	old_column: str = Body(...), 
	new_column: str = Body(...), 
	new_type: str = Body(...),
	default_value: str = Body(None)
	):
	'''
	Edit a column in a specific table.

	Location: appsmith/aps_backend/admin_api.py
	'''

	edited = db.edit_table_column(
		table_name, 
		old_column, 
		new_column, 
		new_type, 
		default_value
		)

	return {"edited": edited}