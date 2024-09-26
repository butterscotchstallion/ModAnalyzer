import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from ModAnalyzer.TreasureTable.models import ItemSummary

from .xml_utils import (
    attr_is_ignore_comment,
    get_comment_preserving_parser,
    get_error_message,
    get_tag_with_id_from_node,
)


class RootTemplateParser:
    """
    Handles parsing XML in root templates
    """

    def __init__(self):
        self.filename = ""
        self.tree: ET.ElementTree
        self.logger = logging.getLogger(__name__)

    def get_stats_names_from_node_children(
        self, node_children: list[ET.Element]
    ) -> set[str]:
        stats_names: set[str] = set()

        if node_children is not None:
            for node_child in node_children:
                attributes = node_child.findall("attribute")
                for attr_node in attributes:
                    if attr_node.attrib["id"] == "Stats":
                        stats_names.add(attr_node.attrib["value"])

        return stats_names

    def get_map_key_from_attributes(self, attrs: list[ET.Element]) -> str:
        """
        We have to go through all attributes and get the map key first, because
        we are using it as a key. There could be a scenario where the ignore attribute
        comes before the map key, and then we can't build the ignore map. Doing it this way
        means iterating the attributes twice, but it's not like this process is going to be
        running a lot. It's surely a better alternative to including an ignored node
        """
        map_key = ""

        try:
            for attr in attrs:
                if attr.attrib["id"] == "MapKey":
                    map_key = attr.attrib["value"]
                    break
        except Exception as err:
            self.logger.error(
                f"Unexpected error while trying to find map key for get_valid_nodes: {err}"
            )

        return map_key

    def get_verified_nodes(self, root: ET.Element) -> ItemSummary:
        """
        Gets templates children and filters nodes with a DevComment set to
        Ignore
        """
        verified_nodes: list[ET.Element] = []
        ignored_nodes_map: dict[str, bool] = {}
        ignored_nodes: list[ET.Element] = []
        node_children = self.get_templates_children(root)
        has_ignored_attr = False

        if node_children is not None:
            for node_child in node_children:
                has_ignored_attr = False
                attributes = node_child.findall("attribute")
                map_key = self.get_map_key_from_attributes(attributes)

                # Get ignored nodes
                for attr_node in attributes:
                    has_ignored_attr = attr_is_ignore_comment(attr_node)
                    if has_ignored_attr:
                        ignored_nodes_map[map_key] = True

                if map_key in ignored_nodes_map:
                    ignored_nodes.append(node_child)
                else:
                    verified_nodes.append(node_child)

        self.logger.info(f"Found {len(verified_nodes)} nodes in RT")

        return {"verified": verified_nodes, "ignored": ignored_nodes}

    def get_templates_children(self, root: ET.Element) -> ET.Element | None:
        # Get region#Templates
        templates_region = get_tag_with_id_from_node(root, "region", "Templates")
        if templates_region is not None:
            node = get_tag_with_id_from_node(templates_region, "node", "Templates")
            if node is not None:
                return node.find("children")

    def get_names_from_children(self, node_children: ET.Element) -> list[str]:
        """
        Need to get all the names at once from the entire node collection
        instead of iterating
        """
        existing_names: list[str] = []

        # Build name list from children
        all_nodes = node_children.findall("node")
        total_children = 0
        if all_nodes is not None:
            for node_child in node_children:
                # Don't try to parse comments
                if node_child.tag is ET.Comment:
                    continue

                total_children = total_children + 1
                attributes = node_child.findall("attribute")
                if attributes and len(attributes) > 0:
                    for attribute_tag in attributes:
                        if attribute_tag.attrib["id"] == "Name":
                            name_value = attribute_tag.attrib["value"]
                            existing_names.append(name_value)
                else:
                    self.logger.error(
                        "Unexpected XML format: no attributes found in node tag!"
                    )
                    break

            total_existing_names = len(existing_names)

            if total_existing_names != total_children:
                self.logger.error(
                    f"Total names doesn't match total children: {total_existing_names} != {total_children}!"
                )

            if total_existing_names > 0:
                self.logger.info(
                    f"There are {total_existing_names} existing names in the RT"
                )

        return existing_names

    def get_updated_children(self, filename: str, nodes: set) -> str | None:
        """
        Finds templates node, appends nodes, and returns
        updated structure.
        """
        new_node = None
        node_child = None
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError()

            parser = get_comment_preserving_parser()
            self.filename = filename
            self.tree = ET.parse(filename, parser)
            root = self.tree.getroot()
            """
            <region id="Templates">
		        <node id="Templates">
			        <children>
                        <node id="GameObjects">
            """
            node_children = self.get_templates_children(root)
            if node_children is not None:
                existing_names = self.get_names_from_children(node_children)

                # Iterate supplied nodes and append if not existent
                if existing_names is not None:
                    nodes_names_added: set[str] = set([])
                    for new_node in nodes:
                        if new_node.name not in existing_names:
                            if new_node.comment:
                                node_children.append(ET.Comment(new_node.comment))

                    self.logger.info(
                        f"{len(nodes_names_added)} root templates added to {Path(self.filename).stem}: {','.join(nodes_names_added)}"
                    )

                    ET.indent(self.tree, space="\t", level=0)
                    return ET.tostring(root, encoding="unicode")
                else:
                    if node_child is not None:
                        ET.dump(node_child)
                    self.logger.error("Found 0 existing names. This should not happen")
        except ET.ParseError as err:
            if new_node:
                err_msg = get_error_message(new_node.root_template_xml, err)
            else:
                err_msg = "unknown"
            self.logger.error(f"Failed to parse XML: {err_msg}")

    def write(self):
        if self.tree:
            self.tree.write(self.filename, "unicode", True)
