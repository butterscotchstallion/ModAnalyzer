from ModAnalyzer.Structure import ModLinker


def test_create_symlinks():
    """
    1. Create Mod folder symlink: C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data\Mods
    2. Create localization symlink: C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data\Localization\English\
       - ModName.loca
       - ModName.xml
    3. Public folder: C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3\Data\Public\ModName
    """
    game_dir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3"
    mod_linker = ModLinker(game_dir)

    mod_dir_linked = mod_linker.link_mod_dir()

    assert mod_dir_linked, "Failed to link mod dir"
