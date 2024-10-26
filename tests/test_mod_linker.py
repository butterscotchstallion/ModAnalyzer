from ModAnalyzer.Structure import ModLinker


def test_create_symlinks():
    """
    1. Create Mod folder symlink: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Mods
    2. Create localization symlink: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Localization\\English
       - ModName.loca
       - ModName.xml
    3. Public folder: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3\\Data\\Public\\ModName
    """
    # game_dir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baldurs Gate 3"

    game_dir = "FakeGameFolder"
    mod_dir = "TestMod"
    mod_linker = ModLinker(game_dir)

    # FakeGameFolder/Data/Mods
    expected_symlink_path = f"{game_dir}\\Data\\Mods\\{mod_dir}"
    actual_symlink_path = mod_linker.get_mod_dir_symlink_path(mod_dir)
    assert expected_symlink_path == str(actual_symlink_path)

    linked_mod = mod_linker.link_mod(mod_dir)
    assert linked_mod, "Failed to link mod"
