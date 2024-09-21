import logging
import os
from dataclasses import dataclass


@dataclass(init=False)
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class PathAnalyzerReport:
    paths: dict[str, dict]
    colored_path: str

    def __init__(self):
        self.paths = {}
        self.colored_path = ""


class PathAnalyzer:
    """
    Displays a directory path with colors
    to indicate which part doesn't exist
    """

    EXISTS_COLOR: str
    NON_EXISTENT_COLOR: str

    def __init__(self):
        self.EXISTS_COLOR = bcolors.OKGREEN
        self.NON_EXISTENT_COLOR = bcolors.FAIL
        self.logger = logging.getLogger(__name__)

    def get_colored_path(self, path: str):
        report = self.get_path_report(path)
        return report.colored_path

    def get_path_report(self, path: str) -> PathAnalyzerReport:
        """
        Generates a PathAnalyzerReport based on supplied path
        """
        report = PathAnalyzerReport()
        path_parts = path.split(os.sep)
        colored_paths = []
        existent_paths = []
        encountered_non_existent_dir = False

        for p in path_parts:
            exists = False
            color = bcolors.FAIL
            test_path = p

            if len(existent_paths) > 0:
                test_path = os.path.join(*existent_paths, p)

            if not encountered_non_existent_dir and os.path.exists(test_path):
                exists = True
                color = bcolors.OKGREEN
                existent_paths.append(p)
            else:
                encountered_non_existent_dir = True

            # if os.path.isfile(test_path):
            #    color = bcolors.OKCYAN

            # The file shows as existent here because we are testing the whole path
            # self.logger.debug(f"{color}{p}: {exists}{bcolors.ENDC}")

            path_with_colors = f"{color}{p}{bcolors.ENDC}"
            report.paths[p] = {"exists": exists, "path_with_color": path_with_colors}
            colored_paths.append(path_with_colors)

        report.colored_path = os.path.join(*colored_paths)

        return report
