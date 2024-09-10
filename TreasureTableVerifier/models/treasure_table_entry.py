from dataclasses import dataclass


@dataclass
class TreasureTableEntry:
    """
    TreasureTableEntry

    // A comment looks like this //
    new treasuretable "CHA_Exterior_Bandit_Leader"
    CanMerge 1
    new subtable "1,1"
    object category "I_OBJ_RUNE_ROF_BONE_ARMOR",1,0,0,0,0,0,0,0
    """

    can_merge: bool
    # I think this is row/column but I don't care about this right now
    subtable_position: str
    object_category_name: str

    def __eq__(self, other):
        return self.object_category_name == other.object_category_name
