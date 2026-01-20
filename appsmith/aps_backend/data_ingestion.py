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
	def __init__(self, db_params, schema_mapper: SchemaMapper):
		self.db_params = db_params
		self.mapper = schema_mapper
		self.db = DBTable()
		self.graph = GraphEditor(self.db)

	def extract_jobs(self):
		"""
		Extract jobs from the mapped table/columns in PostgreSQL using DBTable.
		Returns: dict of jobs for SchedulerDataInput
		"""
		mapping = self.mapper.get_job_mapping()
		if not mapping:
			return {}
		table = mapping.get('table')
		fields = mapping.get('fields', {})
		id_col = mapping.get('id_col')
		# Fetch all rows using DBTable
		
		if not table or not id_col:
			return {}
		
		if not isinstance(fields, dict) or not fields:
			return {}
        
		rows = self.db.fetch(table)
		jobs = {}
		for props in rows:
			job_id = props.get(id_col)
			job_props = {}
			for key, col in fields.items():
				job_props[key] = props.get(col)
			jobs[job_id] = job_props
		return jobs

	def extract_graph_jobs(self, graph_name: str = 'production_graph'):
		"""
		Extract jobs from graph nodes in Apache AGE using GraphEditor.
		Returns: dict of jobs for SchedulerDataInput
		"""
		mapping = self.mapper.get_job_mapping()
		if not mapping:
			return {}
		job_label = mapping.get('graph_label')
		fields = mapping.get('fields')
		id_prop = mapping.get('id_prop')

		# All must be present and valid
		if not job_label or not isinstance(fields, dict) or not fields or not id_prop:
			return {}

		nodes = self.graph.get_node(label=job_label, filters={})
		jobs = {}
		for node in nodes:
			job_id = node.get(id_prop)
			job_props = {}
			for key, prop in fields.items():
				job_props[key] = node.get(prop)
			jobs[job_id] = job_props
		return jobs

	def extract_all(self):
		"""
		Extract all mapped entities (jobs, machines, materials, etc.)
		Returns: dict with all entities for scheduler
		"""
		jobs = self.extract_jobs()
		# You can add extract_machines(), extract_materials(), etc. similarly
		return {
			'jobs': jobs,
			# 'machines': self.extract_machines(),
			# 'materials': self.extract_materials(),
		}

# Example usage:
# db_params = {...}
# mapper = SchemaMapper(db_params)
# ingestion = DataIngestion(db_params, mapper)
# jobs = ingestion.extract_jobs()
