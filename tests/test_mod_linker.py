import os

from ModAnalyzer.Structure import ModLinker


def test_create_symlinks():
    """
    1. Create Mod folder symlink: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Mods
    2. Create localization symlink: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Localization\\English
       - ModName.loca
       - ModName.xml
    3. Public folder: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Public\\ModName
    """
    game_dir = "FakeGameFolder"
    mod_dir = os.path.join("..", "..", "Mods", "FaerunForAll-BG3Mod", "FaerunForAll")
    mod_linker = ModLinker(game_dir)

    linked_mod = mod_linker.link_mod(mod_dir)
    assert linked_mod, "Failed to link mod"
