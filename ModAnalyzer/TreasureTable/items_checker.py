class ItemsChecker:
    """
    Checks that all nodes from the RT appear in at least one
    treasure table
    """

    def check_items(
        self, stats_names: set[str], tt_summary: dict[str, list[str]]
    ) -> list[str]:
        """
        Checks each item's stats name against the treasure table summary
        """
        verified_items: list[str] = []
        for stats_name in stats_names:
            if self.item_in_treasure_table(stats_name, tt_summary):
                verified_items.append(stats_name)
        return verified_items

    def item_in_treasure_table(
        self, object_category_name: str, tt_summary: dict[str, list[str]]
    ) -> bool:
        """Checks if stats name is in summary"""
        exists = False
        tt_entry_name = f"I_{object_category_name}"
        if tt_entry_name in tt_summary.keys():
            exists = len(tt_summary[tt_entry_name]) > 0
        return exists
