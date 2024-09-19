import logging

from ModAnalyzer import Structure

logger = logging.getLogger(__file__)


def test_get_dirs(mod_dirs_fixture: list[str]):
    """
    Tests assembling of various dir paths
    """
    analyzer = Structure.StructureAnalyzer()
    report = analyzer.generate_report("TestMod", mod_dirs_fixture)

    # pprint.pp(report)

    assert report.has_meta_file, "No meta file detected"
    assert report.has_mods_modname, "No mod root dir"
    assert report.has_public, "No public dir"
    assert report.has_root_templates, "No root templates"
    assert report.has_treasure_table, "No treasure table"
    # NYI
    assert not report.has_mod_fixer, "Has ModFixer?"
