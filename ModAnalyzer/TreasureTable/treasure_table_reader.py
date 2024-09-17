import logging


class TreasureTableReader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def read_from_file(self, filename: str) -> list[str]:
        """Returns list of lines from TT file"""
        lines: list[str] = []
        try:
            with open(filename, "r", encoding="UTF-8") as file:
                while line := file.readline():
                    lines.append(line.strip())
        except Exception as err:
            self.logger.error(f"Error reading file: {err}")

        return lines
