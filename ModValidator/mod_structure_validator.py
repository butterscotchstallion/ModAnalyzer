import logging
import os
from pathlib import Path


class ModStructureValidator:
    """
    Verifies the directory structure of a
    mod.

    Verify the following directories
    1. Localization with at least one directory a one file inside
    2. ModDir/Mods/ModName
    3. ModDir/Mods/ModName/meta.lsx or meta.lsf.lsx
    4. ModDir/Mods/ModName/Public/RootTemplates/*.lsx
    5. ModDir/Mods/ModName/Public/Stats/
    6. ModDir/Mods/ModName/Public/Stats/Generated
    7. ModDir/Mods/ModName/Public/Stats/Generated/Data
    8. ModDir/Mods/ModName/Public/Stats/Generated/Equipment.txt
    9. ModDir/Mods/ModName/Public/Stats/Generated/TreasureTable.txt
    8. ModDir/Mods/ModName/Public/Tags

    Decide if structure is valid based on require directories
    """

    def __init__(self):
        self.logger = logging.getLogger(__file__)

    def verify(self, mod_name: str, mod_path: str) -> dict:
        """
        Main verification method containing various checks

        - Check each directory starting from the beginning
        - Do not perform additional checks if the first directories
        do not exist, because then we know others also do not exist
        """
        report = {
            # Directories
            "has_mods_modname": False,
            # Files
            "has_meta": False,
            "has_mod_fixer": False,
        }
        has_mods_modname = self.has_mods_modname(mod_name, mod_path)
        if not has_mods_modname:
            return report

        return report

    def get_mod_dirs(self, mod_dir: Path) -> list[Path]:
        return list(mod_dir.glob(os.path.join(mod_dir, "**", "*")))

    def dir_list_to_dict(self, directory_list: list[Path]) -> dict:
        dirs: dict = {}
        for item in directory_list:
            p = dirs
            for x in str(item).split(os.pathsep):
                p = p.setdefault(x, {})
        return dirs

    def get_mods_modname_path(self, mod_name: str, mod_path: str) -> str:
        return os.path.join(mod_path, "Mods", mod_name)

    def get_lsx_files_in_dir(self, directory: Path) -> list[Path]:
        return list(directory.glob("*.lsx")) + list(directory.glob("*.lsf.lsx"))

    def has_mods_modname(self, mod_name: str, mod_path: str) -> bool:
        return os.path.isdir(self.get_mods_modname_path(mod_name, mod_path))

    def has_public(self, mod_name: str, mod_path: str) -> bool:
        return False

    def has_meta(self, mod_name: str, mod_path: str) -> bool:
        mods_base_path = self.get_mods_modname_path(mod_name, mod_path)
        meta_exists = os.path.isfile(os.path.join(mods_base_path, "meta.lsx"))
        meta_mt_exists = os.path.isfile(os.path.join(mods_base_path, "meta.lsf.lsx"))
        if meta_exists:
            return True
        if meta_mt_exists:
            return True
        return False

    def has_root_templates(self) -> list[Path]:
        rts: list[Path] = []
        rt_dir = Path("ModDir/Mods/ModName/Public/RootTemplates/*.lsx")
        if os.path.isdir(rt_dir):
            rts = self.get_lsx_files_in_dir(rt_dir)
        return rts

    def has_mod_fixer(self) -> bool:
        return False
