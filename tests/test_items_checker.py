import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from TreasureTableVerifier.items_checker import ItemsChecker
from TreasureTableVerifier.root_template_parser import RootTemplateParser
from TreasureTableVerifier.treasure_table_parser import TreasureTableParser
from TreasureTableVerifier.treasure_table_reader import TreasureTableReader

logger = logging.getLogger(__name__)


def test_check_items():
    reader = TreasureTableReader()
    tt_parser = TreasureTableParser()
    tt_lines = reader.read_from_file("tests/fixture/TreasureTable.txt")
    tt_map = tt_parser.parse_treasure_table(tt_lines)
    tt_summary = tt_parser.get_summary_from_tt_map(tt_map)
    rt_parser = RootTemplateParser()
    rt_xml = Path("tests/fixture/runes.lsx").read_text()
    root_node = ET.fromstring(rt_xml)
    rt_nodes = rt_parser.get_unignored_nodes(root_node)
    stats_names = rt_parser.get_stats_names_from_node_children(rt_nodes)
    checker = ItemsChecker()
    verified_items = checker.check_items(stats_names, tt_summary)

    items_verified = len(verified_items) == len(stats_names)

    if not items_verified:
        unverified_items = [item for item in stats_names if item not in verified_items]
        logger.error(
            f"Items not in a treasure table: {unverified_items} ({len(verified_items)}, {len(stats_names)})"
        )

    assert items_verified, "Some items not verified"
