import typer

from file_search.cli.store import store_app
from file_search.cli.file import file_app
from file_search.cli.search import search_app, query

app = typer.Typer(help="Gemini File Search CLI Tool")

# 서브커맨드 그룹 등록
app.add_typer(store_app, name="store")
app.add_typer(file_app, name="file")
app.add_typer(search_app, name="search")

# 루트 커맨드 등록
app.command("query")(query)
