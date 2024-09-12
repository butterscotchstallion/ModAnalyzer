import logging

from TreasureTableVerifier.models import TreasureTableEntry


class TreasureTableParser:
    """
    Parses Treasure Table files

    Each file has a series of entries like this:

    // A comment looks like this //
    new treasuretable "CHA_Exterior_Bandit_Leader"
    CanMerge 1
    new subtable "1,1"
    object category "I_OBJ_RUNE_ROF_BONE_ARMOR",1,0,0,0,0,0,0,0
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_quoted_values(self, input: str) -> list[str]:
        values = input.split('"')[1::]
        return [value.strip() for value in values if value.strip()]

    def get_value_from_line_in_quotes(self, input: str) -> str:
        """Parses value from within quotes"""
        values = self.get_quoted_values(input)
        value = ""
        if len(values):
            value = values[0]
        return value

    def parse_treasure_table(
        self, lines: list[str]
    ) -> dict[str, list[TreasureTableEntry]]:
        """
        Parses a list of strings into a TreasureTableEntry list
        """
        tt_map: dict[str, list[TreasureTableEntry]] = {}
        tt_name = None
        can_merge = False
        subtable_position = ""
        object_category_name = ""
        tt_entry_map: dict[str, dict[str, bool]] = {}

        self.logger.info(f"Parsing {len(lines)} lines")

        for line in lines:
            if line.startswith("//"):
                continue

            if line.startswith("new treasuretable"):
                tt_name = line.split('"')[1].strip()

            if tt_name:
                self.logger.debug(f"Name: {tt_name}")

                if tt_name not in tt_map:
                    tt_map[tt_name] = []

                if line.startswith("CanMerge"):
                    can_merge = bool(self.get_value_from_line_in_quotes(line))

                if line.startswith("new subtable"):
                    subtable_position = self.get_value_from_line_in_quotes(line)

                if line.startswith("object category"):
                    object_category_name = self.get_value_from_line_in_quotes(line)

                if object_category_name and subtable_position:
                    print("valid object category name and subtable")

                    tt_entry = TreasureTableEntry(
                        can_merge=can_merge,
                        subtable_position=subtable_position,
                        object_category_name=object_category_name,
                    )

                    if tt_name not in tt_entry_map:
                        tt_entry_map[tt_name] = {}

                    if object_category_name not in tt_entry_map[tt_name].keys():
                        print("adding entry")
                        tt_map[tt_name].append(tt_entry)
                        tt_entry_map[tt_name][object_category_name] = True
                    else:
                        print(tt_entry_map)
        return tt_map
