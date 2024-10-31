import logging
import os
from pathlib import Path

from ModAnalyzer import Structure
from ModAnalyzer.Structure.models import Tag

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


def test_get_tags_from_file():
    """Parses tag file XML and returns each tag as an object"""
    analyzer = Structure.StructureAnalyzer()
    tag_file_contents = Path(os.path.join("tests", "fixture", "tag.lsx")).read_text()
    tags: list[Tag] = analyzer.get_tags_from_file_contents(tag_file_contents)

    assert tags
    assert len(tags) == 1

    tag = tags[0]
    assert tag.uuid == "4b8dbf5b-68d8-4c1e-80c2-b68ce13a82c8"
    assert tag.name == "TEST_MOD_TAG"
    assert tag.description == "test description"
    assert tag.display_name == "ha59594e8g8544g4bbdg82ddge6c19ba2bc6d"
    assert tag.display_description == "h6c83d504g5aa4g42abga0e7g770c9d830753"
    assert tag.icon == "icon"
    assert tag.categories == ["Code", "CharacterSheet"]
