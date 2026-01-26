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
		"""
		mapping = self.mapper.get_job_mapping()
		if not mapping:
			return {}
		table = mapping.get('table')
		fields = self.job_fields
		id_col = mapping.get('id_col')
		if not table or not id_col:
			return {}
		if not isinstance(fields, dict) or not fields:
			return {}
		rows = self.db.fetch(table)
		jobs = {}
		for props in rows:
			job_id = props.get(id_col)
			job_props = {key: props.get(col) for key, col in fields.items()}
			jobs[job_id] = job_props
		return jobs

	def extract_graph_jobs(self, graph_name: str = 'production_graph'):
		"""
		Extract jobs from graph nodes in Apache AGE using GraphEditor.
		Returns: dict of jobs for SchedulerDataInput
		Uses dynamic job_fields for consistency with config.json and configs.py.
		"""
		mapping = self.mapper.get_job_mapping()
		if not mapping:
			return {}
		job_label = mapping.get('graph_label')
		fields = self.job_fields
		id_prop = mapping.get('id_prop')
		if not job_label or not isinstance(fields, dict) or not fields or not id_prop:
			return {}
		nodes = self.graph.get_node(label=job_label, filters={})
		jobs = {}
		for node in nodes:
			job_id = node.get(id_prop)
			job_props = {key: node.get(prop) for key, prop in fields.items()}
			jobs[job_id] = job_props
		return jobs

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