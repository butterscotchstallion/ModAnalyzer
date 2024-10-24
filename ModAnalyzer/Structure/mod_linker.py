import logging
import os
from pathlib import Path


class ModLinker:
    """
    - Link mod dir
    - Link localization file
    - Link public
    """

    game_data_dir: str
    game_data_path: Path

    def __init__(self, game_data_dir: str):
        self.logger = logging.getLogger(__file__)
        self.game_data_dir = game_data_dir

        game_data_path = Path(self.game_data_dir)

        if not game_data_path.is_dir():
            raise RuntimeError(f"{game_data_dir} does not exist or is not a directory")

        self.game_data_path = game_data_path

    def _check_dir(self, dir: str) -> Path | bool:
        dir_path = Path(dir)
        if dir_path.is_dir():
            return dir_path
        return False

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
        paths: list[str] = [self.game_data_dir, "Mods", mod_name]
        return Path(os.path.join(*paths))

    def get_loca_dir_symlink_path(self, mod_name: str) -> Path:
        paths: list[str] = [
            self.game_data_dir,
            "Localization",
            "English",
            f"{mod_name}.xml",
        ]
        return Path(os.path.join(*paths))

    def get_public_dir_symlink_path(self) -> Path:
        paths: list[str] = [self.game_data_dir, "Mods", "Public"]
        return Path(os.path.join(*paths))

    def link_mod_dir(self, mod_dir: str) -> bool:
        mod_path = self.check_mod_dir(mod_dir)
        if not mod_path:
            raise ValueError(f"{mod_dir} does not exist or is not a directory")

        self.logger.debug(f"{mod_path} is a directory")

        try:
            mod_name = os.path.normpath(mod_dir)
            symlink_path = self.get_mod_dir_symlink_path(mod_name)

            self.logger.debug(
                f"Attempting to symlink (symlink path -> mod target path) {symlink_path} -> {mod_path}"
            )

            symlink_path.touch()
            symlink_path.symlink_to(str(mod_path), target_is_directory=True)

            return symlink_path.is_symlink()
        except OSError as err:
            self.logger.error(f"link_mod_dir: Error creating symlink: {err}")
            return False
        except Exception as err:
            self.logger.error(f"link_mod_dir: Unexpected error: {err}")
            return False

    def link_localization_file(self, localization_file: str) -> bool:
        loca_path = self.check_localization_file(localization_file)
        if not loca_path:
            raise ValueError(f"{loca_path} does not exist or is not a file")

    def link_public_dir(self, public_dir: str) -> bool:
        public_path = self.check_mod_dir(public_dir)
        if not public_path:
            raise ValueError(f"{public_path} does not exist or is not a directory")
