import typer
from rich.console import Console
from rich.table import Table

from file_search.core.client import get_client

store_app = typer.Typer(help="File Search Store 관리")
console = Console()

@store_app.command("create")
def create_store(
    name: str = typer.Argument(..., help="Store name"),
) -> None:
    """새로운 FileSearchStore를 생성한다."""
    client = get_client()
    store = client.file_search_stores.create(
        config={"display_name": name}
    )
    console.print(f"[green]Store created: {store.name}[/green]")
    console.print(f" Name: {store.name}")
    console.print(f" Display Name: {store.display_name}")

@store_app.command("list")
def list_stores() -> None:
    """FileSearchStore 목록을 조회한다."""
    client = get_client()
    stores = client.file_search_stores.list()

    table = Table(title="File Search Stores")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Created", style="yellow")
    
    for store in stores:
        table.add_row(
            store.name,
            store.display_name or "-",
            str(store.create_time or "-")
        )

    console.print(table)

@store_app.command("delete")
def delete_store(
    name: str = typer.Argument(..., help="Store 리소스 이름"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """FileSearchStore를 삭제한다."""
    if not force:
        confirm = typer.confirm(f"'{name}'을(를) 삭제하시겠습니까?")
        if not confirm:
            raise typer.Exit()

    client = get_client()
    client.file_search_stores.delete(name=name)
    console.print(f"[red]삭제 완료: {name}[/red]")