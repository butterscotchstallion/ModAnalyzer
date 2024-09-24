import json
import logging
import traceback
from pathlib import Path
from uuid import UUID

from directory_tree import DisplayTree

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
                target_path_public = structure_analyzer.get_generated_path()
                # SE side
                target_path_server = se_analyzer.get_server_dir()

                # Check dirs exist
                public_path = Path(target_path_public)
                server_path = Path(target_path_server)

                public_path.mkdir(parents=True, exist_ok=False)
                server_path.mkdir(parents=True, exist_ok=False)

                create_success = public_path.exists() and server_path.exists()

                if create_success:
                    self.logger.debug("Main directories created")

                    self.create_meta(structure_analyzer.get_meta_path())
                    self.create_se_files(mod_dir, se_analyzer.get_config_path())
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
