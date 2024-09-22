import pprint

from ModAnalyzer import Structure
from ModAnalyzer.Structure import StructureReport
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

    def analyze(self, mod_dir: str):
        # Structure report
        structure_analyzer = Structure.StructureAnalyzer()
        structure_report = structure_analyzer.generate_report(mod_dir)

        pprint.pp(structure_report)

        # Treasure table report
        if structure_report.has_treasure_table:
            tt_filename = structure_analyzer.get_treasure_table_file_path()
            rt_dir = structure_analyzer.get_rt_dir()
            tt_report = self.get_tt_report(tt_filename, rt_dir)
            pprint.pp(tt_report)
        else:
            print("No treasure table found")

    def get_tt_report(self, tt_filename: str, rt_dir: str) -> TreasureTableReport:
        tt_analyzer = TreasureTableAnalyzer()
        report = tt_analyzer.generate_report(tt_filename, rt_dir)
        return report
