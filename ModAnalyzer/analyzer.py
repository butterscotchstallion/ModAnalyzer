import os
import pprint
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import typer
from tabulate import tabulate

from ModAnalyzer import Structure
from ModAnalyzer.ScriptExtender import SEAnalyzer
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

    def print(self, input_str: str):
        if self.using_typer:
            typer.echo(input_str)
        else:
            pprint.pp(input_str)

    def get_colored_status(
        self,
        status: bool,
        ok_str="FOUND",
        fail_str="NOT FOUND",
        ok_color=typer.colors.GREEN,
        fail_color=typer.colors.RED,
    ):
        if status:
            return typer.style(ok_str, fg=ok_color, bold=True)
        else:
            return typer.style(fail_str, fg=fail_color, bold=True)

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
            for mod_dir in analyzer.mod_dirs:
                debug_tbl.append([mod_dir])

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

            num_verified_items = typer.style(
                len(tt_report.verified_items), typer.colors.GREEN
            )
            tt_report_table = [
                [
                    "Verified treasure items",
                    self.get_colored_status(True, ok_str="OK", fail_str="FAIL"),
                    f"{num_verified_items} items present in treasure tables",
                ]
            ]

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

    def print_se_report(
        self, mod_dirs: list[str], structure_analyzer: StructureAnalyzer
    ):
        se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)
        se_report = se_analyzer.generate_report(mod_dirs)

        """
        has_se_dir: bool = False
        has_config: bool = False
        has_server_dir: bool = False
        has_config_parse_error: bool = False
        has_bootstrap_server: bool = False
        has_bootstrap_client: bool = False
        """
        se_report_table = [
            [
                "SE dir",
                self.get_colored_status(se_report.has_se_dir),
                self.path_analyzer.get_colored_path(se_analyzer.get_base_path()),
            ]
        ]

        if se_report.has_se_dir:
            ### Config
            se_report_table.append(
                [
                    "Config file",
                    self.get_colored_status(se_report.has_config),
                    self.path_analyzer.get_colored_path(se_analyzer.get_config_path()),
                ]
            )

            if se_report.has_config:
                # Parse error
                if se_report.config_parse_error:
                    se_report_table.append(
                        [
                            "Config Parse Error",
                            self.get_colored_status(
                                len(se_report.config_parse_error) == 0,
                                ok_str="OK",
                                fail_str="FAIL",
                            ),
                            typer.style(
                                se_report.config_parse_error,
                                fg=typer.colors.RED,
                                bold=True,
                            ),
                        ]
                    )
                else:
                    # Missing fields
                    has_invalid_fields = False

                    missing_fields = se_report.config_missing_fields
                    has_missing_fields = len(missing_fields) > 0
                    missing_color = (
                        typer.colors.RED if has_missing_fields else typer.colors.GREEN
                    )
                    se_report_table.append(
                        [
                            "Config Required Fields",
                            self.get_colored_status(not has_missing_fields),
                            typer.style(
                                ", ".join(se_analyzer.get_required_config_fields()),
                                fg=missing_color,
                                bold=True,
                            ),
                        ]
                    )

                    # Check invalid fields
                    if not has_missing_fields:
                        invalid_fields = se_report.config_invalid_fields
                        has_invalid_fields = len(invalid_fields) > 0
                        invalid_fields_summary = []
                        for field in invalid_fields:
                            invalid_fields_summary.append(
                                f"{field}: {invalid_fields[field]}"
                            )

                        if has_invalid_fields:
                            se_report_table.append(
                                [
                                    "Config Invalid Fields",
                                    self.get_colored_status(
                                        not has_invalid_fields, fail_str="FAIL"
                                    ),
                                    typer.style(
                                        os.linesep.join(invalid_fields_summary),
                                        fg=typer.colors.RED,
                                        bold=True,
                                    ),
                                ]
                            )

                    if not has_missing_fields and not has_invalid_fields:
                        pass

            ### Directories
            se_report_table.append(
                [
                    "Server dir",
                    self.get_colored_status(se_report.has_server_dir),
                    self.path_analyzer.get_colored_path(se_analyzer.get_server_dir()),
                ]
            )

            if (
                not se_report.has_bootstrap_server
                and not se_report.has_bootstrap_client
            ):
                se_report_table.append(
                    [
                        "Bootstrap files",
                        self.get_colored_status(se_report.has_bootstrap_client),
                        os.linesep.join(
                            [
                                self.path_analyzer.get_colored_path(
                                    se_analyzer.get_bootstrap_server_file_path()
                                ),
                                self.path_analyzer.get_colored_path(
                                    se_analyzer.get_bootstrap_client_file_path()
                                ),
                                "You need at least one of these",
                            ]
                        ),
                    ]
                )
            else:
                se_report_table.append(
                    [
                        "BootstrapServer file",
                        self.get_colored_status(
                            se_report.has_bootstrap_server,
                            fail_color=typer.colors.YELLOW,
                        ),
                        self.path_analyzer.get_colored_path(
                            se_analyzer.get_bootstrap_server_file_path()
                        ),
                    ]
                )
                se_report_table.append(
                    [
                        "BootstrapClient file",
                        self.get_colored_status(
                            se_report.has_bootstrap_client,
                            fail_color=typer.colors.YELLOW,
                        ),
                        self.path_analyzer.get_colored_path(
                            se_analyzer.get_bootstrap_client_file_path()
                        ),
                    ]
                )

        typer.echo(
            tabulate(
                se_report_table,
                headers=["Script Extender Report", "Status", "Details"],
            )
        )

    def print_analysis_duration(self, start_time: float):
        # Show elapsed time
        elapsed_seconds = round(time.time() - start_time, 2)
        elapsed_desc = typer.style(elapsed_seconds, typer.colors.GREEN)

        typer.echo(os.linesep)
        typer.echo(f"Analysis complete in {elapsed_desc} seconds")
        typer.echo(os.linesep)

    def analyze(self, mod_dir: str, **kwargs):
        start_time: float = time.time()
        mod_name = StructureAnalyzer.get_mod_name_from_dir(mod_dir)
        structure_analyzer = Structure.StructureAnalyzer(mod_name=mod_name)

        # Resolve if relative path
        if "." in mod_dir:
            mod_dir = str(Path(mod_dir).resolve())

        mod_dir = structure_analyzer.get_mod_dir_without_dir_seps(mod_dir)
        structure_report = structure_analyzer.generate_report(mod_dir)
        debug_mode = False

        if "debug_mode" in kwargs:
            debug_mode = kwargs["debug_mode"]

        if structure_report.mod_dir_exists:
            # Structure
            self.print_structure_report(
                mod_dir, structure_analyzer, structure_report, debug_mode
            )

            # Treasure table report
            tt_filename = structure_analyzer.get_treasure_table_file_path()
            rt_dir = structure_analyzer.get_rt_dir()
            has_tt = structure_report.has_treasure_table
            self.print_tt_report(has_tt, tt_filename, rt_dir)
            typer.echo(os.linesep)

            # SE
            self.print_se_report(structure_analyzer.mod_dirs, structure_analyzer)

        self.print_analysis_duration(start_time)

    def get_tt_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        tt_analyzer = TreasureTableAnalyzer()
        report = tt_analyzer.generate_report(tt_filename, rt_dir)
        return report
