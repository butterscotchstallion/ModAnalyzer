import logging
import os

from ModAnalyzer import Structure
from ModAnalyzer.TreasureTable import (
    TreasureTableAnalyzer,
)
from tests.conftest import FIXTURE_PATHS

logger = logging.getLogger("TestTreasureTableAnalyzer")


def test_generate_report(mod_dirs_fixture: list[str]):
    structure_analyzer = Structure.StructureAnalyzer()
    structure_report = structure_analyzer.generate_report("TestMod", mod_dirs_fixture)

    tt_filename = structure_analyzer.get_treasure_table_file_path()
    rt_dir = structure_analyzer.get_rt_dir()

    assert structure_report.has_treasure_table, f"No treasure table at {tt_filename}"

    if structure_report.has_treasure_table:
        treasure_table_analyzer = TreasureTableAnalyzer()
        tt_report = treasure_table_analyzer.generate_report(tt_filename, rt_dir)

        assert len(tt_report.valid_items) == 13
        assert len(tt_report.treasure_table_entries) == 29


def test_check_items():
    analyzer = TreasureTableAnalyzer()
    report = analyzer.generate_report(
        FIXTURE_PATHS["TREASURE_TABLE"],
        os.path.split(FIXTURE_PATHS["ROOT_TEMPLATE"])[0],
    )

    if len(report.inaccessible_items) > 0:
        logger.error(
            f"Items not in a treasure table: {report.inaccessible_items} ({len(report.valid_items)}, {len(report.inaccessible_items)})"
        )

    assert len(report.valid_items) > 0, "No valid items!"
    assert len(report.inaccessible_items) == 0, "Some items not verified"


def test_replacement_entry_detection():
    analyzer = TreasureTableAnalyzer()
    report = analyzer.generate_report(
        "tests/fixture/TreasureTableWithoutReplacementEntryExample.txt",
        os.path.split(FIXTURE_PATHS["ROOT_TEMPLATE"])[0],
    )

    assert len(report.treasure_table_entries) == 2, "Failed to find entry"
    assert len(report.replacement_entries) == 2, "Failed to identify replacement entry"
