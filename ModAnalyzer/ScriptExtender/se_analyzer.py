import json
import logging
import os
from numbers import Number
from pathlib import Path

from ModAnalyzer.Structure.structure_analyzer import StructureAnalyzer


class SEReport:
    has_se_dir: bool = False
    has_config: bool = False
    config_parse_error: str = ""
    config_missing_fields: list[str] = []
    config_invalid_fields: dict[str, str] = {}
    config: dict
    has_server_dir: bool = False
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

    def has_required_config_fields(self, missing_fields: list[str]) -> bool:
        return len(missing_fields) == 0

    def has_bootstrap_server(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_bootstrap_server_file_path()
        )

    def has_bootstrap_client(self, mod_dirs: list[str]) -> bool:
        return self.structure_analyzer.is_path_in_mod_dirs(
            mod_dirs, self.get_bootstrap_client_file_path()
        )

    def get_required_config_fields(self) -> tuple:
        return ("RequiredVersion", "ModTable", "FeatureFlags")

    def get_missing_config_fields(self, parsed_config: dict) -> list[str]:
        required_fields: tuple = self.get_required_config_fields()
        missing_fields: list[str] = []

        for field in required_fields:
            if field not in parsed_config:
                missing_fields.append(field)

        return missing_fields

    def get_invalid_config_fields(self, parsed_config: dict) -> dict[str, str]:
        """
        This should be run after confirming
        """
        invalid_fields: dict[str, str] = {}

        try:
            req_version = parsed_config["RequiredVersion"]
            if not isinstance(req_version, Number):
                invalid_fields["RequiredVersion"] = "Value does not seem to be a number"

            if len(parsed_config["ModTable"]) == 0:
                invalid_fields["ModTable"] = "Value is blank"

            if (
                not isinstance(parsed_config["FeatureFlags"], list)
                or "Lua" not in parsed_config["FeatureFlags"]
            ):
                invalid_fields["FeatureFlags"] = (
                    'Value is not a list or is missing "Lua"'
                )

            return invalid_fields
        except KeyError:
            # missing_key = str(missing_key_ex)
            # invalid_fields[missing_key] = f"{missing_key} is missing from the config"
            pass
        except Exception as err:
            self.logger.error(f"Unexpected error in get_invalid_config_fields: {err}")
        finally:
            return invalid_fields

    def get_parsed_config(self, config_path: str) -> dict | None:
        path = Path(config_path)
        if path.exists():
            config_contents = path.read_text()
            config = json.loads(config_contents)
            self.logger.debug("Parsed SE config successfully")
            return config

    def generate_report(self, mod_dirs: list[str]) -> SEReport:
        report = SEReport()

        report.has_se_dir = self.has_se_dir(mod_dirs)

        if report.has_se_dir:
            report.has_server_dir = self.has_server_dir(mod_dirs)
            report.has_config = self.has_config(mod_dirs)

            if report.has_config:
                config_path = self.get_config_path()

                try:
                    parsed_config = self.get_parsed_config(config_path)
                    if parsed_config:
                        missing_fields = self.get_missing_config_fields(parsed_config)

                        if len(missing_fields) > 0:
                            report.config_missing_fields = missing_fields

                        report.config = parsed_config
                        report.config_invalid_fields = self.get_invalid_config_fields(
                            parsed_config
                        )
                    else:
                        self.logger.error("Config does not exist?")
                except json.JSONDecodeError as err:
                    # This log will show in the output!
                    # self.logger.error(f"Error parsing {config_path}: {err}")
                    report.config_parse_error = str(err)
                except Exception:
                    self.logger.error(f"Unexpected error while parsing {config_path}")

            if report.has_server_dir:
                report.has_bootstrap_server = self.has_bootstrap_server(mod_dirs)
                report.has_bootstrap_client = self.has_bootstrap_client(mod_dirs)

        return report
