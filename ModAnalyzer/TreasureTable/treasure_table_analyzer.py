import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from ModAnalyzer import Structure, TreasureTable
from ModAnalyzer.Structure import PathAnalyzer
from ModAnalyzer.TreasureTable.models import ItemSummary, TreasureTableEntry


class TreasureTableReport:
    verified_items: list[ET.Element] = []
    ignored_items: list[ET.Element] = []
    treasure_table_entries: list[TreasureTableEntry] = []
    inaccessible_items: list[str] = []
    replacement_entries: set[str] = set()
    invalid_entries: set[str] = set()


class TreasureTableAnalyzer:
    """
    Checks that all nodes from the RT appear in at least one
    treasure table
    """

    path_analyzer: PathAnalyzer
    logger: logging.Logger

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.path_analyzer = PathAnalyzer(**kwargs)

    def get_item_list(
        self, rt_parser: TreasureTable.RootTemplateParser, rt_dir: str
    ) -> ItemSummary:
        """
        1. Find LSX files in RT dir
        2. Parse the XML from each file
        3. Get nodes from each file
        4. Add to list
        """
        item_summary: ItemSummary = {"verified": [], "ignored": []}
        verified_nodes: list[ET.Element] = []
        ignored_nodes: list[ET.Element] = []
        structure_analyzer = Structure.StructureAnalyzer()
        rt_dir_path = Path(rt_dir)
        try:
            if rt_dir_path.exists() and rt_dir_path.is_dir():
                root_templates = structure_analyzer.get_lsx_files_in_dir(rt_dir_path)

                if len(root_templates) > 0:
                    for rt in root_templates:
                        rt_path = Path(rt)

                        if rt_path.exists():
                            rt_xml = rt_path.read_text()
                            root_node = ET.fromstring(rt_xml)
                            file_summary = rt_parser.get_verified_nodes(root_node)
                            # All verified nodes
                            verified_nodes += file_summary["verified"]
                            # All ignored nodes
                            ignored_nodes += file_summary["ignored"]

                            log_msg = f"Added {len(file_summary["verified"])} ({len(file_summary["ignored"])} ignored)"
                            log_msg += " nodes from {rt_path.stem}{rt_path.suffix}"
                            self.logger.debug(log_msg)
                        else:
                            self.logger.error(
                                f"TreasureTableAnalyzer: RT path {self.path_analyzer.get_colored_path(str(rt_path))} does not exist"
                            )
                    item_summary["verified"] = verified_nodes
                    item_summary["ignored"] = ignored_nodes
                else:
                    self.logger.error(
                        f"TreasureTableAnalyzer: cannot find any RTs in {rt_dir}"
                    )
            else:
                self.logger.error(
                    f"TreasureTableAnalyzer: {rt_dir} doesn't exist or isn't a directory"
                )
        except Exception as err:
            self.logger.error(f"TreasureTableAnalyzer: Unexpected exception: {err}")
        finally:
            return item_summary

    def get_replacement_entries_from_map(
        self,
        tt_map: dict[str, list[TreasureTableEntry]],
    ) -> set[str]:
        """
        CanMerge is a property of treasure tables, but the way
        I implemented this, I made it a property of the items in
        each treasure table. I thought about refactoring it, but
        the result is the same this way.
        """
        replacement_entries: set[str] = set()

        for tt_name in tt_map:
            for entry in tt_map[tt_name]:
                if not entry.can_merge:
                    replacement_entries.add(entry.object_category_name)

        return replacement_entries

    def get_invalid_entries(
        self, tt_map: dict[str, list[TreasureTableEntry]]
    ) -> set[str]:
        invalid_entries = set()

        for tt_name in tt_map:
            for entry in tt_map[tt_name]:
                if not entry.is_valid:
                    invalid_entries.add(entry.object_category_name)

        return invalid_entries

    def generate_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        report = TreasureTableReport()

        # Read/parse treasure tables
        reader = TreasureTable.TreasureTableReader()
        tt_parser = TreasureTable.TreasureTableParser()
        tt_lines = reader.read_from_file(tt_filename)
        items_verified: bool = False

        if len(tt_lines) > 0:
            tt_map: dict[str, list[TreasureTableEntry]] = (
                tt_parser.parse_treasure_table(tt_lines)
            )
            tt_summary: dict[str, list[str]] = tt_parser.get_summary_from_tt_map(tt_map)
            # Read/parse RTs
            rt_parser = TreasureTable.RootTemplateParser()
            item_summary: ItemSummary = self.get_item_list(rt_parser, rt_dir)
            rt_nodes = item_summary["verified"]

            report.invalid_entries = self.get_invalid_entries(tt_map)
            report.replacement_entries = self.get_replacement_entries_from_map(tt_map)

            self.logger.debug(f"rt_nodes: {rt_nodes}")

            if len(rt_nodes) > 0:
                stats_names = rt_parser.get_stats_names_from_node_children(rt_nodes)
                # Verify stats names against treasure tables
                verified_stat_names: list[str] = self.check_items(
                    stats_names, tt_summary
                )
                items_verified: bool = len(verified_stat_names) == len(stats_names)

                report.verified_items = item_summary["verified"]
                report.ignored_items = item_summary["ignored"]
                report.treasure_table_entries = tt_parser.get_flattened_map(tt_map)

                if not items_verified:
                    report.inaccessible_items = [
                        item for item in stats_names if item not in verified_stat_names
                    ]
                    self.logger.error(
                        f"Items not in a treasure table: {report.inaccessible_items} ({len(verified_stat_names)}, {len(stats_names)})"
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
