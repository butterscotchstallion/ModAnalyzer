import os
import pprint
import time
import xml.etree.ElementTree as ET

import typer
from tabulate import tabulate

from ModAnalyzer import Structure
from ModAnalyzer.Structure import StructureReport
from ModAnalyzer.Structure.path_analyzer import PathAnalyzer
from ModAnalyzer.Structure.structure_analyzer import StructureAnalyzer
from ModAnalyzer.TreasureTable import (
    TreasureTableAnalyzer,
    TreasureTableReport,
)


class AnalyzerReport:
    # TreasureTable: TreasureTableReport
    Structure: StructureReport
    TreasureTable: TreasureTableReport


class Analyzer:
    """
    Compiles reports from submodules
    """

    using_typer: bool = False

    def __init__(self, **kwargs):
        self.path_analyzer = PathAnalyzer(**kwargs)

        if "using_typer" in kwargs:
            self.using_typer = kwargs["using_typer"]

    def print(self, input: str):
        if self.using_typer:
            typer.echo(input)
        else:
            pprint.pp(input)

    def get_colored_status(self, status: bool, ok_str="FOUND", fail_str="NOT FOUND"):
        if status:
            return typer.style(ok_str, fg=typer.colors.GREEN, bold=True)
        else:
            return typer.style(fail_str, fg=typer.colors.RED, bold=True)

    def get_meta_csv_path(self, analyzer: StructureAnalyzer) -> str:
        """
        Gets both meta paths as a comma separated string
        """
        return ", ".join(
            [
                analyzer.path_analyzer.get_colored_path(analyzer.get_meta_path()),
                analyzer.path_analyzer.get_colored_path(analyzer.get_mt_meta_path()),
            ]
        )

    def print_debug_info(self, analyzer: StructureAnalyzer):
        debug_tbl = []

        if len(analyzer.mod_dirs) > 0:
            for dir in analyzer.mod_dirs:
                debug_tbl.append([dir])

            typer.echo(tabulate(debug_tbl, headers=["Mod Directories"]))
        else:
            typer.echo("No mod directories found")

        typer.echo(os.linesep)

    def get_list_of_ignored_items(self, items: list[ET.Element]) -> str:
        names: list[str] = []
        output = ""
        for item in items:
            attributes = item.findall("attribute")

            # Get ignored nodes
            for attr_node in attributes:
                if "id" in attr_node.attrib and attr_node.attrib["id"] == "Name":
                    names.append(attr_node.attrib["value"])

        if len(names) > 0:
            output = ", ".join(names)

        return output

    def get_rt_notes(self, structure_analyzer: StructureAnalyzer) -> str:
        rt_filenames = [
            structure_analyzer.path_analyzer.get_colored_path(str(p))
            for p in structure_analyzer.get_root_templates()
        ]
        rt_list = os.linesep.join(rt_filenames)
        return os.linesep.join(
            [
                # structure_analyzer.path_analyzer.get_colored_path(rt_dir),
                rt_list,
            ]
        )

    def print_structure_report(
        self,
        mod_dir: str,
        structure_analyzer: StructureAnalyzer,
        structure_report: StructureReport,
        debug_mode: bool,
    ):
        if debug_mode:
            self.print_debug_info(structure_analyzer)

        headers = ["Mod Structure Report", "Status", "Details"]
        structure_report_table: list[list[str]] = [
            [
                f'"{mod_dir}" exists',
                self.get_colored_status(structure_report.mod_dir_exists),
                structure_analyzer.path_analyzer.get_colored_path(mod_dir),
            ],
            # ["Mod Fixer", self.get_colored_status(structure_report.has_mod_fixer)],
            [
                "Public directory",
                self.get_colored_status(structure_report.has_public),
                structure_analyzer.path_analyzer.get_colored_path(
                    structure_analyzer.get_public_path()
                ),
            ],
            [
                "Meta file",
                self.get_colored_status(structure_report.has_meta_file),
                self.get_meta_csv_path(structure_analyzer),
            ],
            [
                "Root Templates",
                self.get_colored_status(structure_report.has_root_templates),
                self.get_rt_notes(structure_analyzer),
            ],
            [
                "Treasure Table",
                self.get_colored_status(structure_report.has_treasure_table),
                structure_analyzer.path_analyzer.get_colored_path(
                    structure_analyzer.get_treasure_table_file_path()
                ),
            ],
        ]

        typer.echo(tabulate(structure_report_table, headers=headers))

    def print_tt_report(self, has_tt: bool, tt_filename: str, rt_dir: str):
        # Treasure table report
        if has_tt:
            tt_report = self.get_tt_report(tt_filename, rt_dir)

            """
            valid_items: list[ET.Element] = []
            ignored_items: list[ET.Element] = []
            treasure_table_entries: list[TreasureTableEntry] = []
            inaccessible_items: list[str] = []
            """
            num_valid_items = typer.style(
                len(tt_report.valid_items), typer.colors.GREEN
            )
            tt_report_table = []
            tt_report_table.append(
                [
                    "Valid treasure items",
                    self.get_colored_status(True, ok_str="OK", fail_str="FAIL"),
                    f"{num_valid_items} items present in treasure tables",
                ]
            )

            num_ignored = typer.style(
                len(tt_report.ignored_items), fg=typer.colors.GREEN
            )
            ignored_items_csv = self.get_list_of_ignored_items(tt_report.ignored_items)
            ignored_items_with_paren = (
                f"({ignored_items_csv})" if ignored_items_csv else ""
            )
            tt_report_table.append(
                [
                    "Ignored treasure items",
                    # This isn't really ok/fail
                    self.get_colored_status(True, ok_str="OK", fail_str="FAIL"),
                    f"{str(num_ignored)} items ignored {ignored_items_with_paren}",
                ],
            )

            num_tt_entries = typer.style(
                len(tt_report.treasure_table_entries), fg=typer.colors.GREEN
            )
            tt_report_table.append(
                [
                    "Treasure table entries",
                    self.get_colored_status(True, ok_str="OK", fail_str="FAIL"),
                    f"{num_tt_entries} entries",
                ],
            )

            num_inaccessible = typer.style(
                len(tt_report.inaccessible_items), fg=typer.colors.GREEN
            )
            tt_report_table.append(
                [
                    "Items not in treasure file",
                    self.get_colored_status(True, ok_str="OK", fail_str="FAIL"),
                    f"{num_inaccessible} items may not be accessible",
                ],
            )

            typer.echo(os.linesep)
            typer.echo(
                tabulate(
                    tt_report_table,
                    headers=["Treasure Table Report", "Status", "Details"],
                )
            )
            typer.echo(os.linesep)

    def analyze(self, mod_dir: str, **kwargs):
        start_time: float = time.time()
        structure_analyzer = Structure.StructureAnalyzer()
        structure_report = structure_analyzer.generate_report(mod_dir)
        debug_mode = False

        if "debug_mode" in kwargs:
            debug_mode = kwargs["debug_mode"]

        self.print_structure_report(
            mod_dir, structure_analyzer, structure_report, debug_mode
        )

        if structure_report.mod_dir_exists:
            tt_filename = structure_analyzer.get_treasure_table_file_path()
            rt_dir = structure_analyzer.get_rt_dir()
            has_tt = structure_report.has_treasure_table
            self.print_tt_report(has_tt, tt_filename, rt_dir)

        # Show elapsed time
        elapsed_seconds = round(time.time() - start_time, 2)
        elapsed_desc = typer.style(elapsed_seconds, typer.colors.GREEN)
        typer.echo(f"Analysis complete in {elapsed_desc} seconds")
        typer.echo(os.linesep)

    def get_tt_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        tt_analyzer = TreasureTableAnalyzer()
        report = tt_analyzer.generate_report(tt_filename, rt_dir)
        return report
