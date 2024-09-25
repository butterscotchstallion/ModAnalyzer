import os
import uuid
from typing import Optional

import typer

from ModAnalyzer.Structure import StructureGenerator

app = typer.Typer()


@app.command()
def generate(
    mod_name: str,
    debug_mode: Optional[bool] = typer.Option(
        False, help="Enables additional debug logging"
    ),
):
    debug_mode_indicator = ""
    if debug_mode:
        debug_mode_indicator = "[Debug Mode]"

    typer.echo(f"Generating mod: {mod_name} {debug_mode_indicator}")
    typer.echo(f"=================================================={os.linesep}")
    generator = StructureGenerator(mod_name=mod_name)
    success = generator.create_structure(mod_name, uuid.uuid4(), display_tree=True)


if __name__ == "__main__":
    app()
