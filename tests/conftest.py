import json
import logging
from pathlib import Path

import pytest

logger = logging.getLogger(__file__)


@pytest.fixture(autouse=True, scope="session")
def mod_dirs_fixture():
    logger.info("Loading mod dirs fixture")
    # lines = Path("tests/fixture/dirs.txt").read_text().splitlines()
    # return [line.strip() for line in lines if line]
    return json.loads(Path("tests/fixture/dirs.json").read_text())


FIXTURE_PATHS = {
    "TREASURE_TABLE": "TestMod/Public/TestMod/Stats/Generated/TreasureTable.txt",
    "ROOT_TEMPLATE": "TestMod/Public/TestMod/RootTemplates/runes.lsx",
}
