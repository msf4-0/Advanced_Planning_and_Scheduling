# Main entry point for running data extraction and scheduling (no API)
import sys
from repository import DBTable
from schema_mapper import SchemaMapper
from data_ingestion import DataIngestion
from scheduler.dataInput import SchedulerDataInput
from scheduler.modelBuilder import SchedulerModelBuilder
from scheduler.constraint import SchedulerConstraint
from scheduler.objective import SchedulerObjective
from scheduler.scheduler import Scheduler

lock = False

def main():
	# Database connection
	conn = DBTable().get_connection()

	# Initialize schema mapper and data ingestion
	mapper = SchemaMapper(conn)
	ingestion = DataIngestion(mapper)

	# Extract all data for the scheduler
	extracted = ingestion.extract_all()
	jobs = extracted.get('jobs', {})
	# You can add machines/materials extraction as needed

	# Prepare scheduler input
	data_input = SchedulerDataInput()
	for job_id, props in jobs.items():
		data_input.add_jobs(job_id, props)

	# Validate input
	if not data_input.validate_input():
		print("No jobs found or input invalid. Exiting.")
		raise ValueError("Invalid scheduler input data.")

	# Set up constraints and objectives (add more as needed)
	constraints = SchedulerConstraint()
	constraints.add_constraint(SchedulerConstraint.no_overlap_constraint)
	constraints.add_constraint(SchedulerConstraint.machine_downtime_constraint)
	constraints.add_constraint(SchedulerConstraint.precedence_constraint)
	
	if lock:
		constraints.add_constraint(SchedulerConstraint.lock_sequence_constraint)

	objective = SchedulerObjective()
	objective.add_objective(SchedulerObjective.minimize_makespan)
	objective.add_objective(SchedulerObjective.minimize_total_tardiness)
	objective.add_objective(SchedulerObjective.minimize_total_completion_time)

	# Build model and run scheduler
	model_builder = SchedulerModelBuilder(data_input, constraints, objective)
	scheduler = Scheduler(data_input, constraints, model_builder, objective)
	results = scheduler.solve()

	if results:
		print("Schedule Results:")
		for job, res in results.items():
			print(f"{job}: {res}")
	else:
		print("No feasible schedule found.")

if __name__ == "__main__":
	main()
