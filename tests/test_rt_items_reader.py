import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from ModAnalyzer.TreasureTable.root_template_parser import RootTemplateParser
from ModAnalyzer.TreasureTable.xml_utils import attr_is_ignore_comment
from tests.conftest import FIXTURE_PATHS

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def node_children():
    runes_xml: str = Path(FIXTURE_PATHS["ROOT_TEMPLATE"]).read_text()

    assert runes_xml, "Failed to read XML file"

    parser = RootTemplateParser()
    root_node = ET.fromstring(runes_xml)

    assert root_node is not None, "Failed to get root node from XML"

    node_summary = parser.get_verified_nodes(root_node)

    assert len(node_summary["verified"]) > 0, "Failed to get template children"

    return node_summary["verified"]


def test_get_items_from_rt(node_children: list[ET.Element]):
    """
    Parses RT XML and retrieves all items
    that don't have the comment to ignore.

    We don't want the template item
    """

    for node_child in node_children:
        attributes = node_child.findall("attribute")
        for attr_node in attributes:
            assert not attr_is_ignore_comment(
                attr_node
            ), "Found ignore comment in attr_node"


def test_get_stats_names_from_node_children(node_children: list[ET.Element]):
    parser = RootTemplateParser()
    stats_names = parser.get_stats_names_from_node_children(node_children)
    assert len(stats_names) == len(node_children), "Failed to get stats names"
