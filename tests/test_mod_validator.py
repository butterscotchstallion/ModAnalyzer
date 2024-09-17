import json
import logging
import pprint
from pathlib import Path

import ModAnalyzer

logger = logging.getLogger(__file__)


def test_get_dirs():
    """
    Tests assembling of various dir paths
    """
    dirs = json.loads(Path("tests/fixture/dirs.json").read_text())
    validator = ModAnalyzer.ModAnalyzer()
    report = validator.validate("RunesOfFaerun", dirs)

    pprint.pp(report)

    assert report.has_meta_file, "No meta file detected"
    assert report.has_mods_modname, "No mod root dir"
    assert report.has_public, "No public dir"
    assert report.has_root_templates, "No root templates"
    # NYI
    assert not report.has_mod_fixer, "Has ModFixer?"
