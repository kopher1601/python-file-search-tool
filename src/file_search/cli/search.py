from rich.markdown import Markdown
from rich.panel import Panel
from google.genai import types
import typer
from rich.console import Console
from file_search.cli import normalize_store_name
from file_search.core.client import get_client
from file_search.models.schemas import SearchResponse, Citation

search_app = typer.Typer(help="Search")
console = Console()


def _parse_response(response, model_name: str) -> SearchResponse:
    """Gemini API 응답을 SearchResponse 모델로 변환한다."""
    citations: list[Citation] = []
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata
        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                source = chunk.retrieved_context
                citations.append(Citation(
                    title=source.title or None,
                    content=source.uri if hasattr(source, "uri") else None,
                ))
    return SearchResponse(
        answer=response.text,
        citations=citations,
        model=model_name,
    )


def _print_response(sr: SearchResponse) -> None:
    """SearchResponse를 Rich로 출력한다."""
    console.print(Panel(
        Markdown(sr.answer),
        title="[bold cyan]Answer[/bold cyan]",
        border_style="cyan",
    ))
    if sr.citations:
        console.print("\n[bold yellow]Sources:[/bold yellow]")
        for i, cite in enumerate(sr.citations, 1):
            console.print(f" {i}. {cite.title or 'Unknown'}")


def query(
    question: str = typer.Argument(..., help="検索質問"),
    store_name: str = typer.Option(..., "--store", "-s", help="Storeリソース名"),
    model: str = typer.Option("gemini-2.5-flash", "--model", "-m", help="使用するモデル名")
) -> None:
    """문서를 기반으로 질문에 답변한다."""
    store_name = normalize_store_name(store_name)
    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
         tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
                )
            )
         ],
        ),
    )

    sr = _parse_response(response, model)
    _print_response(sr)

@search_app.command("chat")
def chat(
    store_name: str = typer.Option(..., "--store", "-s", help="Storeリソース名"),
) -> None:
    """대화형 검색 모드를 실행한다."""
    store_name = normalize_store_name(store_name)
    client = get_client()
    console.print("[bold]대화형 검색 모드 (종료: quit.exit)[/bold]\n")

    history: list[types.Content] = []

    while True:
        question = console.input("[bold green]Q: [/bold green]")
        if question.lower() in {"quit", "exit", "q"}:
            break

        history.append(types.Content(
            role="user",
            parts=[types.Part(text=question)],
        ))
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ],
            ),
        )

        history.append(types.Content(
            role="model",
            parts=[types.Part(text=response.text)],
        ))
        sr = _parse_response(response, "gemini-2.5-flash")
        _print_response(sr)
