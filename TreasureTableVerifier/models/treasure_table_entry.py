from dataclasses import dataclass


@dataclass
class TreasureTableEntry:
    # I think this is row/column but I don't care about this right now
    subtable_position: str
    object_category_name: str
