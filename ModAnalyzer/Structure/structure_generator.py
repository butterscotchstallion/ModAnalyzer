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

    def create_structure(self, mod_dir: str, mod_uuid: UUID) -> bool:
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

                # os.makedirs(target_path_public, exist_ok=False)
                # os.makedirs(target_path_server, exist_ok=False)

                DisplayTree(mod_dir)

                # Check dirs exist
                public_path = Path(target_path_public)
                server_path = Path(target_path_server)

                public_path.mkdir(parents=True, exist_ok=False)
                server_path.mkdir(parents=True, exist_ok=False)

                create_success = public_path.exists() and server_path.exists()

                if create_success:
                    self.logger.debug("Main directories created")

                return create_success
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
