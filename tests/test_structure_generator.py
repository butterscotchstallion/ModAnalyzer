import logging
import os
import uuid

from ModAnalyzer.Structure import StructureGenerator

logger = logging.getLogger(__file__)


def test_generate_structure():
    generator = StructureGenerator()
    mod_uuid = uuid.uuid4()
    mod_name = f"Generated_Test_Mod_{mod_uuid}"

    success = generator.create_structure(mod_name, mod_uuid)

    assert success, "Failed to generate structure"

    os.remove(mod_name)

    logger.debug(f"Removed test mod dir {mod_name}")
