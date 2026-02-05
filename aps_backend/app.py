# Main entry point for running data extraction and scheduling (no API)
import logging
import sys
from repository import DBTable
from schema_mapper import SchemaMapper
from data_ingestion import DataIngestion
from scheduler import SchedulerDataInput, SchedulerModelBuilder, SchedulerConstraint, SchedulerObjective, Scheduler
from configs import Configs

mock_data = {
	'jobs': {
		'jobA': {
			'duration': 5,
			'allowed_machines': [1, 2],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
		'jobB': {
			'duration': 7,
			'allowed_machines': [2],
			'domain': (0, 25),
			'predecessor': 'jobA',
			'due_date': 20,
			'qty_ordered': 120,
			'qty_initialized': 110,
			'locked': False
		},
		'jobC': {
			'duration': 4,
			'allowed_machines': [1],
			'domain': (0, 18),
			'predecessor': None,
			'due_date': 10,
			'qty_ordered': 80,
			'qty_initialized': 80,
			'locked': True,
			'locked_start': 2,
			'locked_machine': 1
		},
		'jobD': {
			'duration': 10,
			'allowed_machines': [2, 3],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
		'jobE': {
			'duration': 15,
			'allowed_machines': [3],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
	},
	'machines': {
		1: {
			'type': 'CNC',
			'capacity': 2
		},
		2: {
			'type': 'Lathe',
			'capacity': 1
		},
		3: {
			'type': 'Milling',
			'capacity': 1
		}
	},
	'materials': {
		'matA': {
			'material_name': 'Steel'
		},
		'matB': {
			'material_name': 'Aluminum'
		}
	}
}

logging.basicConfig(level=logging.INFO)

def main():
	# Database connection
	# conn = DBTable().get_connection_graph()
	conn = DBTable().get_connection()
	logging.info("Database connection established.")

	# Initialize schema mapper and data ingestion
	mapper = SchemaMapper(conn)
	# logging.info(f"(APP) Current mapping config: {mapper.get_mapping()}")
	ingestion = DataIngestion(mapper)


	# Extract all data for the scheduler
	extracted = ingestion.extract_all()
	logging.info(f"Extracted data: {extracted}")

	jobs = extracted.get('jobs', {})
	logging.info(f"Extracted jobs: {jobs}")

	# jobs = mock_data['jobs']
	# You can add machines/materials extraction as needed

	# Prepare scheduler input
	data_input = SchedulerDataInput()
	for job_id, props in jobs.items():
		logging.info(f"Adding job {job_id} with props {props}")
		data_input.add_jobs(job_id, props)

	# Validate input
	if not data_input.validate_input():
		raise ValueError("(app.py) Invalid scheduler input data.")

	# Set up constraints and objectives (add more as needed)
	constraints = SchedulerConstraint()
	objective = SchedulerObjective()

	# Configs(constraints, objective, mapper.get_mapping())  # Register built-in constraints and objectives
	# You can pass a static mapping or mock config if needed
	Configs(constraints, objective, {})  # Register built-in constraints and objectives

	# Build model and run scheduler
	model_builder = SchedulerModelBuilder(data_input, constraints, objective)
	scheduler = Scheduler(data_input, constraints, model_builder, objective)
	results = scheduler.solve()

	if results:
		return results
	else:
		raise ValueError("No feasible schedule found.")

if __name__ == "__main__":
	output = main()
	if output is not None:
		print(output)
	else:
		print("No feasible schedule found.")
