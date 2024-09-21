import logging
import os

from ModAnalyzer.Structure.path_analyzer import PathAnalyzer, PathAnalyzerReport

logger = logging.getLogger(__name__)


def test_path_exists():
    analyzer = PathAnalyzer()
    path_parts = ["tests", "fixture", "dirs.json"]
    report: PathAnalyzerReport = analyzer.get_path_report(os.path.join(*path_parts))

    assert report.paths["tests"]["exists"]
    assert report.paths["fixture"]["exists"]
    assert report.paths["dirs.json"]["exists"]

    logger.debug(report.colored_path)


def test_path_doesnt_exist():
    analyzer = PathAnalyzer()
    path_parts = ["tests", "woof", "meow"]
    report: PathAnalyzerReport = analyzer.get_path_report(os.path.join(*path_parts))

    assert report.paths["tests"]["exists"]
    assert not report.paths["woof"]["exists"]
    assert not report.paths["meow"]["exists"]

    logger.debug(report.colored_path)
