import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import quote

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from file_search.cli import normalize_store_name
from file_search.core.client import get_client

file_app = typer.Typer(help="File Management")
console = Console()


def _to_ascii_filename(filename: str) -> str:
    """비 ASCII 파일명을 URL 인코딩하여 ASCII 안전한 이름으로 변환한다.

    macOS(HFS+/APFS)는 파일명을 NFD(분해형)로 저장하고,
    Windows/Linux는 NFC(조합형)를 사용한다.
    예: "が" → NFD: U+304B + U+3099 (か + 탁점) / NFC: U+304C (が)
    NFC로 정규화한 뒤 URL 인코딩하면 OS에 관계없이 동일한 결과가 나온다.
    """
    normalized = unicodedata.normalize("NFC", filename)
    return quote(normalized, safe=".")


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

    store_name = normalize_store_name(store_name)
    client = get_client()
    name = display_name or file_path.name

    # google-genai SDK는 파일명을 X-Goog-Upload-File-Name 헤더에 넣는데,
    # 비 ASCII 문자가 포함되면 httpx가 인코딩에 실패한다.
    # 파일명을 NFC 정규화 후 URL 인코딩하여 ASCII 안전한 하드링크를 만들어 우회한다.
    upload_path = file_path.resolve()
    try:
        upload_path.name.encode("ascii")
        needs_encoding = False
    except UnicodeEncodeError:
        needs_encoding = True

    with tempfile.TemporaryDirectory() as tmp_dir:
        if needs_encoding:
            encoded_name = _to_ascii_filename(file_path.name)
            tmp_path = Path(tmp_dir) / encoded_name
            tmp_path.hardlink_to(upload_path)
            upload_path = tmp_path

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Uploading {file_path.name}...", total=None)
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(upload_path),
                file_search_store_name=store_name,
                config={"display_name": name},
            )

    console.print(f"[green]업로드 완료: {name}[/green]")

@file_app.command("list")
def list_files(
    store_name: str = typer.Option(..., "--store", "-s", help="Store 리소스 이름"),
) -> None:
    """Store 내 파일 목록을 조회한다."""
    store_name = normalize_store_name(store_name)
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