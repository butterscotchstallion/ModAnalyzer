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
        paths = [self.game_data_dir, "Mods", mod_name]

        dest_path = Path(os.path.join(paths.pop()))
        if not dest_path.is_dir():
            dest_path.mkdir()

        return Path(os.path.join(*paths))

    def get_loca_dir_symlink_path(self, mod_name: str) -> Path:
        paths = [self.game_data_dir, "Localization", "English", f"{mod_name}.xml"]
        return Path(os.path.join(*paths))

    def get_public_dir_symlink_path(self) -> Path:
        paths = [self.game_data_dir, "Mods", "Public"]
        return Path(os.path.join(*paths))

    def link_mod_dir(self, mod_dir: str) -> bool:
        mod_path = self.check_mod_dir(mod_dir)
        if not mod_path:
            raise ValueError(f"{mod_dir} does not exist or is not a directory")

        mod_name = os.path.normpath(mod_dir)
        symlink_path = self.get_mod_dir_symlink_path(mod_name)
        target_path = Path()

        symlink_path.symlink_to(target_path, target_is_directory=True)

        return target_path.is_symlink()

    def link_localization_file(self, localization_file: str) -> bool:
        pass

    def link_public_dir(self, public_dir: str) -> bool:
        pass
