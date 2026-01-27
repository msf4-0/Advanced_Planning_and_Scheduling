"""
data_ingestion.py: Extracts and transforms data from PostgreSQL/Apache AGE for scheduler input.

Features:
- Uses SchemaMapper for dynamic mapping
- Extracts jobs, machines, materials, etc. from DB/graph
- Transforms data into scheduler-friendly format
"""

from schema_mapper import SchemaMapper
from repository import DBTable, GraphEditor


class DataIngestion:
	def __init__(self, schema_mapper: SchemaMapper):
		self.mapper = schema_mapper
		self.db = DBTable()
		self.graph = GraphEditor(self.db)
		# Extract job fields mapping for dynamic property access
		mapping = self.mapper.get_job_mapping() or {}
		self.job_fields = mapping.get('fields', {})

	def extract_jobs(self):
		"""
		Extract jobs from the mapped table/columns in PostgreSQL using DBTable.
		Returns: dict of jobs for SchedulerDataInput
		Uses dynamic job_fields for consistency with config.json and configs.py.
		Steps:
		1. Get job mapping from SchemaMapper (contains table/column info).
		2. Validate mapping and required fields.
		3. Fetch all rows from the mapped table.
		4. For each row, build a job dict using internal keys mapped to DB columns.
		5. Return a dict of jobs keyed by job_id.
		"""
		mapping = self.mapper.get_job_mapping()  # Get job mapping config (table/column info)
		if not mapping:
			return {}  # No mapping found, return empty
		table = mapping.get('table_name')	# Table name in DB
		fields = self.job_fields	# Internal-to-DB column mapping
		id_col = mapping.get('column_id')	# Primary key column name
		if not table or not id_col:
			return {}  # Required info missing
		if not isinstance(fields, dict) or not fields:
			return {}  # No field mapping found
		rows = self.db.fetch(table)  # Fetch all rows from the table
		jobs = {}
		for props in rows:
			job_id = props.get(id_col)  # Get the job's unique ID from the row

			# Build a dict of job properties using internal keys mapped to DB columns
			job_props = {key: props.get(col) for key, col in fields.items()}
			jobs[job_id] = job_props  # Add to jobs dict
			
		return jobs  # Return all jobs as a dict

	def extract_graph_jobs(self, graph_name: str = 'production_graph'):
		"""
		Extract jobs from graph nodes in Apache AGE using GraphEditor.
		Returns: dict of jobs for SchedulerDataInput
		Uses dynamic job_fields for consistency with config.json and configs.py.
		Steps:
		1. Get job mapping from SchemaMapper (contains graph label/property info).
		2. Validate mapping and required fields.
		3. Fetch all nodes with the mapped label from the graph.
		4. For each node, build a job dict using internal keys mapped to node properties.
		5. Return a dict of jobs keyed by job_id.
		"""
		mapping = self.mapper.get_job_mapping()  # Get job mapping config (graph label/property info)
		if not mapping:
			return {}  # No mapping found, return empty
		job_label = mapping.get('graph_label')  # Node label in the graph
		fields = self.job_fields                # Internal-to-graph property mapping
		id_prop = mapping.get('id_property')    # Unique property name for node ID
		if not job_label or not isinstance(fields, dict) or not fields or not id_prop:
			return {}  # Required info missing
		
		nodes = self.graph.get_node(label=job_label, filters={})  # Fetch all nodes with the label
		jobs = {}
		for node in nodes:
			job_id = node.get(id_prop)  # Get the job's unique ID from the node
			# Build a dict of job properties using internal keys mapped to node properties
			job_props = {key: node.get(prop) for key, prop in fields.items()}
			jobs[job_id] = job_props  # Add to jobs dict
		return jobs  # Return all jobs as a dict

	def extract_all(self):
		"""
		Extract all mapped entities (jobs, machines, materials, etc.)
		Returns: dict with all entities for scheduler
		Uses only internal keys from config.json for consistency.
		"""
		jobs = self.extract_jobs()
		# jobs = self.extract_graph_jobs()
		# You can add extract_machines(), extract_materials(), etc. using the same pattern:
		# - Use mapping.get('fields') for internal keys
		# - Build dicts with those keys for consistency
		return {
			'jobs': jobs,
			# 'machines': self.extract_machines(),
			# 'materials': self.extract_materials(),
		}

# Example usage:
# mapper = SchemaMapper(db.get_connection())
# ingestion = DataIngestion(mapper)
# jobs = ingestion.extract_graph_jobs()