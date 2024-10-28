import logging
import os
import subprocess
from pathlib import Path


class ModLinker:
    """
    - Link mod dir
    - Link localization file
    - Link public
    """

    game_data_dir: Path
    game_data_path: Path

    def __init__(self, game_data_dir_override: str = ""):
        self.logger = logging.getLogger(__file__)
        self.game_data_dir = Path(
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3"
        )

        if game_data_dir_override:
            self.game_data_dir = Path(game_data_dir_override)

        game_data_path = Path(self.game_data_dir)

        if not game_data_path.is_dir():
            raise RuntimeError(f"{game_data_path} does not exist or is not a directory")

        self.game_data_path = game_data_path

    def _check_dir(self, dir_path: Path) -> Path | bool:
        if dir_path.is_dir():
            return dir_path
        else:
            self.logger.error(f"{dir_path} is not a directory or does not exist")
        return False

    def _check_file(self, file: str) -> Path | bool:
        file_path = Path(file)
        if file_path.is_file():
            return file_path
        else:
            self.logger.error(f"{file} is not a file or does not exist")
        return False

    def get_localization_files(self, mod_dir: str) -> list[str]:
        """TODO: maybe handle other languages"""
        loca_path = Path(os.path.join(mod_dir, "Localization", "English"))

        if not loca_path.is_dir():
            raise RuntimeError(f"{loca_path} does not exist or is not a directory")

        loca_files_pattern = os.path.join(loca_path, "*.xml")
        loca_files = loca_path.glob(loca_files_pattern)

        if not next(loca_files):
            self.logger.error(f"No localization files found in {loca_files_pattern}")

        return [str(file) for file in loca_files]

    ###
    ### Public methods
    ###

    def check_mod_dir(self, mod_dir: str) -> Path | bool:
        dir_without_ending_slash = mod_dir.rstrip("/")
        normalized_path = Path(dir_without_ending_slash)
        if "." in mod_dir:
            normalized_path = normalized_path.resolve()
            self.logger.debug(f"Resolving relative directory path to {normalized_path}")
        return self._check_dir(normalized_path)

    def check_localization_file(self, loca_file: str) -> Path | bool:
        normalized_path = Path(loca_file)
        if "." in loca_file:
            normalized_path = normalized_path.resolve()
            self.logger.debug(
                f"Resolving relative localization path to {normalized_path}"
            )
        return normalized_path if normalized_path.is_file() else False

    def check_public_dir(self, public_dir: str) -> Path | bool:
        return self._check_dir(Path(public_dir))

    def get_mod_dir_symlink_path(self, mod_dir: str) -> Path:
        """Assemble symlink path using data dir and mod name"""
        mod_name = self.get_mod_name_from_dir(mod_dir)
        return Path(os.path.join(self.game_data_dir, "Data", "Mods", mod_name))

    def get_mod_name_from_dir(self, mod_dir: str) -> str:
        return os.path.basename(os.path.normpath(mod_dir))

    def get_localization_filename(self, mod_name: str) -> str:
        return f"{mod_name}-English.xml"

    def get_loca_dir_symlink_path(self, mod_dir: str) -> Path:
        mod_name = self.get_mod_name_from_dir(mod_dir)
        return Path(
            os.path.join(
                self.game_data_dir,
                "Data",
                "Localization",
                "English",
                self.get_localization_filename(mod_name),
            )
        )

    def get_public_dir_symlink_path(self, mod_dir: str) -> Path:
        mod_name = self.get_mod_name_from_dir(mod_dir)
        return Path(
            os.path.join(
                self.game_data_dir,
                "Data",
                "Public",
                mod_name,
            )
        )

    def link(self, mod_dir: str, symlink_path: Path, is_dir: bool = True) -> bool:
        if is_dir:
            path_to_link = self.check_mod_dir(mod_dir)
            if not isinstance(path_to_link, Path):
                raise ValueError(f"{mod_dir} does not exist or is not a directory")
        else:
            path_to_link = self._check_file(mod_dir)
            if not isinstance(path_to_link, Path):
                raise ValueError(f"{mod_dir} does not exist or is not a file")

        try:
            self.logger.debug(
                f"Attempting to symlink (symlink path -> mod target path) {symlink_path} -> {path_to_link}"
            )

            if os.path.isjunction(symlink_path):
                self.logger.debug(f"Removing existing symlink: {symlink_path}")
                os.remove(symlink_path)

            # symlink_path.symlink_to(mod_path)
            # os.symlink(symlink_path, mod_path, target_is_directory=True)
            # /D requires elevation
            output = subprocess.check_output(
                f'mklink /J "{symlink_path}" "{path_to_link}"', shell=True
            )
            self.logger.debug(f"mklink output: {output.decode('utf-8')}")

            return os.path.isjunction(symlink_path)
        except subprocess.CalledProcessError as e:
            self.logger.debug(f"Subprocess error: {e}")
            return False
        except OSError as err:
            self.logger.error(f"link_mod_dir: Error creating symlink: {err}")
            return False
        except Exception as err:
            self.logger.error(f"link_mod_dir: Unexpected error: {err}")
            return False

    def link_mod_dir(self, mod_dir: str) -> bool:
        symlink_path = self.get_mod_dir_symlink_path(mod_dir)
        return self.link(mod_dir, symlink_path, True)

    def link_localization_file(self, mod_dir: str) -> bool:
        mod_name = self.get_mod_name_from_dir(mod_dir)
        localization_file = os.path.join(
            mod_dir, "Localization", "English", self.get_localization_filename(mod_name)
        )

        self.logger.debug(f"Loca path before resolve: {localization_file}")

        loca_path = self.check_localization_file(localization_file)
        if not loca_path:
            raise ValueError(
                f"link_localization_file: {localization_file} does not exist or is not a file"
            )

        symlink_path: Path = self.get_loca_dir_symlink_path(mod_dir)
        return self.link(localization_file, symlink_path, False)

    def link_public_dir(self, mod_dir: str) -> bool:
        mod_name = self.get_mod_name_from_dir(mod_dir)
        mod_public_dir = os.path.join(mod_dir, "Public", mod_name)
        mod_public_path = self.check_mod_dir(mod_public_dir)
        if not mod_public_path:
            raise ValueError(
                f"link_public_dir: {mod_public_dir} does not exist or is not a directory"
            )
        symlink_path: Path = self.get_public_dir_symlink_path(mod_name)
        return self.link(mod_public_dir, symlink_path, True)

    def link_mod(self, mod_dir: str) -> bool:
        """
        Links mod dirs/localization
        """

        # Mod dir
        linked_mod_dir_success = self.link_mod_dir(mod_dir)
        if linked_mod_dir_success:
            self.logger.info("Linked mod dir successfully")
        else:
            self.logger.error("Failed to link mod dir")

        # Public
        linked_public_dir_success = self.link_public_dir(mod_dir)
        if linked_public_dir_success:
            self.logger.info("Linked public dir successfully")
        else:
            self.logger.error("Failed to link public dir")

        # Localization
        linked_localization_file_success = self.link_localization_file(mod_dir)
        if linked_localization_file_success:
            self.logger.info("Linked localization file successfully")
        else:
            self.logger.error("Failed to link localization file")

        return (
            linked_mod_dir_success
            and linked_public_dir_success
            and linked_localization_file_success
        )

    def remove_link_if_exists(self, link_path: Path) -> bool:
        removed_link = False
        if link_path.is_junction():
            os.remove(link_path)
            if not link_path.is_junction():
                self.logger.info(f"Removed mod link: {link_path}")
                removed_link = True
        else:
            self.logger.error(f"remove_mod_links: {link_path} is not a junction")
        return removed_link

    def remove_mod_links(self, mod_dir: str) -> bool:
        # Mod dir
        mod_dir_link_path = self.get_mod_dir_symlink_path(mod_dir)
        removed_mod_dir_link = self.remove_link_if_exists(mod_dir_link_path)
        # Public dir
        public_dir_link_path = self.get_public_dir_symlink_path(mod_dir)
        removed_public_dir_link = self.remove_link_if_exists(public_dir_link_path)
        # Localization file
        localization_file_link_path = self.get_loca_dir_symlink_path(mod_dir)
        removed_localization_file_link = self.remove_link_if_exists(
            localization_file_link_path
        )
        return (
            removed_mod_dir_link
            and removed_public_dir_link
            and removed_localization_file_link
        )
