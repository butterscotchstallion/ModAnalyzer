import os

import typer

from ModAnalyzer.Structure import ModLinker

app = typer.Typer()


@app.command()
def link(mod_directory: str):
    typer.echo(f"Linking {mod_directory}")
    typer.echo(f"=================================================={os.linesep}")
    linker = ModLinker()
    success = linker.link_mod(mod_directory)

    if success:
        typer.echo(f"Successfully linked {mod_directory} in {linker.game_data_path}")
    else:
        typer.echo(f"Failed to link {mod_directory} in {linker.game_data_path}")


if __name__ == "__main__":
    app()
