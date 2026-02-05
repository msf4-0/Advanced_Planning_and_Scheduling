"""
data_ingestion.py: Extracts and transforms data from PostgreSQL/Apache AGE for scheduler input.

Features:
- Uses SchemaMapper for dynamic mapping
- Extracts jobs, machines, materials, etc. from DB/graph
- Transforms data into scheduler-friendly format
"""

from schema_mapper import SchemaMapper
from repository import DBTable, GraphEditor
import logging


class DataIngestion:
	def __init__(self, schema_mapper: SchemaMapper):
		self.mapper = schema_mapper
		self.db = DBTable()
		self.graph = GraphEditor(self.db)
		# Extract job fields mapping for dynamic property access
		mapping = self.mapper.get_job_mapping() or {}
		# logging.info(f"Job mapping for DataIngestion: {mapping}")
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
		logging.info(f"Job mapping: {mapping}")
		if not mapping:
			return {}  # No mapping found, return empty
		
		table = mapping.get('table_name')	# Table name in DB
		fields = self.job_fields	# Internal-to-DB column mapping
		id_col = mapping.get('column_id')	# Primary key column name
		
		logging.info(f"Extracting jobs from table: {table}, id_col: {id_col}, fields: {fields}")

		if not table or not id_col:
			return {}  # Required info missing
		
		if not isinstance(fields, dict) or not fields:
			return {}  # No field mapping found
		
		rows = self.db.fetch(table)  # Fetch all rows from the table
		jobs = {}
		# First pass: collect all job IDs (case-insensitive map)
		job_id_map = {}
		for props in rows:
			job_id = props.get(id_col)
			if job_id:
				job_id_map[job_id.lower()] = job_id

		for props in rows:
			job_id = props.get(id_col)  # Get the job's unique ID from the row
			logging.info(f"Extracting job {job_id} with properties {props}")

			# Build a dict of job properties using internal keys mapped to DB columns
			job_props = {key: props.get(col) for key, col in fields.items()}
			machine_type_id = props.get('required_machine_type_id')
			if machine_type_id is not None:
				allowed = self.db.fetch(
					'machines',
					{'machine_type_id': machine_type_id},
				)
				job_props['allowed_machines'] = [m.get('machine_id') for m in allowed]
			else:
				job_props['allowed_machines'] = []

			# Auto-assign the first allowed machine if available
			if job_props['allowed_machines']:
				job_props['machine'] = job_props['allowed_machines'][0]
			else:
				job_props['machine'] = None

			# Normalize predecessor field (if present)
			predecessor = job_props.get('predecessor')
			if predecessor:
				# Try to match case-insensitively to a job ID
				pred_key = predecessor.lower()
				if pred_key in job_id_map:
					job_props['predecessor'] = job_id_map[pred_key]
				else:
					logging.warning(f"Job {job_id} predecessor '{predecessor}' does not match any job ID; removing predecessor.")
					job_props['predecessor'] = None

			jobs[job_id] = job_props  # Add to jobs dict

		return jobs  # Return all jobs as a dict

	def extract_graph_jobs(self, graph_name: str = 'production_graph'):
		"""
		Extract jobs from graph nodes in Apache AGE using GraphEditor, including edge traversal.
		Returns: dict of jobs for SchedulerDataInput
		For each job node, also extract outgoing edges (e.g., precedence, allowed machines).
		"""
		mapping = self.mapper.get_job_mapping()  # Get job mapping config (graph label/property info)
		if not mapping:
			logging.info("No job mapping found.")
			return {}  # No mapping found, return empty
		job_label = mapping.get('graph_label') # Node label in the graph
		fields = self.job_fields # Internal-to-graph property mapping
		id_prop = mapping.get('id_property')    # Unique property name for node ID

		logging.info(f"Extracting graph jobs with label: {job_label}, id_prop: {id_prop}, fields: {fields}")

		if not job_label or not isinstance(fields, dict) or not fields or not id_prop:
			return {}  # Required info missing

		nodes = self.graph.get_node(label=job_label, filters={})  # Fetch all nodes with the label
		jobs = {}
		logging.info(f"Found {len(nodes)} job nodes in graph.")
		logging.info(f"1 Job node: {nodes[0] if nodes else 'N/A'}")
		for node in nodes:
			job_id = node.get(id_prop)  # Get the job's unique ID from the node
			# Build a dict of job properties using internal keys mapped to node properties
			job_props = {key: node.get(prop) for key, prop in fields.items()}

			if not job_id:
				logging.warning(f"Job node missing id property '{id_prop}': {node}")
				continue  # Skip nodes without valid ID

			# --- EDGE TRAVERSAL ---
			# 1. Find predecessor jobs (edges: Job)-[:PRECEDES]->(Job)
			predecessors = self.graph.get_related_nodes(
				node_id=(id_prop, job_id),
				source_label=job_label,
				edge_type='PRECEDES',
				direction='in',
				graph_name=graph_name
			)
			if predecessors:
				job_props['predecessors'] = [pred.get(id_prop) for pred in predecessors]
			else:
				job_props['predecessors'] = []

			# 2. Find allowed machines (edges: Job)-[:ALLOWED_ON]->(Machine)
			allowed_machines = self.graph.get_related_nodes(
				node_id=(id_prop, job_id),
				source_label=job_label,
				edge_type='ALLOWED_ON',
				direction='out',
				graph_name=graph_name
			)
			if allowed_machines:
				job_props['allowed_machines'] = [m.get('machine_id') for m in allowed_machines]
			else:
				job_props['allowed_machines'] = []

			# 3. Find assigned machine (edges: Job)-[:ASSIGNED_TO]->(Machine)
			assigned_machine = self.graph.get_related_nodes(
				node_id=(id_prop, job_id),
				source_label=job_label,
				edge_type='ASSIGNED_TO',
				direction='out',
				graph_name=graph_name
			)
			if assigned_machine:
				job_props['assigned_machine'] = assigned_machine[0].get('machine_id')
			else:
				job_props['assigned_machine'] = None

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