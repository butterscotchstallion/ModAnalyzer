import os
from typing import Optional

import typer

from ModAnalyzer.analyzer import Analyzer

app = typer.Typer()


@app.command()
def analyze(
    mod_directory: str,
    mod_name: str,
    debug_mode: Optional[bool] = typer.Option(
        False, help="Enables additional debug logging"
    ),
):
    debug_mode_indicator = ""
    if debug_mode:
        debug_mode_indicator = "[Debug Mode]"

    typer.echo(f"Analyzing {mod_directory} {debug_mode_indicator}")
    typer.echo(f"=================================================={os.linesep}")
    analyzer = Analyzer(using_typer=True)
    analyzer.analyze(mod_directory, debug_mode=debug_mode)


if __name__ == "__main__":
    app()
