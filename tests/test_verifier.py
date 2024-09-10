from TreasureTableVerifier import TreasureTableParser, TreasureTableReader


def test_parse_file():
    parser = TreasureTableParser()
    reader = TreasureTableReader()
    tt_lines = reader.read_from_file("tests/fixture/TreasureTable.txt")
    tt = parser.parse_treasure_table(tt_lines)

    assert tt is not None, "Failed to parse treasure table"
    assert len(tt) == 32

    print(tt)
