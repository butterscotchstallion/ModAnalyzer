import json
import logging
import os
from pathlib import Path

from ModAnalyzer.Structure.structure_analyzer import StructureAnalyzer


class SEReport:
    has_se_dir: bool = False
    has_config: bool = False
    has_server_dir: bool = False
    config_parse_error: str = ""
    has_bootstrap_server: bool = False
    has_bootstrap_client: bool = False


class SEAnalyzer:
    structure_analyzer: StructureAnalyzer

    """
    Analyzes structure and files of the ScriptExtender folder
    """

    def __init__(self, **kwargs):
        self.structure_analyzer = kwargs["structure_analyzer"]
        self.logger = logging.getLogger(__file__)

    def get_config_path(self) -> str:
        config_path = os.path.join(self.get_base_path(), "Config.json")
        # TestMod\Mods\TestMod\ScriptExtender\Config.json
        # TestMod\Mods\TestMod\ScriptExtender\Config.json
        self.logger.debug(config_path)
        return config_path

    def get_base_path(self) -> str:
        path_parts = [self.structure_analyzer.get_mods_modname_path(), "ScriptExtender"]
        return os.path.join(*path_parts)

    def get_lua_dir(self) -> str:
        return os.path.join(*[self.get_base_path(), "Lua"])

    def get_server_dir(self) -> str:
        return os.path.join(self.get_lua_dir(), "Server")

    def get_bootstrap_server_file_path(self) -> str:
        return os.path.join(self.get_lua_dir(), "BootstrapServer.lua")

    def get_bootstrap_client_file_path(self) -> str:
        return os.path.join(self.get_lua_dir(), "BootstrapClient.lua")

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

    def get_config_parse_error(self, config_path: str) -> str | None:
        try:
            path = Path(config_path)
            if path.exists():
                config_contents = path.read_text()
                json.loads(config_contents)
                self.logger.debug("Parsed SE config successfully")
        except json.JSONDecodeError as err:
            self.logger.error(f"Error parsing {config_path}: {err}")
            return str(err)
        except Exception:
            self.logger.error(f"Unexpected error while parsing {config_path}")

    def generate_report(self, mod_dirs: list[str]) -> SEReport:
        report = SEReport()

        report.has_se_dir = self.has_se_dir(mod_dirs)

        if report.has_se_dir:
            report.has_server_dir = self.has_server_dir(mod_dirs)

            if report.has_server_dir:
                report.has_config = self.has_config(mod_dirs)

                if report.has_config:
                    config_parse_error = self.get_config_parse_error(
                        self.get_config_path()
                    )
                    if config_parse_error:
                        report.config_parse_error = config_parse_error

                report.has_bootstrap_server = self.has_bootstrap_server(mod_dirs)
                report.has_bootstrap_client = self.has_bootstrap_client(mod_dirs)

        return report
