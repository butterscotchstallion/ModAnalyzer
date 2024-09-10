class TreasureTableReader:
    def read_from_file(self, filename: str) -> list[str]:
        """Returns list of lines from TT file"""
        lines: list[str] = []
        with open(filename, "r", encoding="UTF-8") as file:
            while line := file.readline():
                lines.append(line.strip())
        return lines
