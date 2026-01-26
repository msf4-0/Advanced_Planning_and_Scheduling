from enum import Enum

class EdgeType(Enum):
    """
    Enum for different types of edges in the graph database.

    Attributes:
        HAS_STEP (str): Edge type representing that a product has a step.
        USES_STEP (str): Edge type representing that a product route uses a step.
        NEXT_OPERATION (str): Edge type representing the sequence of operations.
        HAS_ROUTE_STEP (str): Edge type representing that a route has a step.
        DOES (str): Edge type representing that an operation does something.
        CAN_RUN_ON (str): Edge type representing that an operation can run on a machine.
        USES_MATERIAL (str): Edge type representing that an operation uses a material.
        BLOCKED_BY (str): Edge type representing that an operation is blocked by another operation.
    """
    HAS_STEP = "HAS_STEP"
    USES_STEP = "USES_STEP"
    NEXT_OPERATION = "NEXT_OPERATION"
    HAS_ROUTE_STEP = "HAS_ROUTE_STEP"
    DOES = "DOES"
    CAN_RUN_ON = "CAN_RUN_ON"
    USES_MATERIAL = "USES_MATERIAL"
    BLOCKED_BY = "BLOCKED_BY"


# Constraint node enums
class ConstraintType(Enum):
    MACHINE_BROKEN = "machine_broken"
    MATERIAL_SHORTAGE = "material_shortage"
    CUSTOM_RULE = "custom_rule"
    MAINTENANCE = "maintenance"
    QUALITY_HOLD = "quality_hold"

class ConstraintStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESOLVED = "resolved"

class ConstraintSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

