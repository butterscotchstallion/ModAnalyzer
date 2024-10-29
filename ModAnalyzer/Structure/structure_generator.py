import json
import logging
import os
import time
import traceback
import uuid
from pathlib import Path
from uuid import uuid4

from directory_tree import DisplayTree
from jinja2 import Environment, FileSystemLoader

from ModAnalyzer.ScriptExtender import SEAnalyzer
from ModAnalyzer.Structure import StructureAnalyzer


class StructureGenerator:
    """
    Creates basic mod structure
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__file__)
        self.tpl_dir = os.path.join(*["ModAnalyzer", "Structure", "file_templates"])
        self.tpl_env = Environment(loader=FileSystemLoader(self.tpl_dir))
        self.mod_name = kwargs["mod_name"]

    def generate_handle(self) -> str:
        reg_uuid = f"h{uuid4()}"
        return reg_uuid.replace("-", "g")

    def create_meta(self, **kwargs) -> bool:
        path = Path(kwargs["meta_path"])
        path.touch(exist_ok=False)
        created = path.exists()

        if created:
            self.logger.debug(f"Created meta: {kwargs["meta_path"]}")
            version_1_int64 = 36028797018963968
            replacements = {
                "MOD_AUTHOR_NAME": kwargs["mod_author_name"],
                "MOD_DESCRIPTION": kwargs["mod_description"],
                "MOD_DIR_NAME": kwargs["mod_dir"],
                "MOD_NAME": self.mod_name,
                "MOD_UUID": kwargs["mod_uuid"],
                "MOD_VERSION_INT64": version_1_int64,
            }
            template = self.get_template_with_replacements(replacements, "meta.lsx")
            path.write_text(template)
        else:
            self.logger.error(f"Error creating meta: {kwargs["meta_path"]}")

        return created

    def create_se_lua_file(
        self, mod_name: str, lua_file_path: str, write_hello_world: bool = False
    ) -> bool:
        se_file_path = Path(lua_file_path)
        se_file_path.touch()

        if write_hello_world:
            hello_world = f'print("Hello world from {mod_name}!{os.linesep * 2}")'
            se_file_path.write_text(hello_world)

        self.logger.debug(
            f"Wrote {se_file_path.stem}.lua ({se_file_path.stat().st_size} bytes)"
        )

        return se_file_path.is_file()

    def create_se_files(self, mod_name: str, se_analyzer: SEAnalyzer) -> bool:
        try:
            config_file_path = Path(se_analyzer.get_config_path())
            if not config_file_path.exists():
                config_file_path.touch(exist_ok=False)
                config_exists = config_file_path.exists()

                if config_exists:
                    config_json = json.dumps(
                        {
                            "RequiredVersion": 20,
                            "ModTable": mod_name,
                            "FeatureFlags": ["Lua"],
                        },
                        indent=4,
                        sort_keys=True,
                    )
                    config_file_path.write_text(config_json)

                    self.logger.debug(f"Wrote SE config JSON to {config_file_path}")

                    """
                    Create server/client bootstraps
                    """

                    # Server
                    server_bootstrap_filename = (
                        se_analyzer.get_bootstrap_server_file_path()
                    )
                    server_bootstrap_path_exists = self.create_se_lua_file(
                        mod_name, server_bootstrap_filename, True
                    )

                    # Client
                    client_bootstrap_filename = (
                        se_analyzer.get_bootstrap_client_file_path()
                    )
                    client_bootstrap_path_exists = self.create_se_lua_file(
                        mod_name, client_bootstrap_filename
                    )

                    return (
                        config_exists
                        and server_bootstrap_path_exists
                        and client_bootstrap_path_exists
                    )
                else:
                    return False
            else:
                self.logger.error(f"create_se_files: {config_file_path} exists")
                return False
        except Exception as err:
            self.logger.error(f"create_se_files: Unexpected error: {err}")
            return False

    def create_root_templates(self, rt_dir: str) -> bool:
        try:
            rt_dir_path = Path(rt_dir)
            rt_dir_path.mkdir(parents=True, exist_ok=False)
            rt_dir_exists = rt_dir_path.exists()

            if rt_dir_exists:
                filename = os.path.join(rt_dir, "merged.lsx")
                filename_path = Path(filename)
                filename_path.touch()

                return filename_path.exists()
            else:
                self.logger.error(f"Failed to create RT dir: {rt_dir}")

            return False
        except Exception as err:
            self.logger.error(f"create_se_files: Unexpected error: {err}")
            return False

    def create_localization_files(
        self, localization_dir_path: str, localization_file_path: str
    ) -> bool:
        try:
            loca_path = Path(localization_dir_path)
            loca_file_exists = False
            if not loca_path.exists():
                loca_path.mkdir(exist_ok=False, parents=True)
                loca_dir_exists = loca_path.exists()

                # Create localization file
                if loca_dir_exists:
                    self.logger.debug(f"Localization directory created: {loca_path}")
                    loca_file_path = Path(localization_file_path)
                    loca_file_path.touch()
                    loca_file_exists = loca_file_path.exists()

                    if loca_file_exists:
                        self.logger.debug(
                            f"Localization file created: {localization_file_path}"
                        )

                return loca_dir_exists and loca_file_exists
            else:
                self.logger.error(
                    f"Localization directory exists at {localization_dir_path}"
                )
                return False
        except Exception as err:
            self.logger.error(
                f"Unexpected error creating localization directory: {err}"
            )
            return False

    def create_file_and_confirm_exists(self, filename: str) -> bool:
        try:
            file_path = Path(filename)
            if not file_path.exists():
                file_path.touch()
                return file_path.exists()
            else:
                self.logger.error(f"File exists at {file_path}")
                return False
        except Exception as err:
            self.logger.error(f"Unexpected error creating file: {err}")
            return False

    def get_template_with_replacements(
        self, replacements: dict, tpl_filename: str
    ) -> str:
        try:
            dir_path = Path(self.tpl_dir)
            tpl_path = Path(os.path.join(self.tpl_dir, tpl_filename))
            is_dir_valid = dir_path.exists() and dir_path.is_dir()
            is_tpl_valid = tpl_path.exists() and tpl_path.is_file()
            if is_dir_valid and is_tpl_valid:
                template = self.tpl_env.get_template(tpl_filename)
                return template.render(**replacements)
            else:
                self.logger.error(f"Template directory {self.tpl_dir} does not exist")
                return ""
        except Exception as err:
            self.logger.error(f"Error creating template: {err}")
            return ""

    def create_sample_tag_file(self, tags_path: str) -> bool:
        """
        1. Get tag template
        2. Replace variables
        3. Write updated string to tags path
        """
        try:
            sample_tag_path = os.path.join(tags_path, "SampleTag.lsx")
            tag_path = Path(sample_tag_path)

            if not tag_path.exists():
                tag_path.touch()

                # Get updated template
                replacements = {
                    "MA_TAG_DISPLAY_DESCRIPTION_HANDLE": "tag desc handle",
                    "MA_TAG_DESCRIPTION": "tag description",
                    "MA_TAG_DISPLAY_NAME_HANDLE": "tag display name handle",
                    "MA_TAG_ICON_NAME": "",
                    "MA_TAG_NAME": "Sample Tag Name",
                    "MA_TAG_UUID": uuid.uuid4(),
                }
                template = self.get_template_with_replacements(replacements, "tag.lsx")

                if not template:
                    return False

                # Write updated template
                tag_path.write_text(template)
            else:
                self.logger.error(f"Sample tag file exists at {sample_tag_path}")

            return False
        except Exception as err:
            self.logger.error(f"Unexpected error while creating sample tag file: {err}")
            return False

    def create_tags_directory_and_sample_tag(self, tags_path: str) -> bool:
        path = None
        try:
            path = Path(tags_path)

            if not path.exists():
                path.mkdir()
                exists = path.exists()

                if exists and path.is_dir():
                    self.create_sample_tag_file(tags_path)

                return exists
            else:
                self.logger.error(f"Tags dir exists at {path}")
                return False
        except Exception as err:
            self.logger.error(f"Unexpected error creating tags dir: {path}: {err}")
            return False

    def create_item_combos_file(self, generated_path: str) -> bool:
        try:
            item_combos_path = Path(os.path.join(generated_path, "ItemCombos.txt"))
            item_combos_path.touch()
            return item_combos_path.exists()
        except Exception as err:
            self.logger.error(f"Unexpected error creating stats files: {err}")
            return False

    def create_stats_files(self, stats_dir: str) -> bool:
        """
        Creates a few stats files as an example
        - Status.txt
        - Passive.txt
        - Target.txt
        - Projectile.txt
        """
        try:
            files: list[str] = [
                "Status.txt",
                "Passive.txt",
                "Target.txt",
                "Projectile.txt",
                "Shout.txt",
                "Character.txt",
                "Object.txt",
            ]

            if Path(stats_dir).exists():
                for filename in files:
                    Path(os.path.join(stats_dir, filename)).touch()
                return True
            else:
                self.logger.error(
                    "Could not create stats files, stats dir doesn't exist"
                )
                return False
        except Exception as err:
            self.logger.error(f"Unexpected error creating stats files: {err}")
            return False

    def get_mod_uuid(self) -> str:
        return str(uuid.uuid4())

    def create_structure(self, **kwargs) -> bool:
        """
        Generates basic mod structure

        TestMod/
        ├── Localization/
        ├── Mods/
        │   └── TestMod/
        │       ├── meta.lsx
        │       └── ScriptExtender/
        │           ├── Config.json
        │           └── Lua/
        │               └── Server/
        └── Public/
            └── TestMod/
                ├── RootTemplates/
                │   └── runes.lsx
                └── Stats/
                    └── Generated/
                        ├── Data/
                        └── TreasureTable.txt
        """
        mod_dir = kwargs["mod_dir"]
        mod_uuid = kwargs["mod_uuid"]
        display_tree = kwargs["display_tree"]

        base_mod_dir_path = Path(mod_dir)

        if not base_mod_dir_path.exists():
            try:
                start_time: float = time.time()
                self.logger.info(f"Creating {mod_dir}")

                structure_analyzer = StructureAnalyzer(
                    mod_dir_name=mod_dir, mod_name=self.mod_name
                )
                se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)
                # First deepest path
                target_path_data = structure_analyzer.get_data_path()
                # SE side
                target_path_server = se_analyzer.get_server_dir()

                # Check dirs exist
                data_path = Path(target_path_data)
                server_path = Path(target_path_server)

                data_path.mkdir(parents=True, exist_ok=False)
                server_path.mkdir(parents=True, exist_ok=False)

                create_success = data_path.exists() and server_path.exists()

                if create_success:
                    self.logger.debug("Main directories created")

                    self.create_meta(
                        meta_path=structure_analyzer.get_meta_path(),
                        mod_dir=mod_dir,
                        mod_uuid=mod_uuid,
                        mod_author_name=kwargs["mod_author_name"],
                        mod_description=kwargs["mod_description"],
                    )
                    self.create_se_files(mod_dir, se_analyzer)
                    self.create_root_templates(structure_analyzer.get_rt_dir())
                    self.create_file_and_confirm_exists(
                        structure_analyzer.get_treasure_table_file_path()
                    )
                    self.create_file_and_confirm_exists(
                        structure_analyzer.get_equipment_file_path()
                    )
                    self.create_tags_directory_and_sample_tag(
                        structure_analyzer.get_tags_path()
                    )
                    self.create_localization_files(
                        structure_analyzer.get_localization_dir_path(),
                        structure_analyzer.get_localization_file_path(),
                    )
                    self.create_stats_files(structure_analyzer.get_data_path())
                    self.create_item_combos_file(
                        structure_analyzer.get_generated_path()
                    )

                    if display_tree:
                        DisplayTree(mod_dir)

                    print(
                        f"Mod generated in {round(time.time() - start_time, 2)} seconds"
                    )

                return create_success
            except FileNotFoundError as not_found_err:
                self.logger.error(f"Error displaying tree: {not_found_err}")
                return False
            except FileExistsError as file_exists_err:
                self.logger.error(
                    f"create_structure: Directory exists: {file_exists_err}"
                )
                return False
            except Exception as unexpected_err:
                self.logger.error(
                    f"create_structure: Unexpected exception: {unexpected_err}"
                )
                print(traceback.format_exception(unexpected_err))
                return False
        else:
            return False
