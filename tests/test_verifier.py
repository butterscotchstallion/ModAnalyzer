import logging

import pytest

from ModAnalyzer.TreasureTable import TreasureTableParser, TreasureTableReader
from ModAnalyzer.TreasureTable.models import TreasureTableEntry
from tests.conftest import FIXTURE_PATHS

parser = TreasureTableParser()
reader = TreasureTableReader()
logger = logging.getLogger(__name__)


def get_tt_map(file_path: str):
    tt_lines = reader.read_from_file(file_path)

    assert len(tt_lines) > 0, "Failed to read from file"

    tt_map: dict[str, list[TreasureTableEntry]] = parser.parse_treasure_table(tt_lines)

    assert tt_map is not None, "Failed to parse treasure table"
    assert len(tt_map) > 0, "Empty treasure table"

    return tt_map


@pytest.fixture(scope="session")
def treasure_table_map():
    tt_map = get_tt_map(FIXTURE_PATHS["TREASURE_TABLE"])
    assert len(tt_map.keys()) == 29
    yield tt_map


def test_parse_file(treasure_table_map: dict[str, list[TreasureTableEntry]]):
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

    for tt in treasure_table_map:
        tt_entry_len = len(treasure_table_map[tt])
        if tt in entry_map:
            assert tt_entry_len == len(entry_map[tt]), f"Entries mismatch: {tt}"

        for entry in treasure_table_map[tt]:
            assert entry.is_valid, "Unexpected invalid entry"
            assert len(entry.options) == 8, "No options"

        # logger.debug(f"{tt}: {tt_entry_len} entries")


def test_treasure_table_summary(
    treasure_table_map: dict[str, list[TreasureTableEntry]],
):
    summary = parser.get_summary_from_tt_map(treasure_table_map)

    assert summary, "Failed to get treasure table summary"

    for obj_category_name in summary:
        assert (
            len(summary[obj_category_name]) > 0
        ), f"{obj_category_name} is not in at least 1 TT"

        """
        logger.debug(
            f"{obj_category_name} is in {len(summary[obj_category_name])} tables"
        )
        """


def test_invalid_tt_entry():
    tt_map = get_tt_map("tests/fixture/TreasureTableInvalidEntry.txt")
    num_invalid_entries = 0

    for tt_name in tt_map:
        for entry in tt_map[tt_name]:
            if not entry.is_valid:
                num_invalid_entries += 1

    assert num_invalid_entries == 1, "Invalid entry detection not working as expected"
