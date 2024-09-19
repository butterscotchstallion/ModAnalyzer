from argparse import ArgumentParser

from ModAnalyzer import Analyzer

parser = ArgumentParser(
    prog="Mod Analyzer",
    description="Analyzes BG3 mods to find and fix problems",
)
parser.add_argument(
    "-m", dest="mod_directory", help="Your mod directory", required=True
)
args = parser.parse_args()

if __name__ == "__main__":
    if args.mod_directory:
        analyzer = Analyzer()
        report = analyzer.analyze(args.mod_directory)
