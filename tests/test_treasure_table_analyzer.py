import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from ModAnalyzer import Structure
from ModAnalyzer.TreasureTable import (
    RootTemplateParser,
    TreasureTableAnalyzer,
    TreasureTableParser,
    TreasureTableReader,
)
from tests.conftest import FIXTURE_PATHS

logger = logging.getLogger("TestTreasureTableAnalyzer")


def test_generate_report(mod_dirs_fixture: list[str]):
    structure_analyzer = Structure.StructureAnalyzer()
    structure_report = structure_analyzer.generate_report("TestMod", mod_dirs_fixture)

    tt_filename = structure_analyzer.get_treasure_table_file_path()
    rt_dir = structure_analyzer.get_rt_dir()

    logger.debug(f"RT dir: {rt_dir}")

    assert structure_report.has_treasure_table, f"No treasure table at {tt_filename}"

    if structure_report.has_treasure_table:
        treasure_table_analyzer = TreasureTableAnalyzer()
        tt_report = treasure_table_analyzer.generate_report(tt_filename, rt_dir)

        assert tt_report.total_items == 13
        assert len(tt_report.verified_items) == 13
        assert len(tt_report.treasure_table_entries) == 29


def test_check_items():
    # Read/parse treasure tables
    reader = TreasureTableReader()
    tt_parser = TreasureTableParser()
    tt_lines = reader.read_from_file(FIXTURE_PATHS["TREASURE_TABLE"])
    tt_map = tt_parser.parse_treasure_table(tt_lines)
    tt_summary = tt_parser.get_summary_from_tt_map(tt_map)
    # Read/parse RTs
    rt_parser = RootTemplateParser()
    rt_xml = Path(FIXTURE_PATHS["ROOT_TEMPLATE"]).read_text()
    root_node = ET.fromstring(rt_xml)
    rt_nodes = rt_parser.get_unignored_nodes(root_node)
    stats_names = rt_parser.get_stats_names_from_node_children(rt_nodes)
    # Verify stats names against treasure tables
    checker = TreasureTableAnalyzer()
    verified_items = checker.check_items(stats_names, tt_summary)
    items_verified = len(verified_items) == len(stats_names)

    if not items_verified:
        unverified_items = [item for item in stats_names if item not in verified_items]
        logger.error(
            f"Items not in a treasure table: {unverified_items} ({len(verified_items)}, {len(stats_names)})"
        )

    assert items_verified, "Some items not verified"
