import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StructureReport:
    # Directories
    # TODO: rename this to root dir maybe?
    has_mods_modname: bool = False
    has_mod_fixer: bool = False
    has_public: bool = False
    # Files
    has_meta_file: bool = False
    has_root_templates: bool = False
    has_treasure_table: bool = False


class StructureAnalyzer:
    """
    Verifies the directory structure of a
    mod.

    Verify the following directories
    1. ModDir/Localization with at least one directory a one file inside
    2. ModDir/Mods/ModName
    3. ModDir/Mods/ModName/meta.lsx or meta.lsf.lsx
    4. ModDir/Mods/ModName/Public/RootTemplates/*.lsx
    5. ModDir/Mods/ModName/Public/Stats/
    6. ModDir/Mods/ModName/Public/Stats/Generated
    7. ModDir/Mods/ModName/Public/Stats/Generated/Data
    8. ModDir/Mods/ModName/Public/Stats/Generated/Equipment.txt
    9. ModDir/Mods/ModName/Public/Stats/Generated/TreasureTable.txt
    8. ModDir/Mods/ModName/Public/Tags

    Decide if structure is valid based on required directories. Glob
    tells us what is in the structure, so we do not have to perform lots
    of calls to exists
    """

    mod_dir_name: str

    def __init__(self):
        self.logger = logging.getLogger(__file__)
        self.mod_dir_name = ""

    def generate_report(
        self,
        mod_dir_name: str,
        mod_dirs_override: list[str] | None = None,
    ) -> StructureReport:
        """
        Main entry method containing various checks.

        - Use glob to get entire directory structure from supplied mod dir
        - Convert to list of strings
        - Early return upon finding the one we want
        - Check each directory starting from the beginning
        - Do not perform additional checks if the first directories
        do not exist, because then we know others also do not exist
        """
        self.mod_dir_name = mod_dir_name

        # Used in test
        if mod_dirs_override:
            if len(mod_dirs_override) == 0:
                raise ValueError(
                    "Empty mod dirs supplied to StructureAnalyzer.generate_report"
                )
            mod_dirs = mod_dirs_override
            for d in mod_dirs_override:
                if "Treasure" in d:
                    self.logger.info(f"mod_dirs tt path = {d}")
        else:
            mod_dirs_paths: list[Path] = self.get_mod_dirs(Path(mod_dir_name))
            mod_dirs: list[str] = [str(d) for d in mod_dirs_paths]

        report = StructureReport()
        report.has_mods_modname = self.has_mods_modname(mod_dirs)

        if not report.has_mods_modname:
            self.logger.info("No mod root dir!")
            return report

        self.logger.info("Mod root dir confirmed")

        # If they do not have the mod root dir, then they won't have this stuff either
        report.has_meta_file = self.has_meta(mod_dirs)
        report.has_public = self.has_public(mod_dirs)
        report.has_mod_fixer = self.has_mod_fixer(mod_dirs)
        report.has_root_templates = self.has_root_templates(mod_dirs)
        report.has_treasure_table = self.has_treasure_table(mod_dirs)

        return report

    def is_path_in_mod_dirs(self, mod_dirs: list[str], path: str) -> bool:
        return path in mod_dirs

    def get_lsx_files_in_dir(self, directory: Path) -> list[Path]:
        return list(directory.glob("*.lsx")) + list(directory.glob("*.lsf.lsx"))

    def get_mod_dirs(self, mod_dir: Path) -> list[Path]:
        """Used initially to create list of mod dirs"""
        return list(mod_dir.glob(os.path.join(mod_dir, "**", "*")))

    def get_mods_modname_path(self) -> str:
        return os.path.join(self.mod_dir_name, "Mods", self.mod_dir_name)

    def get_public_path(self) -> str:
        return os.path.join(self.mod_dir_name, "Public")

    def get_stats_path(self) -> str:
        dir_parts = [self.get_public_path(), self.mod_dir_name, "Stats"]
        return os.path.join(*dir_parts)

    def get_generated_path(self) -> str:
        return os.path.join(self.get_stats_path(), "Generated")

    def get_treasure_table_file_path(self) -> str:
        return os.path.join(self.get_generated_path(), "TreasureTable.txt")

    def get_rt_dir(self) -> str:
        rt_dir_parts = [self.get_public_path(), self.mod_dir_name, "RootTemplates"]
        return os.path.join(*rt_dir_parts)

    def get_rt_dir_path(self) -> Path:
        return Path(self.get_rt_dir())

    def get_root_templates(self) -> list[Path]:
        rts: list[Path] = []
        rt_dir = self.get_rt_dir_path()
        if os.path.isdir(rt_dir):
            self.logger.info("RootTemplates dir exists")
            rts = self.get_lsx_files_in_dir(rt_dir)
            self.logger.info(f"LSX files in RT dir: {rts}")
        else:
            self.logger.info(f"RT dir does not exist: {rt_dir}")
        return rts

    def get_goals_path_parts(self) -> list[str]:
        return [self.get_mods_modname_path(), "Story", "RawFiles", "Goals"]

    #################################
    # Directory checks              #
    #################################

    def has_treasure_table(self, mod_dirs: list[str]) -> bool:
        tt_path = self.get_treasure_table_file_path()
        return self.is_path_in_mod_dirs(mod_dirs, tt_path)

    def has_mods_modname(self, mod_dirs: list[str]) -> bool:
        path = self.get_mods_modname_path()
        return self.is_path_in_mod_dirs(mod_dirs, path)

    def has_public(self, mod_dirs: list[str]) -> bool:
        public_path = self.get_public_path()
        return self.is_path_in_mod_dirs(mod_dirs, public_path)

    def has_localization(self, mod_dirs: list[str]) -> bool:
        return self.is_path_in_mod_dirs(mod_dirs, self.mod_dir_name)

    def has_meta(self, mod_dirs: list[str]) -> bool:
        mods_base_path = self.get_mods_modname_path()
        meta_path = os.path.join(mods_base_path, "meta.lsx")
        meta_mt_path = os.path.join(mods_base_path, "meta.lsf.lsx")

        # Maybe glob this
        meta_exists = self.is_path_in_mod_dirs(mod_dirs, meta_path)
        meta_mt_exists = self.is_path_in_mod_dirs(mod_dirs, meta_mt_path)

        return meta_exists or meta_mt_exists

    def has_root_templates(self, mod_dirs: list[str]) -> bool:
        rt_path_parts = [self.get_public_path(), self.mod_dir_name, "RootTemplates"]
        rt_dir = os.path.join(*rt_path_parts)
        has_rt_dir = self.is_path_in_mod_dirs(mod_dirs, rt_dir)

        if has_rt_dir:
            for mod_dir in mod_dirs:
                if mod_dir.startswith(rt_dir) and mod_dir.endswith(".lsx"):
                    return True

        return False

    def has_goals(self, mod_dirs: list[str]) -> bool:
        goals_path_parts = self.get_goals_path_parts()
        return self.is_path_in_mod_dirs(mod_dirs, *goals_path_parts)

    #################################
    # Other checks                  #
    #################################

    def has_mod_fixer(self, mod_dirs: list[str]) -> bool:
        """
        This needs to be more nuanced than checking for files
        in the Goals directory
        """

        """
        if self.has_goals(mod_dirs):
            goals_path_parts = self.get_goals_path_parts()
            goals_path_parts.append("ForceRecompile.txt")
            mod_fixer_path = os.path.join(*goals_path_parts)
        """
        return False
