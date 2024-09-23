import json
import logging
import os
from pathlib import Path

from ModAnalyzer.Structure.structure_analyzer import StructureAnalyzer


class SEReport:
    has_se_dir: bool = False
    has_config: bool = False
    has_server_dir: bool = False
    has_config_parse_error: bool = False
    has_bootstrap_server: bool = False
    has_bootstrap_client: bool = False


class SEAnalyzer:
    structure_analyzer: StructureAnalyzer

    """
    Analyzes structure and files of the ScriptExtender folder
    """

    def __init__(self, **kwargs):
        self.structure_analyzer = kwargs["structure_analyzer"]
        self.mod_dir_name = kwargs["mod_dir_name"]
        self.logger = logging.getLogger(__file__)

    def get_config_path(self) -> str:
        return os.path.join(self.get_base_path(), "Config.json")

    def get_base_path(self) -> str:
        path_parts = [self.structure_analyzer.get_mods_modname_path(), "ScriptExtender"]
        self.logger.debug(path_parts)
        return os.path.join(*path_parts)

    def get_server_dir(self) -> str:
        return os.path.join(*[self.get_base_path(), "Lua", "Server"])

    def get_bootstrap_server_file_path(self) -> str:
        return os.path.join(self.get_server_dir(), "BootstrapServer.lua")

    def get_bootstrap_client_file_path(self) -> str:
        return os.path.join(self.get_server_dir(), "BootstrapClient.lua")

    ####################

    def has_se_dir(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_base_path()
        )

    def has_server_dir(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_server_dir()
        )

    def has_config(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_config_path()
        )

    def has_bootstrap_server(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_bootstrap_server_file_path()
        )

    def has_bootstrap_client(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_bootstrap_client_file_path()
        )

    def has_config_parse_error(self, config_path: str):
        try:
            config_contents = Path(config_path).read_text()
            json.loads(config_contents)
            self.logger.debug("Parsed SE config successfully")
            return False
        except json.JSONDecodeError as err:
            self.logger.error(f"Error parsing {config_path}: {err}")
            return True
        except Exception:
            self.logger.error(f"Unexpected error while parsing {config_path}")
            return True

    def generate_report(self, mod_dirs: list[str]) -> SEReport:
        report = SEReport()

        report.has_se_dir = self.has_se_dir(mod_dirs)

        if report.has_se_dir:
            report.has_server_dir = self.has_server_dir(mod_dirs)

            if report.has_server_dir:
                report.has_config = self.has_config(mod_dirs)

                if report.has_config:
                    report.has_config_parse_error = self.has_config_parse_error(
                        self.get_config_path()
                    )

                report.has_bootstrap_server = self.has_bootstrap_server(mod_dirs)
                report.has_bootstrap_client = self.has_bootstrap_client(mod_dirs)

        return report
