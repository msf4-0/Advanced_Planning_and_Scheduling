from ortools.sat.python import cp_model

class Scheduler:
    """
    Main Scheduler class that integrates data input, constraints, model building, and objectives
    to solve manufacturing scheduling problems using OR-Tools CP-SAT.
    """

    def __init__(self, data_input, constraints, model_builder, objective=None):
        """
        :param data_input: SchedulerDataInput instance
        :param constraints: SchedulerConstraint instance
        :param model_builder: SchedulerModelBuilder instance
        :param objective: SchedulerObjective instance (optional)
        """
        self.data_input = data_input
        self.constraints = constraints
        self.model_builder = model_builder
        self.objective = objective

    def solve(self, solver_params=None):
        """
        Build and solve the scheduling model.
        :param solver_params: Optional dictionary of solver parameters
        :return: Dictionary of job results if feasible/optimal, else None
        """
        model, job_vars = self.model_builder.build_model()
        solver = cp_model.CpSolver()

        # Set optional solver parameters
        if solver_params:
            for param, value in solver_params.items():
                setattr(solver.parameters, param, value)

        status = solver.Solve(model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            # Store results in data_input.values
            for job_name, vars in job_vars.items():
                result = {}
                for var_name, var in vars.items():
                    if isinstance(var, cp_model.IntVar):
                        result[var_name] = solver.Value(var)
                self.data_input.store_result(job_name, result)
            return self.data_input.values
        else:
            return None