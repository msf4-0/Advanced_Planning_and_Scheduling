
class ConstraintBase:
    """
    Base class for all constraints. Each constraint should define required_fields.
    """
    required_fields = []  # List of internal field names needed by this constraint

    @classmethod
    def get_required_fields(cls):
        return cls.required_fields


class ObjectiveBase:
    """
    Base class for all objectives. Each objective should define required_fields if needed.
    """
    required_fields = []

    @classmethod
    def get_required_fields(cls):
        return cls.required_fields


class BaseConfigs:
    """
    Abstract base class for scheduling configuration classes.
    Provides interface and shared logic for constraint/objective registration and mapping.
    """

    def __init__(self, constraintClass, objectiveClass, mapping: dict):
        """
        Initialize with constraint/objective classes and mapping config.
        """
        self.constraintClass = constraintClass
        self.objectiveClass = objectiveClass
        self.mapping = mapping

        # Extract job fields mapping for dynamic property access
        self.job_fields = self.mapping.get('job_mapping', {}).get('fields', {})

    @staticmethod
    def collect_required_fields(constraint_classes, objective_classes):
        """
        Collect all required fields from the given constraint and objective classes.
        Returns a set of all unique required field names.
        """
        fields = set()
        for cls in constraint_classes:
            fields.update(cls.get_required_fields())
        for cls in objective_classes:
            fields.update(cls.get_required_fields())
        return fields

    def register_default_constraints(self):
        """
        Register built-in constraints. To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement register_default_constraints.")

    def register_default_objectives(self):
        """
        Register built-in objectives. To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement register_default_objectives.")