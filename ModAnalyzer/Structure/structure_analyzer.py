import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from ModAnalyzer.Structure.models import Tag
from ModAnalyzer.Structure.path_analyzer import PathAnalyzer
from ModAnalyzer.Structure.xml_utils import get_tag_with_id_from_node


@dataclass
class StructureReport:
    # Directories
    # TODO: rename this to root dir maybe?
    mod_dir_exists: bool = False
    mod_dir_is_dir: bool = False
    has_mods_modname: bool = False
    has_public: bool = False
    has_tags: bool = False
    # Files
    has_meta_file: bool = False
    has_root_templates: bool = False
    has_treasure_table: bool = False


class StructureAnalyzer:
    """
    Verifies the directory structure of a
    mod.

    Verify the following directories
    1. ModDir/Localization with at least one directory a one file inside
    2. ModDir/Mods/ModName
    3. ModDir/Mods/ModName/meta.lsx or meta.lsf.lsx
    4. ModDir/Mods/ModName/Public/RootTemplates/*.lsx
    5. ModDir/Mods/ModName/Public/Stats/
    6. ModDir/Mods/ModName/Public/Stats/Generated
    7. ModDir/Mods/ModName/Public/Stats/Generated/Data
    8. ModDir/Mods/ModName/Public/Stats/Generated/Equipment.txt
    9. ModDir/Mods/ModName/Public/Stats/Generated/TreasureTable.txt
    8. ModDir/Mods/ModName/Public/Tags

    Decide if structure is valid based on required directories. Glob
    tells us what is in the structure, so we do not have to perform lots
    of calls to exists
    """

    mod_dir_name: str = ""
    mod_name: str = ""
    mod_dirs: list[str] = []

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__file__)
        self.mod_dir_name = ""
        self.path_analyzer = PathAnalyzer()

        if "mod_dir_name" in kwargs:
            self.mod_dir_name = self.get_mod_dir_without_dir_seps(
                kwargs["mod_dir_name"]
            )

        self.mod_name = self.mod_dir_name
        if "mod_name" in kwargs:
            self.mod_name = kwargs["mod_name"]

    def get_mod_dir_without_dir_seps(self, mod_dir_name: str) -> str:
        mod_name = mod_dir_name.rstrip(os.sep)
        mod_name = mod_name.rstrip("/")
        return mod_name

    def generate_report(
        self,
        mod_dir_name: str,
        mod_dirs_override: list[str] | None = None,
    ) -> StructureReport:
        """
        Main entry method containing various checks.

        - Use glob to get entire directory structure from supplied mod dir
        - Convert to list of strings
        - Early return upon finding the one we want
        - Check each directory starting from the beginning
        - Do not perform additional checks if the first directories
        do not exist, because then we know others also do not exist
        """
        report = StructureReport()

        self.mod_dir_name = self.get_mod_dir_without_dir_seps(mod_dir_name)

        # Check exists
        report.mod_dir_exists = os.path.exists(self.mod_dir_name)
        if not report.mod_dir_exists:
            self.logger.error(f"{self.mod_dir_name} does not exist")
            return report

        # Check is dir
        report.mod_dir_is_dir = os.path.isdir(self.mod_dir_name)
        if not report.mod_dir_is_dir:
            self.logger.error(f"{self.mod_dir_name} is not a directory")
            return report

        # Used in test
        if mod_dirs_override:
            self.logger.debug("Using mod_dirs_override")
            if len(mod_dirs_override) == 0:
                raise ValueError(
                    "Empty mod dirs supplied to StructureAnalyzer.generate_report"
                )
            self.mod_dirs = mod_dirs_override
            for d in mod_dirs_override:
                if "Treasure" in d:
                    self.logger.debug(f"mod_dirs tt path = {d}")
        else:
            self.logger.debug("Determining mod dirs path")
            mod_dirs_paths: list[Path] = self.get_mod_dirs(Path(mod_dir_name))
            self.mod_dirs: list[str] = [str(d) for d in mod_dirs_paths]

        report.has_mods_modname = self.has_mods_modname(self.mod_dirs)

        if not report.has_mods_modname:
            self.logger.info("No mod root dir!")
            return report

        # If they do not have the mod root dir, then they won't have this stuff either
        report.has_meta_file = self.has_meta(self.mod_dirs)
        report.has_public = self.has_public(self.mod_dirs)
        report.has_root_templates = self.has_root_templates(self.mod_dirs)
        report.has_treasure_table = self.has_treasure_table(self.mod_dirs)
        report.has_tags = self.has_tags(self.mod_dirs)

        return report

    def is_path_in_mod_dirs(self, mod_dirs: list[str], path: str) -> bool:
        return path in mod_dirs

    def get_lsx_files_in_dir(self, directory: Path) -> list[Path]:
        # TODO: check if extension needs to be case sensitive
        lsx_files = []
        try:
            lsf_lsx_files = list(directory.glob("*.lsf.lsx"))
            lsx_files = (
                list(directory.glob("*.lsx", case_sensitive=False)) + lsf_lsx_files
            )
        except Exception as err:
            self.logger.error(f"Unexpected error in get_lsx_files_in_dir: {err}")
        finally:
            return lsx_files

    def get_mod_dirs(self, mod_dir: Path) -> list[Path]:
        """Used initially to create list of mod dirs"""
        return list(mod_dir.glob("**\\*"))

    def get_mods_modname_path(self) -> str:
        if not self.mod_dir_name:
            raise ValueError("Mod dir name is empty")
        return os.path.join(self.mod_dir_name, "Mods", self.mod_dir_name)

    def get_public_path(self) -> str:
        if not self.mod_dir_name:
            raise ValueError("Mod dir name is empty")
        return os.path.join(self.mod_dir_name, "Public")

    def get_stats_path(self) -> str:
        if not self.mod_dir_name:
            raise ValueError("Mod dir name is empty")
        return os.path.join(self.get_public_path(), self.mod_dir_name, "Stats")

    def get_generated_path(self) -> str:
        return os.path.join(self.get_stats_path(), "Generated")

    def get_data_path(self) -> str:
        return os.path.join(self.get_generated_path(), "Data")

    def get_treasure_table_file_path(self) -> str:
        return os.path.join(self.get_generated_path(), "TreasureTable.txt")

    def get_equipment_file_path(self) -> str:
        return os.path.join(self.get_generated_path(), "Equipment.txt")

    def get_tags_path(self) -> str:
        return os.path.join(self.get_public_path(), self.mod_dir_name, "Tags")

    def get_localization_dir_path(self) -> str:
        return os.path.join(*[self.mod_dir_name, "Localization", "English"])

    def get_localization_file_path(self) -> str:
        if not self.mod_name:
            raise ValueError("mod_name is empty!")
        mod_name_with_lang = f"{self.mod_name}-English.xml"
        return os.path.join(self.get_localization_dir_path(), mod_name_with_lang)

    # RunesOfFaerun\Public\RunesOfFaerun\RootTemplates
    def get_rt_dir(self) -> str:
        return os.path.join(self.get_public_path(), self.mod_dir_name, "RootTemplates")

    def get_rt_dir_path(self) -> Path:
        return Path(self.get_rt_dir())

    def get_root_templates(self) -> list[Path]:
        rts: list[Path] = []
        rt_dir = self.get_rt_dir_path()
        if os.path.isdir(rt_dir):
            self.logger.info("RootTemplates dir exists")
            rts = self.get_lsx_files_in_dir(rt_dir)
            self.logger.info(f"LSX files in RT dir: {rts}")
        else:
            self.logger.info(f"RT dir does not exist: {rt_dir}")
        return rts

    def get_goals_path_parts(self) -> list[str]:
        return [self.get_mods_modname_path(), "Story", "RawFiles", "Goals"]

    #################################
    # Directory checks              #
    #################################

    def has_treasure_table(self, mod_dirs: list[str]) -> bool:
        tt_path = self.get_treasure_table_file_path()
        return self.is_path_in_mod_dirs(mod_dirs, tt_path)

    def has_mods_modname(self, mod_dirs: list[str]) -> bool:
        path = self.get_mods_modname_path()
        return self.is_path_in_mod_dirs(mod_dirs, path)

    def has_public(self, mod_dirs: list[str]) -> bool:
        public_path = self.get_public_path()
        return self.is_path_in_mod_dirs(mod_dirs, public_path)

    def has_localization(self, mod_dirs: list[str]) -> bool:
        return self.is_path_in_mod_dirs(mod_dirs, self.mod_dir_name)

    @staticmethod
    def get_mod_name_from_dir(mod_dir: str) -> str:
        return os.path.basename(os.path.normpath(mod_dir))

    def get_meta_path(self) -> str:
        return os.path.join(self.get_mods_modname_path(), "meta.lsx")

    def get_mt_meta_path(self) -> str:
        return os.path.join(self.get_mods_modname_path(), "meta.lsf.lsx")

    def has_meta(self, mod_dirs: list[str]) -> bool:
        """This file does not need to be converted"""
        meta_path = self.get_meta_path()
        meta_mt_path = self.get_mt_meta_path()

        # Maybe glob this
        meta_exists = self.is_path_in_mod_dirs(mod_dirs, meta_path)
        meta_mt_exists = self.is_path_in_mod_dirs(mod_dirs, meta_mt_path)

        return meta_exists or meta_mt_exists

    def has_root_templates(self, mod_dirs: list[str]) -> bool:
        rt_dir = os.path.join(
            self.get_public_path(), self.mod_dir_name, "RootTemplates"
        )
        has_rt_dir = self.is_path_in_mod_dirs(mod_dirs, rt_dir)

        if has_rt_dir:
            for mod_dir in mod_dirs:
                if mod_dir.startswith(rt_dir) and mod_dir.endswith(".lsx"):
                    return True

        return False

    def has_goals(self, mod_dirs: list[str]) -> bool:
        goals_path_parts = self.get_goals_path_parts()
        return self.is_path_in_mod_dirs(mod_dirs, *goals_path_parts)

    def has_tags(self, mod_dirs) -> bool:
        tags_path = self.get_tags_path()
        return self.is_path_in_mod_dirs(mod_dirs, tags_path)

    def get_categories_from_children_node(self, children_node: ET.Element) -> list[str]:
        """
        <children>
            <node id="Categories">
                <children>
                    <node id="Category">
                        <attribute id="Name" type="LSString" value="Code"/>
                    </node>
                    <node id="Category">
                        <attribute id="Name" type="LSString" value="CharacterSheet"/>
                    </node>
                </children>
            </node>
        </children>
        """
        categories: list[str] = []
        categories_node = children_node.find("node")
        if categories_node is not None:
            categories_node_children = categories_node.find("children")
            if categories_node_children is not None:
                category_nodes = categories_node_children.findall("node")
                for category_node in category_nodes:
                    # There is only one attribute node for each
                    attr = category_node.find("attribute")
                    if attr is not None:
                        categories.append(attr.attrib.get("value"))
        return sorted(categories)

    def get_tag_from_lsx(self, tag_file_contents: str) -> Tag | None:
        """Parse tag XML and build a list of Tags"""
        tag: Tag | None = None
        root_node: ET.Element = ET.fromstring(tag_file_contents)

        if root_node is not None:
            tags_region = get_tag_with_id_from_node(root_node, "region", "Tags")
            if tags_region is not None:
                tag_node: ET.Element = tags_region.find("node")
                if tag_node is not None:
                    tag_props: list[dict] = [
                        {
                            "name": "Name",
                            "value_prop": "value",
                        },
                        {
                            "name": "UUID",
                            "value_prop": "value",
                        },
                        {
                            "name": "Description",
                            "value_prop": "value",
                        },
                        {
                            "name": "DisplayDescription",
                            "value_prop": "handle",
                        },
                        {
                            "name": "DisplayName",
                            "value_prop": "handle",
                        },
                        {
                            "name": "Icon",
                            "value_prop": "value",
                        },
                    ]
                    tag_values: dict[str, str] = {}
                    attrs: list[ET.Element] = tag_node.findall("attribute")
                    for attr in attrs:
                        for tag_prop in tag_props:
                            if (
                                "id" in attr.attrib
                                and attr.attrib["id"] == tag_prop["name"]
                            ):
                                tag_values[tag_prop["name"]] = attr.attrib.get(
                                    tag_prop["value_prop"]
                                )
                    tag = Tag(
                        name=tag_values["Name"],
                        description=tag_values["Description"],
                        display_name=tag_values["DisplayName"],
                        display_description=tag_values["DisplayDescription"],
                        icon=tag_values["Icon"],
                        uuid=tag_values["UUID"],
                        categories=self.get_categories_from_children_node(
                            tag_node.find("children")
                        ),
                    )
            else:
                self.logger.error(
                    "get_tags_from_file_contents: unable to find tags region"
                )

        return tag

    def get_tag_category_list_from_tag(self, tag: Tag) -> str:
        """Returns comma separated list of tag names"""
        return ", ".join(sorted(tag.categories))
