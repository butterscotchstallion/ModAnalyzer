import os

from TreasureTableVerifier import TreasureTableParser, TreasureTableReader


def test_parse_file():
    parser = TreasureTableParser()
    reader = TreasureTableReader()
    tt_lines = reader.read_from_file("tests/fixture/TreasureTable.txt")

    assert len(tt_lines) > 0, "Failed to read from file"

    tt_map = parser.parse_treasure_table(tt_lines)

    assert tt_map is not None, "Failed to parse treasure table"
    assert len(tt_map) > 0, "Empty treasure table"
    assert len(tt_map.keys()) == 29

    entry_map = {
        "CHA_Exterior_Bandit_Leader": [
            "I_OBJ_RUNE_ROF_BONE_ARMOR",
            "I_OBJ_RUNE_OF_SLIMY_COMPANIONSHIP",
            "I_OBJ_RUNE_ROF_OF_RUNIC_INVIGORATION",
        ],
        "_Valuables_Generic": [
            "I_OBJ_RUNE_ROF_BONE_ARMOR",
            "I_OBJ_RUNE_OF_SLIMY_COMPANIONSHIP",
            "I_OBJ_RUNE_ROF_UNSUMMONING",
            "I_OBJ_RUNE_ROF_OF_RUNIC_INVIGORATION",
            "I_OBJ_RUNE_ROF_TEMPORARY_AMNESIA",
        ],
        "OBJ_ROF_RUNE_POUCH_TT": [
            "I_OBJ_SCARRED_RUNE",
            "I_OBJ_CRUSHING_FLIGHT_RUNE",
            "I_OBJ_BLOODSTAINED_RUNE",
            "I_OBJ_RUNE_ROF_MUMMIFICATION",
            "I_OBJ_RUNE_OF_SLIMY_COMPANIONSHIP",
            "I_OBJ_HARNESSED_WEAVE_RUNE",
            "I_OBJ_RUNE_ROF_BONE_ARMOR",
            "I_OBJ_RUNE_ROF_TEMPORARY_AMNESIA",
            "I_OBJ_RUNE_ROF_OF_EMBIGGENING",
            "I_OBJ_RUNE_ROF_OF_GR",
            "I_ROF_Duplicitous_Bow",
            "I_OBJ_RUNE_ROF_UNSUMMONING",
            "I_OBJ_RUNE_ROF_OF_RUNIC_INVIGORATION",
        ],
        "WYR_Circus_KoboldMerchant_Magic": [
            "I_OBJ_BLOODSTAINED_RUNE",
            "I_OBJ_RUNE_ROF_MUMMIFICATION",
            "I_ROF_Duplicitous_Bow",
            "I_OBJ_RUNE_ROF_OF_RUNIC_INVIGORATION",
            "I_OBJ_RUNE_ROF_OF_GR",
        ],
        "MOO_WallTentacleOgress_Treasure": [
            "I_OBJ_BLOODSTAINED_RUNE",
            "I_OBJ_RUNE_ROF_MUMMIFICATION",
            "I_OBJ_RUNE_ROF_TEMPORARY_AMNESIA",
        ],
    }

    # Summary
    print(os.linesep)

    for tt in tt_map:
        tt_entry_len = len(tt_map[tt])
        if tt in entry_map:
            assert tt_entry_len == len(entry_map[tt]), f"Entries mismatch: {tt}"

        print(f"{tt}: {tt_entry_len} entries")

    summary = parser.get_summary_from_tt_map(tt_map)

    assert summary, "Failed to get treasure table summary"

    print(os.linesep)

    for obj_category_name in summary:
        print(f"{obj_category_name} is in {len(summary[obj_category_name])} tables")
