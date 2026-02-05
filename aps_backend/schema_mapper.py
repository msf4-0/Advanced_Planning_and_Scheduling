
"""
SchemaMapper: Dynamic schema mapping and discovery for PostgreSQL/Apache AGE

Features:
- Load/save mapping config from file or database (JSON or mapping_config table)
- Discover tables and columns in PostgreSQL
- Discover node labels and edge types in Apache AGE (graph)
- Provide mapping info to other components for schema-agnostic scheduling

Usage:
	db_params = { ... }
	mapper = SchemaMapper(db_params)
	tables = mapper.list_tables()
	columns = mapper.list_columns('orders')
	labels = mapper.list_graph_labels()
	mapping = mapper.get_mapping()
	mapper.update_mapping(new_mapping, use_db=True)
"""

import json
import psycopg2
import logging
from typing import Dict, Any, Optional

class SchemaMapper:
	"""
	Handles dynamic schema mapping and discovery for both relational (PostgreSQL) and graph (Apache AGE) data sources.
	Allows loading/saving mapping config from file or DB, and schema introspection for both data models.
	"""
	def __init__(self, conn: psycopg2.extensions.connection, config_path: str = "configs/config.json"):
		"""
		Args:
			db_params: dict with PostgreSQL connection params
			config_path: path to mapping config file (default: configs/config.json)
		"""
		self.conn = conn
		self.config_path = config_path
		self.config = self.load_mapping_from_file()
		# logging.info(f"(SCHEMA-MAP) Loaded mapping config: {self.config}")

	# --- FILE-BASED MAPPING ---

	def load_mapping_from_file(self) -> Dict[str, Any]:
		"""
		Load mapping config from a local JSON file.
		Returns: dict mapping config, or empty dict if not found/invalid.
		"""
		try:
			with open(self.config_path, 'r') as f:
				# logging.info(f"(SCHEMA-MAP) Loading mapping config from file: {self.config_path}")
				return json.load(f)
		except (FileNotFoundError, json.JSONDecodeError):
			logging.error(f"(SCHEMA-MAP) Failed to load mapping config from file: {self.config_path}")
			return {}

	def save_mapping_to_file(self, mapping: Dict[str, Any]):
		"""
		Save mapping config to a local JSON file.
		Args:
			mapping: dict to save
		"""
		with open(self.config_path, 'w') as f:
			json.dump(mapping, f, indent=2)
		self.config = mapping

	# --- DB-BASED MAPPING ---

	def load_mapping_from_db(self) -> Dict[str, Any]:
		"""
		Load mapping config from the mapping_config table in the database.
		Returns: dict mapping config, or empty dict if not found.
		"""
			
		cur = self.conn.cursor()
		cur.execute("SELECT config FROM mapping_config ORDER BY updated_at DESC LIMIT 1;")
		row = cur.fetchone()
		cur.close()
		self.conn.close()
		if row:
			return row[0]
		return {}

	def save_mapping_to_db(self, mapping: Dict[str, Any]):
		"""
		Save mapping config to the mapping_config table in the database.
		Args:
			mapping: dict to save
		"""

		cur = self.conn.cursor()
		cur.execute(
			"""
			INSERT INTO mapping_config (config, updated_at)
			VALUES (%s, NOW())
			""",
			(json.dumps(mapping),)
		)
		self.conn.commit()
		cur.close()
		self.conn.close()
		self.config = mapping

	# --- SCHEMA DISCOVERY (PostgreSQL) ---

	def list_tables(self) -> list:
		"""
		List all user tables in the public schema of PostgreSQL.
		Returns: list of table names
		"""

		cur = self.conn.cursor()
		cur.execute("""
			SELECT table_name FROM information_schema.tables
			WHERE table_schema = 'public';
		""")
		tables = [row[0] for row in cur.fetchall()]
		cur.close()
		self.conn.close()
		return tables

	def list_columns(self, table_name: str) -> list:
		"""
		List all columns and their types for a given table.
		Args:
			table_name: name of the table
		Returns: list of (column_name, data_type)
		"""
		cur = self.conn.cursor()
		cur.execute("""
			  	SELECT 
				c.column_name,
				c.data_type,
				c.is_nullable,
				c.column_default,
				EXISTS (
					SELECT 1
					FROM information_schema.table_constraints tc
					JOIN information_schema.key_column_usage kcu
					ON tc.constraint_name = kcu.constraint_name
					AND tc.table_schema = kcu.table_schema
					WHERE tc.constraint_type = 'PRIMARY KEY'
					AND tc.table_name = c.table_name
					AND kcu.column_name = c.column_name
				) AS is_primary_key
				FROM information_schema.columns c
				WHERE c.table_name = %s;
			""", (table_name,))
		
		rows = cur.fetchall()

		if cur.description is not None:
			columns = [
				dict(zip([d[0] for d in cur.description], row))
				for row in rows
			]
		else:
			columns = [{}]

		cur.close()
		self.conn.close()
		return columns

	# --- SCHEMA DISCOVERY (Apache AGE Graph) ---

	def list_graph_label_with_properties(self, graph_name: str = 'production_graph') -> list[dict]:
		"""
		Get all node labels and their properties in the given Apache AGE graph.
		Args:
			graph_name: name of the graph (default: production_graph)
		Returns: list of dicts: [{"label": ..., "properties": [...]}, ...]
		"""

		cur = self.conn.cursor()
		cur.execute(f"""
			SELECT DISTINCT labels(n)[1] as label FROM cypher('{graph_name}', $$
				MATCH (n) RETURN labels(n)
			$$) AS (labels agtype);
		""")
		labels = [row[0] for row in cur.fetchall()]

		result = []
		for label in labels:
			# Get properties for this label
			cur.execute(f"""
				SELECT DISTINCT jsonb_object_keys(properties(n)) FROM cypher('{graph_name}', $$
					MATCH (n:{label}) RETURN properties(n)
				$$) AS (props jsonb);
			""")
			props = [row[0] for row in cur.fetchall()]
			result.append({"label": label, "properties": props})
		cur.close()
		self.conn.close()
		return result
	
	def list_graph_labels(self, graph_name: str = 'production_graph') -> list[str]:
		"""
		List all node labels in the given Apache AGE graph.
		Args:
			graph_name: name of the graph (default: production_graph)
		Returns: list of node labels
		"""
		cur = self.conn.cursor()
		cur.execute(f"""
			SELECT DISTINCT labels(n)[1] as label FROM cypher('{graph_name}', $$
				MATCH (n) RETURN labels(n)
			$$) AS (labels agtype);
		""")
		labels = [row[0] for row in cur.fetchall()]
		cur.close()
		self.conn.close()
		return labels

	def list_graph_edge_types(self, graph_name: str = 'production_graph') -> list[dict]:
		"""
		List all edge types, their properties, and source/target node labels in the given Apache AGE graph.
		Args:
			graph_name: name of the graph (default: production_graph)
		Returns: list of dicts: [{"edge_type": ..., "properties": [...], "source_labels": [...], "target_labels": [...]}, ...]
		"""
		cur = self.conn.cursor()
		cur.execute(f"""
			SELECT DISTINCT type(r) as edge_type FROM cypher('{graph_name}', $$
				MATCH ()-[r]->() RETURN type(r)
			$$) AS (type agtype);
		""")
		edge_types = [row[0] for row in cur.fetchall()]
		result = []
		for edge_type in edge_types:
			# Get properties for this edge type
			cur.execute(f"""
				SELECT DISTINCT jsonb_object_keys(properties(r)) FROM cypher('{graph_name}', $$
					MATCH ()-[r:{edge_type}]->() RETURN properties(r)
				$$) AS (props jsonb);
			""")
			props = [row[0] for row in cur.fetchall()]

			# Get source labels
			cur.execute(f"""
				SELECT DISTINCT labels(a)[1] FROM cypher('{graph_name}', $$
					MATCH (a)-[r:{edge_type}]->(b) RETURN labels(a)
				$$) AS (labels agtype);
			""")
			source_labels = [row[0] for row in cur.fetchall()]

			# Get target labels
			cur.execute(f"""
				SELECT DISTINCT labels(b)[1] FROM cypher('{graph_name}', $$
					MATCH (a)-[r:{edge_type}]->(b) RETURN labels(b)
				$$) AS (labels agtype);
			""")
			target_labels = [row[0] for row in cur.fetchall()]

			result.append({
				"edge_type": edge_type,
				"properties": props,
				"source_labels": source_labels,
				"target_labels": target_labels
			})
		cur.close()
		self.conn.close()
		return result

	# --- MAPPING ACCESS ---

	def get_mapping(self) -> Dict[str, Any]:
		"""
		Get the current mapping config (from file or last loaded from DB).
		Returns: dict mapping config
		"""
		logging.info(f"Getting current mapping config: {self.config}")
		return self.config


	def update_mapping(self, mapping: Dict[str, Any], use_db: bool = False):
		"""
		Update the mapping config, saving to file or DB as specified.
		Args:
			mapping: dict to save
			use_db: if True, save to DB; else, save to file
		"""
		if use_db:
			self.save_mapping_to_db(mapping)
		else:
			self.save_mapping_to_file(mapping)

	# --- EXAMPLE: GET JOB MAPPING ---

	def get_job_mapping(self) -> Optional[Dict[str, str]]:
		"""
		Example: Get mapping for jobs (table/columns or graph labels/props).
		Returns: dict or None
		"""
		return self.config.get('job_mapping')
