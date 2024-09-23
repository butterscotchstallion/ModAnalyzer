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
