from dataclasses import dataclass

from TreasureTableVerifier.models.treasure_table_entry import TreasureTableEntry


@dataclass
class TreasureTable:
    can_merge: bool
    entries: list[TreasureTableEntry]
