import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from TreasureTableVerifier.root_template_parser import RootTemplateParser
from TreasureTableVerifier.xml_utils import attr_is_ignore_comment

logger = logging.getLogger(__name__)


def test_get_items_from_rt():
    """
    Parses RT XML and retrieves all items
    that don't have the comment to ignore.

    We don't want the template item
    """
    runes_xml: str = Path("tests/fixture/runes.lsx").read_text()

    assert runes_xml, "Failed to read XML file"

    parser = RootTemplateParser()
    root_node = ET.fromstring(runes_xml)

    assert root_node is not None, "Failed to get root node from XML"

    node_children = parser.get_unignored_nodes(root_node)

    assert len(node_children) > 0, "Failed to get template children"

    for node_child in node_children:
        attributes = node_child.findall("attribute")
        for attr_node in attributes:
            assert not attr_is_ignore_comment(
                attr_node
            ), "Found ignore comment in attr_node"
