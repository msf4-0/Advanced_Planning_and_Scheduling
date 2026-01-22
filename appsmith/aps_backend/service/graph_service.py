# graph_service.py: Service to build and manage the production graph for scheduling

from schema_mapper import SchemaMapper
from repository import DBTable, GraphEditor
from typing import Optional, Any

class GraphService:
	"""
	Service to build and manage the production graph in Apache AGE from SQL data.
	Provides methods to construct the graph and extract it for the scheduler.
	"""
	def __init__(self, schema_mapper: SchemaMapper):
		self.mapper = schema_mapper
		self.db = DBTable()
		self.graph = GraphEditor(self.db)

	def build_graph_from_sql(self, graph_name: str = 'production_graph') -> None:
		"""
		Build the graph in Apache AGE from SQL tables using the mapping config.
		This will create nodes and edges as defined in the mapping.
		"""
		mapping = self.mapper.get_mapping()

		# Example: Build job nodes
		job_map = mapping.get('job_mapping', {})
		if job_map.get('source') == 'sql':
			table = job_map.get('table')
			id_col = job_map.get('id_col')
			fields = job_map.get('fields')
			label = job_map.get('graph_label', 'Job')
			if table and id_col and fields:
				rows = self.db.fetch(table)
				for row in rows:
					props = {k: row.get(v) for k, v in fields.items()}
					props[id_col] = row.get(id_col)
					self.graph.create_node(label=label, properties=props)

		# Example: Build machine nodes
		machine_map = mapping.get('machine_mapping', {})
		if machine_map.get('source') == 'sql':
			table = machine_map.get('table')
			id_col = machine_map.get('id_col')
			type_col = machine_map.get('type_col')
			capacity_col = machine_map.get('capacity_col')
			label = machine_map.get('graph_label', 'Machine')
			if table and id_col:
				rows = self.db.fetch(table)
				for row in rows:
					props = {
						'machine_id': row.get(id_col),
						'type': row.get(type_col) if type_col else None,
						'capacity': row.get(capacity_col) if capacity_col else None
					}
					props = {k: v for k, v in props.items() if v is not None}
					self.graph.create_node(label=label, properties=props)

		# Example: Build material nodes
		material_map = mapping.get('material_mapping', {})
		if material_map.get('source') == 'sql':
			table = material_map.get('table')
			id_col = material_map.get('id_col')
			name_col = material_map.get('name_col')
			label = material_map.get('graph_label', 'Material')
			if table and id_col:
				rows = self.db.fetch(table)
				for row in rows:
					props = {
						'material_id': row.get(id_col),
						'material_name': row.get(name_col) if name_col else None
					}
					props = {k: v for k, v in props.items() if v is not None}
					self.graph.create_node(label=label, properties=props)

		# Example: Build edges (user can extend this for their schema)
		# For example, connect jobs to machines or materials if mapping is defined
		# This is left as a template for user extension

	def clear_graph(self, graph_name: str = 'production_graph') -> None:
		"""
		Remove all nodes and edges from the graph (dangerous!).
		"""
		# This will delete all nodes and edges in the graph
		# Use with caution!
		cypher = f"""
		SELECT * FROM cypher('{graph_name}', $$
			MATCH (n) DETACH DELETE n
		$$) AS (count agtype);
		"""
		conn = self.db.get_connection()
		cur = conn.cursor()
		try:
			cur.execute(cypher)
			conn.commit()
		finally:
			cur.close()
			conn.close()

	def extract_graph_for_scheduler(self, graph_name: str = 'production_graph') -> dict:
		"""
		Extract the graph as a dict suitable for SchedulerDataInput.
		Returns: dict with jobs, machines, materials, etc.
		"""
		# Example: extract jobs from graph
		job_map = self.mapper.get_mapping().get('job_mapping', {})
		job_label = job_map.get('graph_label', 'Job')
		id_prop = job_map.get('id_prop', 'id')
		fields = job_map.get('fields', {})
		jobs = {}
		nodes = self.graph.get_node(label=job_label, filters={})
		for node in nodes:
			job_id = node.get(id_prop)
			job_props = {k: node.get(v) for k, v in fields.items()}
			jobs[job_id] = job_props

		# Example: extract machines
		machine_map = self.mapper.get_mapping().get('machine_mapping', {})
		machine_label = machine_map.get('graph_label', 'Machine')
		machine_id_prop = machine_map.get('id_prop', 'machine_id')
		machine_fields = machine_map.get('fields', {})
		machines = {}
		nodes = self.graph.get_node(label=machine_label, filters={})
		for node in nodes:
			mid = node.get(machine_id_prop)
			mprops = {k: node.get(v) for k, v in machine_fields.items()}
			machines[mid] = mprops

		# Example: extract materials
		material_map = self.mapper.get_mapping().get('material_mapping', {})
		material_label = material_map.get('graph_label', 'Material')
		material_id_prop = material_map.get('id_prop', 'material_id')
		material_fields = material_map.get('fields', {})
		materials = {}
		nodes = self.graph.get_node(label=material_label, filters={})
		for node in nodes:
			matid = node.get(material_id_prop)
			matprops = {k: node.get(v) for k, v in material_fields.items()}
			materials[matid] = matprops

		return {
			'jobs': jobs,
			'machines': machines,
			'materials': materials
		}
