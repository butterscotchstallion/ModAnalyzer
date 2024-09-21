import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from ModAnalyzer import Structure, TreasureTable
from ModAnalyzer.Structure.path_analyzer import PathAnalyzer


class TreasureTableReport:
    verified_items: list[str] = []
    total_items: int = 0
    treasure_table_entries: list[str]


class TreasureTableAnalyzer:
    """
    Checks that all nodes from the RT appear in at least one
    treasure table
    """

    path_analyzer: PathAnalyzer
    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.path_analyzer = PathAnalyzer()

    def get_item_list(
        self, rt_parser: TreasureTable.RootTemplateParser, rt_dir: str
    ) -> list[ET.Element]:
        """
        1. Find LSX files in RT dir
        2. Parse the XML from each file
        3. Get nodes from each file
        4. Add to list
        """
        nodes: list[ET.Element] = []
        structure_analyzer = Structure.StructureAnalyzer()
        rt_dir_path = Path(rt_dir)
        try:
            if rt_dir_path.exists():
                root_templates = structure_analyzer.get_lsx_files_in_dir(rt_dir_path)

                if len(root_templates) > 0:
                    rt_nodes = []
                    for rt in root_templates:
                        rt_path = Path(os.path.join(rt_dir_path, rt))

                        if rt_path.exists():
                            rt_xml = rt_path.read_text()
                            root_node = ET.fromstring(rt_xml)
                            dir_nodes = rt_parser.get_unignored_nodes(root_node)
                            rt_nodes += dir_nodes

                            self.logger.debug(f"Added {len(dir_nodes)} from {rt}")
                        else:
                            self.logger.error(
                                f"TreasureTableAnalyzer: {self.path_analyzer.get_colored_path(str(rt))} does not exist"
                            )
                else:
                    self.logger.error(
                        f"TreasureTableAnalyzer: cannot find any RTs in {rt_dir}"
                    )
            else:
                self.logger.error(f"TreasureTableAnalyzer: cannot find RT dir {rt_dir}")
        except Exception as err:
            self.logger.error(f"TreasureTableAnalyzer: Unexpected exception: {err}")
        finally:
            return nodes

    def generate_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        report = TreasureTableReport()

        # Read/parse treasure tables
        reader = TreasureTable.TreasureTableReader()
        tt_parser = TreasureTable.TreasureTableParser()
        tt_lines = reader.read_from_file(tt_filename)
        items_verified = []
        report.total_items = 0

        if len(tt_lines) > 0:
            tt_map = tt_parser.parse_treasure_table(tt_lines)
            tt_summary = tt_parser.get_summary_from_tt_map(tt_map)
            # Read/parse RTs
            rt_parser = TreasureTable.RootTemplateParser()
            rt_nodes = self.get_item_list(rt_parser, rt_dir)

            if len(rt_nodes) > 0:
                stats_names = rt_parser.get_stats_names_from_node_children(rt_nodes)
                # Verify stats names against treasure tables
                verified_items = self.check_items(stats_names, tt_summary)
                items_verified = len(verified_items) == len(stats_names)

                if not items_verified:
                    unverified_items = [
                        item for item in stats_names if item not in verified_items
                    ]
                    self.logger.error(
                        f"Items not in a treasure table: {unverified_items} ({len(verified_items)}, {len(stats_names)})"
                    )

            else:
                self.logger.info("0 nodes found from LSX files")
        else:
            self.logger.info("0 treasure table entries found")

        return report

    def check_items(
        self, stats_names: set[str], tt_summary: dict[str, list[str]]
    ) -> list[str]:
        """
        Checks each item's stats name against the treasure table summary
        """
        verified_items: list[str] = []
        for stats_name in stats_names:
            if self.item_in_treasure_table(stats_name, tt_summary):
                verified_items.append(stats_name)
        return verified_items

    def item_in_treasure_table(
        self, object_category_name: str, tt_summary: dict[str, list[str]]
    ) -> bool:
        """Checks if stats name is in summary"""
        exists = False
        tt_entry_name = f"I_{object_category_name}"
        if tt_entry_name in tt_summary.keys():
            exists = len(tt_summary[tt_entry_name]) > 0
        return exists
