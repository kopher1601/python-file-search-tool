from rich.table import Table
from file_search.core.client import get_client
from rich.console import Console
import typer
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn

file_app =typer.Typer(help="File Management")
console = Console()

@file_app.command("upload")
def upload_file(
    file_path: Path = typer.Argument(..., help="업로드할 파일 경로"),
    store_name: str = typer.Option(..., "--store", "-s", help="Store 리소스 이름"),
    display_name: str = typer.Option("", "--name", "-n", help="표시 이름"),
) -> None:
    """파일을 FileSearchStore에 업로드한다."""
    if not file_path.exists():
        console.print(f"[red]파일을 찾을 수 없습니다: {file_path}[/red]")
        raise typer.Exit(1)

    client = get_client()
    name = display_name or file_path.name

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Uploading {file_path.name}...", total=None)
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(file_path),
            file_search_store_name=store_name,
            config={"display_name": name},
        )

    console.print(f"[green]업로드 완료: {name}[/green]")

@file_app.command("list")
def list_files(
    store_name: str = typer.Option(..., "--store", "-s", help="Store 리소스 이름"),
) -> None:
    """Store 내 파일 목록을 조회한다."""
    client = get_client()
    files = client.file_search_stores.documents.list(
        parent=store_name
    )

    table = Table(title="Files in Store")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("State", style="yellow")

    for f in files:
        table.add_row(
            f.name,
            f.display_name or "-",
            str(f.state or "-"),
        )

    console.print(table)