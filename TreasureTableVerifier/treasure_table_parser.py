import logging

from TreasureTableVerifier.models import TreasureTableEntry


class InvalidTreasureTableEntryException(Exception):
    pass


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
        values: list[str] = self.get_quoted_values(input)
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
        tt_name: str = ""
        can_merge: bool = False
        subtable_position: str = ""
        object_category_name: str = ""
        tt_entry_map: dict[str, dict[str, bool]] = {}
        entry_valid = False
        entry_options: list[int] = []

        self.logger.info(f"Parsing {len(lines)} lines")

        for line in lines:
            if line.startswith("//"):
                continue

            """
            Each time there is a new treasure table we must reset
            everything, otherwise the next entry will have items
            from the previous one.
            """
            if line.startswith("new treasuretable"):
                tt_name = self.get_value_from_line_in_quotes(line)
                can_merge = False
                subtable_position = ""
                object_category_name = ""
                entry_valid = False
                entry_options = []

            if tt_name:
                if tt_name not in tt_map:
                    tt_map[tt_name] = []

                if line.startswith("CanMerge"):
                    can_merge = bool(self.get_value_from_line_in_quotes(line))

                if line.startswith("new subtable"):
                    subtable_position = self.get_value_from_line_in_quotes(line)

                if line.startswith("object category"):
                    object_category_name = self.get_value_from_line_in_quotes(line)
                    last_quote_location = line.rfind('"')
                    if last_quote_location:
                        # 1,0,0,0,0,0,0,0
                        option_string = line[last_quote_location + 2 : :]
                        entry_options = [
                            int(option) for option in option_string.split(",")
                        ]
                        self.logger.info(entry_options)

                if object_category_name and subtable_position:
                    if tt_name not in tt_entry_map:
                        tt_entry_map[tt_name] = {}

                    if object_category_name[0:2] != "I_":
                        self.logger.error(
                            f"Invalid object category name: {object_category_name}"
                        )
                        entry_valid = False
                    else:
                        entry_valid = True

                    if object_category_name not in tt_entry_map[tt_name].keys():
                        tt_entry = TreasureTableEntry(
                            can_merge=can_merge,
                            subtable_position=subtable_position,
                            object_category_name=object_category_name,
                            is_valid=entry_valid,
                            options=entry_options,
                        )
                        tt_map[tt_name].append(tt_entry)
                        tt_entry_map[tt_name][object_category_name] = True

        self.logger.info(f"Parsed {len(tt_map.keys())} treasure tables")

        return tt_map

    def get_summary_from_tt_map(
        self, tt_map: dict[str, list[TreasureTableEntry]]
    ) -> dict[str, list[str]]:
        """
        Builds summary of places where an item appears based on the
        generated treasure table map

        obj_category_name -> (
            tt_name,
            tt_name,
            ...
        )
        """
        tt_summary = {}

        for tt_name in tt_map:
            for tt_entry in tt_map[tt_name]:
                if tt_entry.object_category_name not in tt_summary:
                    tt_summary[tt_entry.object_category_name] = []

                tt_summary[tt_entry.object_category_name].append(tt_name)

        return tt_summary

    def get_object_name(self, object_category_name: str):
        return object_category_name[2:]
