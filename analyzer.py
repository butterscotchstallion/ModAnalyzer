import pprint

import typer

from ModAnalyzer.analyzer import Analyzer

app = typer.Typer()


@app.command()
def analyze(mod_directory: str):
    print(f"Analyzing {mod_directory}")
    analyzer = Analyzer()
    report = analyzer.analyze(mod_directory)

    pprint.pp(report)


if __name__ == "__main__":
    app()
