
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
from typing import Dict, Any, Optional

class SchemaMapper:
	"""
	Handles dynamic schema mapping and discovery for both relational (PostgreSQL) and graph (Apache AGE) data sources.
	Allows loading/saving mapping config from file or DB, and schema introspection for both data models.
	"""
	def __init__(self, db_params: dict, config_path: str = "config.json"):
		"""
		Args:
			db_params: dict with PostgreSQL connection params
			config_path: path to mapping config file (default: config.json)
		"""
		self.db_params = db_params
		self.config_path = config_path
		self.config = self.load_mapping_from_file()

	# --- FILE-BASED MAPPING ---

	def load_mapping_from_file(self) -> Dict[str, Any]:
		"""
		Load mapping config from a local JSON file.
		Returns: dict mapping config, or empty dict if not found/invalid.
		"""
		try:
			with open(self.config_path, 'r') as f:
				return json.load(f)
		except (FileNotFoundError, json.JSONDecodeError):
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
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute("SELECT config FROM mapping_config ORDER BY updated_at DESC LIMIT 1;")
		row = cur.fetchone()
		cur.close()
		conn.close()
		if row:
			return row[0]
		return {}


	def save_mapping_to_db(self, mapping: Dict[str, Any]):
		"""
		Save mapping config to the mapping_config table in the database.
		Args:
			mapping: dict to save
		"""
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute(
			"""
			INSERT INTO mapping_config (config, updated_at)
			VALUES (%s, NOW())
			""",
			(json.dumps(mapping),)
		)
		conn.commit()
		cur.close()
		conn.close()
		self.config = mapping

	# --- SCHEMA DISCOVERY (PostgreSQL) ---

	def list_tables(self) -> list:
		"""
		List all user tables in the public schema of PostgreSQL.
		Returns: list of table names
		"""
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute("""
			SELECT table_name FROM information_schema.tables
			WHERE table_schema = 'public';
		""")
		tables = [row[0] for row in cur.fetchall()]
		cur.close()
		conn.close()
		return tables


	def list_columns(self, table_name: str) -> list:
		"""
		List all columns and their types for a given table.
		Args:
			table_name: name of the table
		Returns: list of (column_name, data_type)
		"""
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute("""
			SELECT column_name, data_type FROM information_schema.columns
			WHERE table_name = %s;
		""", (table_name,))
		columns = cur.fetchall()
		cur.close()
		conn.close()
		return columns

	# --- SCHEMA DISCOVERY (Apache AGE Graph) ---

	def list_graph_labels(self, graph_name: str = 'production_graph') -> list:
		"""
		List all node labels in the given Apache AGE graph.
		Args:
			graph_name: name of the graph (default: production_graph)
		Returns: list of node labels
		"""
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute(f"""
			SELECT * FROM cypher('{graph_name}', $$
				MATCH (n) RETURN DISTINCT labels(n)
			$$) AS (labels agtype);
		""")
		labels = [row[0] for row in cur.fetchall()]
		cur.close()
		conn.close()
		return labels


	def list_graph_edge_types(self, graph_name: str = 'production_graph') -> list:
		"""
		List all edge types in the given Apache AGE graph.
		Args:
			graph_name: name of the graph (default: production_graph)
		Returns: list of edge types
		"""
		conn = psycopg2.connect(**self.db_params)
		cur = conn.cursor()
		cur.execute(f"""
			SELECT * FROM cypher('{graph_name}', $$
				MATCH ()-[r]->() RETURN DISTINCT type(r)
			$$) AS (type agtype);
		""")
		edge_types = [row[0] for row in cur.fetchall()]
		cur.close()
		conn.close()
		return edge_types

	# --- MAPPING ACCESS ---

	def get_mapping(self) -> Dict[str, Any]:
		"""
		Get the current mapping config (from file or last loaded from DB).
		Returns: dict mapping config
		"""
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
