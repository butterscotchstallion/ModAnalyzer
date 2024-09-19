import abc

from ModAnalyzer.Structure import StructureReport
from ModAnalyzer.TreasureTable import TreasureTableReport


class AnalyzerReport:
    # TreasureTable: TreasureTableReport
    Structure: StructureReport
    TreasureTable: TreasureTableReport


class Analyzer:
    """
    Compiles reports from submodules
    """

    @abc.abstractmethod
    def analyze(self, mod_dir: str):
        pass
