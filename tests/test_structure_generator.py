import logging
import shutil
import uuid
from pathlib import Path

import pytest

from ModAnalyzer.Structure import StructureGenerator

logger = logging.getLogger(__file__)


def test_create_structure():
    generator = StructureGenerator(mod_name="TestMod")
    mod_uuid = uuid.uuid4()
    mod_name = f"Generated_Test_Mod_{mod_uuid}"

    success = generator.create_structure(
        mod_name=mod_name,
        mod_dir=mod_name,
        mod_uuid=uuid.uuid4(),
        display_tree=True,
        mod_author_name="Bruce Wayne",
        mod_description="I love tests!",
    )

    assert success, "Failed to generate structure"

    try:
        mod_name_path = Path(mod_name)
        if mod_name_path.exists():
            shutil.rmtree(mod_name)

            assert not mod_name_path.exists(), "Failed to delete mod dir"
        else:
            pytest.fail(f"Failed to create mod dir {mod_name}")
    except Exception as err:
        err_msg = f"Error deleting mod dir: {err}"
        logger.error(err_msg)
        pytest.fail(err_msg)

    logger.debug(f"Removed test mod dir {mod_name}")
