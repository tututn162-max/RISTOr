from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TechniqueRecord:
    machine_data: dict
    human_text: str
    status: str
    attempts_history: list


class InMemoryStore:
    def __init__(self) -> None:
        self.by_hash: Dict[str, TechniqueRecord] = {}
        self.name_index: Dict[str, str] = {}  # name -> machine_data_hash

    def get_by_hash(self, machine_data_hash: str) -> Optional[TechniqueRecord]:
        return self.by_hash.get(machine_data_hash)

    def save(self, record: TechniqueRecord) -> None:
        self.by_hash[record.machine_data["machine_data_hash"]] = record
        self.name_index[record.machine_data["name"]] = record.machine_data["machine_data_hash"]

    def is_name_unique(self, name: str) -> bool:
        return name not in self.name_index

    def update_index_on_rename(self, old_name: str, new_name: str, new_hash: str) -> None:
        if old_name in self.name_index:
            del self.name_index[old_name]
        self.name_index[new_name] = new_hash

store = InMemoryStore()