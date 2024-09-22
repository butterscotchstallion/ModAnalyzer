import pprint

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

    def get_colored_status(self, status: bool):
        if status:
            return typer.style("OK", fg=typer.colors.GREEN, bold=True)
        else:
            return typer.style("FAIL", fg=typer.colors.RED, bold=True)

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

    def analyze(self, mod_dir: str):
        # Structure report
        structure_analyzer = Structure.StructureAnalyzer()
        structure_report = structure_analyzer.generate_report(mod_dir)

        headers = ["Subject", "Status", "Notes"]
        summary_table = [
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
                structure_analyzer.path_analyzer.get_colored_path(
                    structure_analyzer.get_rt_dir()
                ),
            ],
            [
                "Treasure Table",
                self.get_colored_status(structure_report.has_treasure_table),
                structure_analyzer.path_analyzer.get_colored_path(
                    structure_analyzer.get_treasure_table_file_path()
                ),
            ],
        ]

        if structure_report.mod_dir_exists:
            # Treasure table report
            if structure_report.has_treasure_table:
                tt_filename = structure_analyzer.get_treasure_table_file_path()
                rt_dir = structure_analyzer.get_rt_dir()
                tt_report = self.get_tt_report(tt_filename, rt_dir)

                """
                summary_table[0].append(
                    [""]
                )
                """

        typer.echo(tabulate(summary_table, headers=headers))

    def get_tt_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        tt_analyzer = TreasureTableAnalyzer()
        report = tt_analyzer.generate_report(tt_filename, rt_dir)
        return report
