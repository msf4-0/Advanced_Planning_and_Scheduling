


class SchedulerDataInput:
    """
    Class to handle input data for the scheduler.
    Data can include jobs, parameters, and other relevant information
    """
    
    def __init__(self) -> None:
        """
        Initialize the SchedulerDataInput with empty data structures.

        self.jobs: dict - holds job names as keys, and for each job, a dictionary of properties such as duration, allowed machines, domain, etc.
            Example: {'jobA': {'duration': 5, 'machines': [1,2,3], 'domain': (0, 10)}, ...}

        self.values: dict - holds job names as keys and their assigned/solved values (e.g., scheduled start time, assigned machine, etc.).
            Example: {'jobA': {'start_time': 3, 'machine': 2}, ...}
        """
        self.jobs = {}
        self.values = {}

    def add_jobs(self, name: str, properties: dict) -> None:
        """
        Add a job to the scheduler input.

        :param properties: Dictionary of properties for the job.
        :param name: Name of the job.
        """
        self.jobs[name] = properties

    def store_result(self, name: str, results: dict) -> None:
        """
        Store the results for a specific job.
        
        :param name: Name of the job.
        :type name: str
        :param results: Results dictionary for the job.
        :type results: dict
        """
        self.values[name] = results

    def get_job_properties(self, name: str) -> dict:
        """
        Retrieve the properties of a specific job.

        :param name: Name of the job.
        :return: Dictionary of job properties.
        """
        return self.jobs.get(name, {})
    
    def get_value(self, name: str) -> dict:
        """
        Retrieve the value of a specific variable.

        :param name: Name of the variable.
        :return: Value of the variable.
        """
        return self.values.get(name, {})
    
    def validate_input(self) -> bool:
        """
        Validate the scheduler input data.

        :return: True if the input data is valid, False otherwise.
        """
        # Basic validation: check if jobs are defined
        if not self.jobs:
            return False
        
        # Further validation can be added as needed
        return True