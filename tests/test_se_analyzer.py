import os

from ModAnalyzer.ScriptExtender import SEAnalyzer
from ModAnalyzer.Structure import StructureAnalyzer


def test_generate_report(mod_dirs_fixture: list[str]):
    structure_analyzer = StructureAnalyzer(mod_dir_name="TestMod")
    se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)
    report = se_analyzer.generate_report(mod_dirs_fixture)

    assert report.has_se_dir, "No SE dir"
    assert report.has_config, "No SE config"
    assert not report.config_parse_error, "Config parse error detected"
    assert report.has_bootstrap_server, "No BootstrapServer.lua"
    assert not report.has_bootstrap_client, "No BootstrapClient.lua"

    # Dir tests
    se_base_path = se_analyzer.get_base_path()
    assert se_analyzer.get_config_path() == os.path.join(
        se_base_path, "Config.json"
    ), "SE config path mismatch"


def test_config_missing_fields():
    structure_analyzer = StructureAnalyzer(mod_dir_name="TestMod")
    se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)

    missing_fields = se_analyzer.get_missing_config_fields({})

    assert "RequiredVersion" in missing_fields
    assert "ModTable" in missing_fields
    assert "FeatureFlags" in missing_fields


def test_config_invalid_fields():
    structure_analyzer = StructureAnalyzer(mod_dir_name="TestMod")
    se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)

    invalid_config = {"RequiredVersion": "MEOW", "ModTable": "", "FeatureFlags": None}
    invalid_fields = se_analyzer.get_invalid_config_fields(invalid_config)

    assert "RequiredVersion" in invalid_fields
    assert "ModTable" in invalid_fields
    assert "FeatureFlags" in invalid_fields
