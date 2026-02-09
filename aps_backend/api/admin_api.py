from fastapi import APIRouter, Body, HTTPException
from typing_extensions import List
from typing import Dict
from schema_mapper import SchemaMapper
from repository import DBTable
import logging

router = APIRouter()



# --------------- Schema Discovery Endpoints --------------- #
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

	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())
	
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

	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())
	
	columns = schema_mapper.list_columns(table_name)
	return columns

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
	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())

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
	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())
	
	edge_types = schema_mapper.list_graph_edge_types()
	return edge_types



# --------------- Mapping Configuration Endpoints --------------- #
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

	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())

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

	db = DBTable()
	schema_mapper = SchemaMapper(db.get_connection_graph())

	schema_mapper.update_mapping(mapping)
	return {"status": "Mapping updated successfully."}


# --------------- Table Schema Operations Endpoints --------------- #
@router.put(
		"/admin/new-table/{table_name}",
		response_model=Dict,
		tags=["Admin"]
		)
def create_new_table(table_name: str, columns: List[dict] = Body(None)):
	'''
	Get the schema details of a specific table.\n\n

	table_name (str): The name of the table to create.\n
	columns (list[dict]): A list of dicts, each with keys:\n
		- name (str): column name\n
		- type (str): SQL data type\n
		- default (optional): default value\n
		- nullable (optional): bool\n
		- primary_key (optional): bool\n
		- unique (optional): bool\n
		- foreign_key (optional): str, e.g. 'other_table(other_id)'\n\n

	Location: appsmith/aps_backend/admin_api.py
	'''

	db = DBTable()

	logging.info(f"Creating table {table_name}")

	table = db.create_table(table_name, columns)

	if not table:
		raise HTTPException(status_code=400, detail="Table creation failed.")

	return {"created": table}

@router.delete(
		"/admin/delete-table/{table_name}",
		response_model=Dict,
		tags=["Admin"]
		)
def drop_table(table_name: str):
	'''
	Delete a specific table from the database.

	Location: appsmith/aps_backend/admin_api.py
	'''

	db = DBTable()

	logging.info(f"Dropping table {table_name}")

	dropped = db.drop_table(table_name)

	if not dropped:
		raise HTTPException(status_code=400, detail="Table drop failed.")

	return {"dropped": dropped}

@router.post(
		"/admin/add-table-column/{table_name}",
		response_model=Dict,
		tags=["Admin"]
		)
def add_table_column(
	table_name: str, 
	column: list[dict] = Body(...)
	):
	'''
	Add a new column to a specific table.

	'''
	db = DBTable()
	added = db.add_table_column(
		table_name, 
		column
		)
	if not added:
		raise HTTPException(status_code=400, detail="Column addition failed.")
	
	return {"added": added}
	

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

	db = DBTable()

	edited = db.edit_table_column(
		table_name, 
		old_column, 
		new_column, 
		new_type, 
		default_value
		)
	
	if not edited:
		raise HTTPException(status_code=400, detail="Column edit failed.")

	return {"edited": edited}

