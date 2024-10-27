import logging
import os

from ModAnalyzer.Structure.path_analyzer import PathAnalyzer, PathAnalyzerReport

logger = logging.getLogger(__name__)


def test_path_exists():
    analyzer = PathAnalyzer()
    report: PathAnalyzerReport = analyzer.get_path_report(
        os.path.join("tests", "fixture", "dirs.json")
    )

    assert report.paths["tests"]["exists"]
    assert report.paths["fixture"]["exists"]
    assert report.paths["dirs.json"]["exists"]

    logger.debug(report.colored_path)


def test_path_doesnt_exist():
    analyzer = PathAnalyzer()
    report: PathAnalyzerReport = analyzer.get_path_report(
        os.path.join("tests", "woof", "meow")
    )

    assert report.paths["tests"]["exists"]
    assert not report.paths["woof"]["exists"]
    assert not report.paths["meow"]["exists"]

    logger.debug(report.colored_path)
