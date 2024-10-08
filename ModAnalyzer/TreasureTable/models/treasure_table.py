import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TypedDict

from ModAnalyzer.TreasureTable.models.treasure_table_entry import TreasureTableEntry


@dataclass
class TreasureTable:
    name: str
    can_merge: bool
    entries: list[TreasureTableEntry]

    def __str__(self):
        return f"{self.name} ({len(self.entries)} entries)"

    def __lt__(self, other):
        return len(self.entries) < len(other.entries)


ItemSummary = TypedDict(
    "ItemSummary", {"verified": list[ET.Element], "ignored": list[ET.Element]}
)
