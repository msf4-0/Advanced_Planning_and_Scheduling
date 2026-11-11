"""Shared domain enums.

Values match the existing database vocabulary and API payloads, so they can be
used at the boundary without translation. `StrEnum` members compare equal to
their string values and serialize as strings.
"""

from enum import StrEnum


class OperationStatus(StrEnum):
    DRAFT = "Draft"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class WorkOrderStatus(StrEnum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class RunStatus(StrEnum):
    QUEUED = "Queued"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class SolverStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    MODEL_INVALID = "MODEL_INVALID"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    OPTIMAL = "OPTIMAL"


class ResourceType(StrEnum):
    MACHINE = "Machine"
    HUMAN = "Human"
    TOOLING = "Tooling"
