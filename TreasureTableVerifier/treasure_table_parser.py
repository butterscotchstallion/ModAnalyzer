import logging

from TreasureTableVerifier.models.treasure_table_entry import TreasureTableEntry

logger = logging.getLogger(__name__)


class TreasureTableParser:
    def parse_treasure_table(self, lines: list[str]) -> list[TreasureTableEntry]:
        entries = {}
        for line in lines:
            tt_name = None

            if line.startswith('new treasuretable "'):
                tt_name = line.split('"')[1].strip()

            if tt_name:
                if tt_name not in entries:
                    entries[tt_name] = {}

                if line.startswith("CanMerge "):
                    entries[tt_name].can_merge = bool(line.split("CanMerge ")[1])

        tt_entries = []

        print(entries)

        for tt_name in entries:
            try:
                entry = entries[tt_name]

                tt_entries.append(
                    TreasureTableEntry(
                        subtable_position=entry["subtable_position"],
                        object_category_name=tt_name,
                    )
                )
            except KeyError as missing_key:
                logger.critical(f"Missing key for entry '{tt_name}': {missing_key}")

        return tt_entries
