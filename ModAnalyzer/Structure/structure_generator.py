import json
import logging
import os
import traceback
import uuid
from pathlib import Path
from uuid import UUID

from directory_tree import DisplayTree
from jinja2 import Environment, FileSystemLoader

from ModAnalyzer.ScriptExtender import SEAnalyzer
from ModAnalyzer.Structure import StructureAnalyzer


class StructureGenerator:
    """
    Creates basic mod structure
    """

    def __init__(self):
        self.logger = logging.getLogger(__file__)

    def create_meta(self, meta_path: str) -> bool:
        path = Path(meta_path)
        path.touch(exist_ok=False)
        created = path.exists()

        if created:
            self.logger.debug(f"Created meta: {meta_path}")
        else:
            self.logger.error(f"Error creating meta: {meta_path}")

        return created

    def create_se_files(self, mod_name: str, config_path: str) -> bool:
        try:
            config_file_path = Path(config_path)
            if not config_file_path.exists():
                config_file_path.touch(exist_ok=False)
                exists = config_file_path.exists()

                if exists:
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

                    return True
                else:
                    return False
            else:
                self.logger.error(f"create_se_files: {config_file_path} exists")
                return False
        except Exception as err:
            self.logger.error(f"create_se_files: Unexpected error: {err}")
            return False

    def create_root_templates(self, rt_dir: str):
        pass

    def create_treasure_table(self, tt_file_path: str) -> bool:
        try:
            tt_path = Path(tt_file_path)

            if not tt_path.exists():
                tt_path.touch()
                return tt_path.exists()
            else:
                self.logger.error(f"Treasure table exists at {tt_file_path}")
                return False
        except Exception as err:
            self.logger.error(f"Unexpected error creating treasure table: {err}")
            return False

    def create_equipment_file(self, equipment_path: str) -> bool:
        try:
            equip_path = Path(equipment_path)

            if not equip_path.exists():
                equip_path.touch()
                return equip_path.exists()
            else:
                self.logger.error(f"Equipment file exists at {equip_path}")
                return False
        except Exception as err:
            self.logger.error(f"Unexpected error creating equipment file: {err}")
            return False

    def get_template_with_replacements(
        self, replacements: dict, tpl_filename: str
    ) -> str:
        try:
            tpl_dir = os.path.join(*["ModAnalyzer", "Structure", "file_templates"])
            dir_path = Path(tpl_dir)
            tpl_path = Path(os.path.join(tpl_dir, tpl_filename))
            is_dir_valid = dir_path.exists() and dir_path.is_dir()
            is_tpl_valid = tpl_path.exists() and tpl_path.is_file()
            if is_dir_valid and is_tpl_valid:
                environment = Environment(loader=FileSystemLoader(tpl_dir))
                template = environment.get_template(tpl_filename)
                return template.render(**replacements)
            else:
                self.logger.error(f"Template directory {tpl_dir} does not exist")
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
                    "MA_TAG_ICON_NAME": "icon name",
                    "MA_TAG_NAME": "Tag Name",
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
        except Exception:
            self.logger.error(f"Unexpected error creating tags dir: {path}")
            return False

    def create_stats_files(self):
        """
        Creates a few stats files as an example
        - Status.txt
        - Passive.txt
        - Target.txt
        - Projectile.txt
        """
        pass

    def create_localization_files(self):
        """
        Create normal folder/file and the one for books
        """
        pass

    def create_structure(
        self, mod_dir: str, mod_uuid: UUID, display_tree=False
    ) -> bool:
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
        base_mod_dir_path = Path(mod_dir)

        if not base_mod_dir_path.exists():
            try:
                self.logger.info(f"Creating {mod_dir}")

                structure_analyzer = StructureAnalyzer(mod_dir_name=mod_dir)
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

                    self.create_meta(structure_analyzer.get_meta_path())
                    self.create_se_files(mod_dir, se_analyzer.get_config_path())
                    self.create_root_templates(structure_analyzer.get_rt_dir())
                    self.create_treasure_table(
                        structure_analyzer.get_treasure_table_file_path()
                    )
                    self.create_equipment_file(
                        structure_analyzer.get_equipment_file_path()
                    )
                    self.create_tags_directory_and_sample_tag(
                        structure_analyzer.get_tags_path()
                    )
                    self.create_localization_files()
                    self.create_stats_files()

                    if display_tree:
                        DisplayTree(mod_dir)

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
