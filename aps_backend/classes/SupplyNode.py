from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ProcessNode import ProcessNode

class SupplyNode:
    def __init__(self, materialId: str, name: str, quantityAvailable: float, available_date: int = 0):
        self.id: str = materialId
        self.name: str = name
        self.quantityAvailable: float = quantityAvailable
        self.available_date: int = available_date

        # Tracking references
        self.consumedBy: list[ProcessNode] = [] # list of ProcessNode that require this material

    def register_consumer(self, processNode: ProcessNode):
        if processNode not in self.consumedBy:
            self.consumedBy.append(processNode)

    def is_available_at(self, time_tick: int) -> bool:
        return time_tick >= self.available_date