import os

import typer

from ModAnalyzer.analyzer import Analyzer

app = typer.Typer()


@app.command()
def analyze(mod_directory: str):
    typer.echo(f"Analyzing {mod_directory}")
    typer.echo(f"=================================================={os.linesep}")
    analyzer = Analyzer(using_typer=True)
    analyzer.analyze(mod_directory)


if __name__ == "__main__":
    app()
