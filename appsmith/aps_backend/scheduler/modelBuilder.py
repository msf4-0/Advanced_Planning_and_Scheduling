from ortools.sat.python import cp_model

class SchedulerModelBuilder:
    """
    Builds an OR-Tools CpModel using SchedulerDataInput, SchedulerConstraint, and SchedulerObjective.
    """

    def __init__(self, data_input, constraints, objective=None):
        """
        :param data_input: SchedulerDataInput instance
        :param constraints: SchedulerConstraint instance
        :param objective: SchedulerObjective instance (optional)
        """
        self.data_input = data_input
        self.constraints = constraints
        self.objective = objective

    def build_model(self):
        """
        Build and return the OR-Tools CpModel and job variables.
        """
        model = cp_model.CpModel()
        
        # Create job variables
        job_vars = self.create_job_vars_default(model, self.data_input.jobs) # Default method; users can comment this and use their own below

        # Apply constraints
        self.constraints.apply_constraints(model, job_vars, self.data_input.jobs)

        # Apply objective if provided
        if self.objective:
            self.objective.apply_objectives(model, job_vars, self.data_input.jobs)

        return model, job_vars
    

    # Built-in job variable creation
    @staticmethod
    def create_job_vars_default(model, jobs):
        job_vars = {}

        # Create variables for each job
        for job_name, props in jobs.jobs.items():
            duration = props.get('duration', 1)
            domain = props.get('domain', (0, 1000))
            start = model.NewIntVar(domain[0], domain[1], f"{job_name}_start")
            end = model.NewIntVar(domain[0], domain[1], f"{job_name}_end")
            interval = model.NewIntervalVar(start, duration, end, f"{job_name}_interval")
            job_vars[job_name] = {
                'start': start,
                'end': end,
                'interval': interval,
                'duration': duration
            }

        return job_vars
    
    # Users can add more job variable creation methods here
    # and call them in build_model by replacing create_job_vars_default

    '''
    Example of a custom job variable creation method:
    @staticmethod
    def create_job_vars_custom(model, jobs):
        job_vars = {}
        # Custom logic to create job variables
        return job_vars
    '''