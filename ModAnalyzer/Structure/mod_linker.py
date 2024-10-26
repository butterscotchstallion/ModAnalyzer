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

    game_data_dir: str
    game_data_path: Path

    def __init__(self, game_data_dir_override: str = ""):
        self.logger = logging.getLogger(__file__)
        self.game_data_dir = (
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3"
        )

        if game_data_dir_override:
            self.game_data_dir = game_data_dir_override

        game_data_path = Path(self.game_data_dir)

        if not game_data_path.is_dir():
            raise RuntimeError(f"{game_data_path} does not exist or is not a directory")

        self.game_data_path = game_data_path

    def _check_dir(self, directory: str) -> Path | bool:
        dir_path = Path(directory)
        if dir_path.is_dir():
            return dir_path
        return False

    def _check_file(self, file: str) -> Path | bool:
        file_path = Path(file)
        if file_path.is_file():
            return file_path
        return False

    def get_localization_files(self, mod_dir: str) -> list[str]:
        """TODO: maybe handle other languages"""
        loca_path = Path(f"{mod_dir}\\Localization\\English")

        if not loca_path.is_dir():
            raise RuntimeError(f"{loca_path} does not exist or is not a directory")

        loca_files_pattern = os.path.join(loca_path, "*.xml")
        loca_files = loca_path.glob(loca_files_pattern)

        if len(loca_files) == 0:
            self.logger.error(f"No localization files found in {loca_files_pattern}")

        return [str(file) for file in loca_files]

    ###
    ### Public methods
    ###

    def check_mod_dir(self, mod_dir: str) -> Path | bool:
        return self._check_dir(mod_dir)

    def check_localization_file(self, loca_file: str) -> bool:
        return Path(loca_file).is_file()

    def check_public_dir(self, public_dir: str) -> Path | bool:
        return self._check_dir(public_dir)

    def get_mod_dir_symlink_path(self, mod_name: str) -> Path:
        """Assemble symlink path using data dir and mod name"""
        return Path(os.path.join(self.game_data_dir, "Data", "Mods", mod_name))

    def get_loca_dir_symlink_path(self, mod_name: str) -> Path:
        return Path(
            os.path.join(
                self.game_data_dir,
                "Data",
                "Localization",
                "English",
                f"{mod_name}",
            )
        )

    def get_public_dir_symlink_path(self) -> Path:
        return Path(os.path.join(self.game_data_dir, "Public"))

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
        except OSError as err:
            self.logger.error(f"link_mod_dir: Error creating symlink: {err}")
            return False
        except Exception as err:
            self.logger.error(f"link_mod_dir: Unexpected error: {err}")
            return False

    def link_mod_dir(self, mod_dir: str) -> bool:
        mod_name = os.path.basename(os.path.normpath(mod_dir))
        symlink_path = self.get_mod_dir_symlink_path(mod_name)
        return self.link(mod_dir, symlink_path, True)

    def link_localization_file(self, mod_dir: str) -> bool:
        localization_file = f"{mod_dir}\\Localization\\English\\{mod_dir}-English.xml"
        loca_path = self.check_localization_file(localization_file)
        if not loca_path:
            raise ValueError(f"{loca_path} does not exist or is not a file")
        mod_name = os.path.basename(localization_file)
        symlink_path: Path = self.get_loca_dir_symlink_path(mod_name)
        return self.link(localization_file, symlink_path, False)

    def link_public_dir(self, mod_dir: str) -> bool:
        public_dir = f"{mod_dir}\\Public"
        public_path = self.check_mod_dir(public_dir)
        if not public_path:
            raise ValueError(f"{public_path} does not exist or is not a directory")
        symlink_path: Path = self.get_public_dir_symlink_path()
        return self.link(public_dir, symlink_path, True)

    def link_mod(self, mod_dir: str) -> bool:
        """
        Links mod dirs/localization
        """
        linked_mod_dir_success = self.link_mod_dir(mod_dir)
        if linked_mod_dir_success:
            self.logger.info("Linked mod dir successfully")
        else:
            self.logger.error("Failed to link mod dir")

        linked_public_dir_success = self.link_public_dir(mod_dir)
        if linked_public_dir_success:
            self.logger.info("Linked public dir successfully")
        else:
            self.logger.error("Failed to link public dir")

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
