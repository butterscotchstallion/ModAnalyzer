from argparse import ArgumentParser

parser = ArgumentParser(
    prog="Treasure Table Verifier",
    description="Verifies BG3 treasure tables by checking if each item from the root templates exists in a treasure table",
)
parser.add_argument(
    "-m", dest="mod_directory", help="Your mod directory", required=True
)
args = parser.parse_args()

if __name__ == "__main__":
    if args.mod_directory:
        pass
