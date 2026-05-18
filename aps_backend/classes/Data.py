import enum


class Operation:
    def __init__(self, name: str, duration: int, workstationType: str):
        self.name = name
        self.duration = duration
        self.workstationType = workstationType

    def get_duration(self) -> int:
        return self.duration

    def is_compatible_with(self, workstation: 'Workstation') -> bool:
        return self.workstationType == workstation.type

    def __str__(self) -> str:
        return f"{self.name} ({self.duration})"

class BOM:
    def __init__(self, itemName: str):
        self.itemName: str = itemName
        self.operations: list[Operation] = []
        self.children: list[BOM] = []

    def add_operation(self, operation: Operation):
        self.operations.append(operation)

    def add_child(self, child_bom: 'BOM'):
        self.children.append(child_bom)

    def get_operations(self) -> list[Operation]:
        ops = self.operations.copy()
        for child in self.children:
            ops.extend(child.get_operations())
        return ops

    def get_children(self) -> list['BOM']:
        children = self.children.copy()
        for child in self.children:
            children.extend(child.get_children())
        return children

    def total_duration(self) -> int:
        duration = sum(op.duration for op in self.operations)
        for child in self.children:
            duration += child.total_duration()
        return duration

    def flatten(self) -> list[Operation]:
        ops = self.operations.copy()
        for child in self.children:
            ops.extend(child.flatten())
        return ops

class WorkOrder:
    def __init__(self, id: str, bom: BOM, quantity: int = 1):
        self.id = id
        self.bom = bom
        self.quantity = quantity

        self.operation: list[Operation] = self.get_operations()
        self.dependencies: list[str] = []

        self.startTime: float = 0
        self.endTime: float = 0
        self.assignedWorkstation: str = ""

        self.status = WorkOrderStatus.PENDING

    def add_depedency(self, workOrderId: str):
        self.dependencies.append(workOrderId)

    def get_operations(self) -> list[Operation]:
        return self.bom.flatten()

    def total_duration(self) -> int:
        return self.bom.total_duration() * self.quantity

    def remaining_duration(self, current_time: float) -> int:
        if self.status == WorkOrderStatus.COMPLETED:
            return 0
        elif self.status == WorkOrderStatus.IN_PROGRESS:
            elapsed = current_time - self.startTime
            remaining = max(0, self.total_duration() - elapsed)
            return int(remaining)
        else:
            return self.total_duration()

    def is_ready(self, graph: 'WorkOrderGraph') -> bool:
        for dep_id in self.dependencies:
            dep_order = graph.get_work_order(dep_id)
            if not dep_order or dep_order.status != WorkOrderStatus.COMPLETED:
                return False
        return True

    def assign_schedule(self, start: float, end: float, workstationId: str):
        self.startTime = start
        self.endTime = end
        self.assignedWorkstation = workstationId
        self.status = WorkOrderStatus.SCHEDULED

class WorkOrderStatus(enum.Enum):
    PENDING = 1
    SCHEDULED = 2
    IN_PROGRESS = 3
    COMPLETED = 4

class Workstation:
    def __init__(self, id: str, type:str, capacity: int):
        self.id = id
        self.type = type
        self.capacity = capacity

class Dependency:
    def __init__(self, fromId: str, toId: str):
        self.fromId = fromId
        self.toId = toId

class WorkOrderGraph:
    def __init__(self):
        self.workOrders: dict[str, WorkOrder] = {}
        self.dependencies: list[Dependency] = []    