import logging
import os

from ModAnalyzer import Structure

logger = logging.getLogger(__file__)
TEST_MOD_NAME = "TestMod"


def test_get_dirs(mod_dirs_fixture: list[str]):
    """
    Tests assembling of various dir paths
    """
    analyzer = Structure.StructureAnalyzer()
    report = analyzer.generate_report(TEST_MOD_NAME, mod_dirs_fixture)

    # pprint.pp(report)
    assert analyzer.get_public_path() == os.path.join(
        TEST_MOD_NAME, "Public"
    ), "Public path incorrect"

    stats_path = os.path.join(TEST_MOD_NAME, "Public", TEST_MOD_NAME, "Stats")
    assert analyzer.get_stats_path() == stats_path, "Stats path is incorrect"

    # TestMod\Public\TestMod\RootTemplates
    assert analyzer.get_rt_dir() == os.path.join(
        TEST_MOD_NAME, "Public", TEST_MOD_NAME, "RootTemplates"
    ), "Root templates path is incorrect"

    assert analyzer.get_generated_path() == os.path.join(
        stats_path, "Generated"
    ), "Generated path is incorrect"

    # has_ tests
    assert report.has_meta_file, "No meta file detected"
    assert report.has_mods_modname, "No mod root dir"
    assert report.has_public, "No public dir"
    assert report.has_root_templates, "No root templates"
    assert report.has_treasure_table, "No treasure table"
    # NYI
    assert not report.has_mod_fixer, "Has ModFixer?"
