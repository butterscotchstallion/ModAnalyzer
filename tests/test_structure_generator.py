import logging
import shutil
import traceback
from pathlib import Path

import pytest

from ModAnalyzer import Structure
from ModAnalyzer.ScriptExtender import SEAnalyzer
from ModAnalyzer.ScriptExtender.se_analyzer import SEReport
from ModAnalyzer.Structure import StructureGenerator, StructureReport

logger = logging.getLogger(__file__)


def test_create_structure():
    generator = StructureGenerator(mod_name="TestMod")
    mod_uuid = generator.get_mod_uuid()
    mod_name = f"Generated_Test_Mod_{mod_uuid}"

    success = generator.create_structure(
        mod_name=mod_name,
        mod_dir=mod_name,
        mod_uuid=mod_uuid,
        display_tree=True,
        mod_author_name="Bruce Wayne",
        mod_description="I love tests!",
    )

    assert success, "Failed to generate structure"

    try:
        mod_name_path = Path(mod_name)
        if mod_name_path.exists():
            logger.debug("Generated mod structure")

            mod_dirs: list[str] = [str(d) for d in mod_name_path.glob("**/*")]

            # Analyze generated structure
            structure_analyzer = Structure.StructureAnalyzer()
            sa_report: StructureReport = structure_analyzer.generate_report(
                mod_name, mod_dirs
            )
            assert sa_report.has_meta_file, "No meta file detected"
            assert sa_report.has_mods_modname, "No mod root dir"
            assert sa_report.has_public, "No public dir"
            assert sa_report.has_root_templates, "No root templates"
            assert sa_report.has_treasure_table, "No treasure table"
            assert sa_report.has_tags, "No tags dir"

            logger.debug("Verified basic mod structure")

            # Analyze SE dir
            se_analyzer = SEAnalyzer(structure_analyzer=structure_analyzer)
            se_report: SEReport = se_analyzer.generate_report(mod_dirs)
            assert se_report.has_se_dir, "No SE dir"
            assert se_report.has_server_dir, "No server dir"
            assert se_report.has_bootstrap_server, "No bootstrap"
            assert se_report.has_bootstrap_client, "No client"
            assert se_report.has_config, "No config"
            assert not se_report.config_parse_error, "Config parse error"
            assert not se_report.config_invalid_fields, "Config invalid fields"
            logger.debug("Verified SE structure")

            logger.debug("Mod is fully validated :)")

            # Remove
            logger.debug(f"Attempting to remove mod dir: {mod_name}")
            shutil.rmtree(mod_name_path)
            assert not mod_name_path.exists(), "Failed to delete mod dir"

            logger.debug(f"Removed test mod dir {mod_name}")
        else:
            pytest.fail(f"Failed to create mod dir {mod_name}")
    except Exception as err:
        err_msg = f"Error deleting mod dir: {err}"
        logger.error(err_msg)
        pytest.fail(err_msg)
        print(traceback.format_exception(err))
