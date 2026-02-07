import typer

from file_search.cli.store import store_app
from file_search.cli.file import file_app

app = typer.Typer(help="Gemini File Search CLI Tool")

app.add_typer(store_app, name="store")
app.add_typer(file_app, name="file")
