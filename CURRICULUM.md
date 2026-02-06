# Python 실습 커리큘럼: Gemini File Search CLI 도구 만들기

> 4년차 백엔드 개발자(Java, Kotlin, Go)를 위한 프로젝트 기반 Python 학습 커리큘럼
>
> Gemini API의 File Search Tool(관리형 RAG)을 활용한 문서 검색 CLI 도구를 단계별로 구현하며 Python의 핵심 개념을 익힌다.

---

## 기술 스택

| 카테고리 | 도구 |
|---------|------|
| 언어 | Python 3.12+ |
| 런타임 관리 | mise (Python 버전 관리) |
| 의존성 관리 | uv (패키지 & 가상환경) |
| AI API | google-genai (Gemini API SDK) |
| CLI | Typer |
| 터미널 UI | Rich |
| 데이터 모델 | Pydantic |
| 테스트 | pytest, pytest-mock |
| 타입 체크 | mypy |
| 린터/포매터 | ruff |

## 프로젝트 구조

```
python-file-search-tool/
├── pyproject.toml          # uv 프로젝트 설정 & 의존성
├── uv.lock                 # 의존성 lock 파일
├── .python-version         # mise가 읽는 Python 버전
├── .mise.toml              # mise 설정
├── README.md
├── CURRICULUM.md
├── .gitignore
├── .env                    # GEMINI_API_KEY (gitignore 대상)
├── src/
│   └── file_search/
│       ├── __init__.py
│       ├── __main__.py         # python -m file_search 진입점
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py          # Typer 앱 & 서브커맨드 등록
│       │   ├── store.py        # store 관련 CLI 명령어
│       │   ├── file.py         # file 관련 CLI 명령어
│       │   └── search.py       # search CLI 명령어
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py       # Gemini 클라이언트 설정
│       │   ├── store.py        # FileSearchStore 비즈니스 로직
│       │   └── search.py       # 검색 비즈니스 로직
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py      # Pydantic 모델
│       └── exceptions.py       # 커스텀 예외 클래스
├── tests/
│   ├── conftest.py             # 공통 fixture
│   └── unit/
│       ├── test_store.py
│       ├── test_search.py
│       └── test_models.py
└── docs/
    └── samples/                # 테스트용 샘플 문서
```

---

## Step 1: 환경 세팅 — mise + uv + 프로젝트 구조

### 학습 목표
- mise로 Python 버전을 관리할 수 있다.
- uv로 프로젝트를 초기화하고 의존성을 관리할 수 있다.
- pyproject.toml의 역할과 구성을 이해한다.
- 가상환경(venv)이 왜 필요한지, 어떻게 동작하는지 안다.

### 익숙한 개념과 비교

| Python | Java/Kotlin/Go |
|--------|---------------|
| mise | sdkman / jabba / goenv |
| uv | Maven / Gradle / go mod |
| pyproject.toml | pom.xml / build.gradle.kts / go.mod |
| uv.lock | pom.xml (resolved) / gradle.lockfile / go.sum |
| venv (가상환경) | 별도 개념 없음 (JVM/GOPATH로 분리) |

### 실습 내용

1. **mise 설치 & Python 버전 관리**
   ```bash
   # mise 설치 (macOS)
   brew install mise

   # 셸 활성화 (~/.zshrc 또는 ~/.bashrc에 추가)
   echo 'eval "$(mise activate zsh)"' >> ~/.zshrc

   # Python 3.12 설치 & 프로젝트에 고정
   cd python-file-search-tool
   mise use python@3.12

   # 확인
   python --version  # Python 3.12.x
   ```
   - `.mise.toml`과 `.python-version` 파일이 자동 생성됨
   - Java의 sdkman, Go의 goenv와 같은 역할

2. **uv 설치 & 프로젝트 초기화**
   ```bash
   # uv 설치 (macOS)
   brew install uv
   # 또는
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 프로젝트 초기화 (src-layout)
   uv init --lib --python 3.12

   # 의존성 설치 (venv 자동 생성)
   uv sync
   ```

3. **pyproject.toml 설정**
   ```toml
   [project]
   name = "file-search"
   version = "0.1.0"
   description = "Gemini File Search CLI Tool"
   requires-python = ">=3.12"
   dependencies = []

   [project.scripts]
   fsearch = "file_search.cli.app:app"

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"
   ```
   - `[project]`: PEP 621 표준 메타데이터 (Poetry의 `[tool.poetry]`와 달리 표준 스펙)
   - `[project.scripts]`: CLI 진입점 등록 (Java의 Main-Class와 유사)

4. **가상환경 이해**
   ```bash
   # uv sync 실행 시 .venv 자동 생성
   uv sync

   # uv run으로 가상환경 내에서 실행 (별도 activate 불필요)
   uv run python -c "print('hello')"

   # 또는 직접 activate
   source .venv/bin/activate
   python -c "print('hello')"
   ```
   - Python은 시스템에 하나의 인터프리터를 공유하므로 프로젝트별 의존성 격리가 필수
   - Java는 JAR로 격리, Go는 바이너리 컴파일이므로 이 문제가 없음
   - **uv는 activate 없이 `uv run`만으로 가상환경 실행이 가능** — Poetry보다 편리

5. **디렉토리 구조 생성**
   ```bash
   mkdir -p src/file_search/{cli,core,models}
   mkdir -p tests/unit
   mkdir -p docs/samples
   touch src/file_search/__init__.py
   touch src/file_search/__main__.py
   touch src/file_search/{cli,core,models}/__init__.py
   ```

### mise + uv 워크플로우 요약

```
mise use python@3.12    → Python 버전 고정
uv init --lib           → 프로젝트 초기화
uv add <패키지>          → 의존성 추가 (go get, gradle add와 유사)
uv remove <패키지>       → 의존성 제거
uv sync                 → 의존성 설치 (npm install, go mod tidy와 유사)
uv run <명령어>          → 가상환경 내에서 실행
uv lock                 → lock 파일 갱신
```

### 체크리스트
- [x] `mise use python@3.12` 후 `python --version`이 3.12.x를 출력한다
- [x] `uv sync` 후 `.venv` 디렉토리가 생성된다
- [x] `uv run python -c "print('hello')"` 가 동작한다
- [x] src-layout 디렉토리 구조가 생성되었다

---

## Step 2: Python 핵심 문법 (Java/Kotlin/Go 개발자 관점)

### 학습 목표
- Python의 타입 시스템과 duck typing을 이해한다.
- 데코레이터, 컨텍스트 매니저, 에러 처리 패턴을 익힌다.
- dataclass와 Pydantic 모델을 활용할 수 있다.

### 2-1. 타입 힌트 & Duck Typing

**Go interface와 비교**

```go
// Go: 명시적 인터페이스 구현 불필요 (structural typing)
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

```python
# Python: 프로토콜(structural subtyping) — Go interface와 가장 유사
from typing import Protocol

class Reader(Protocol):
    def read(self, size: int = -1) -> bytes: ...

def process(reader: Reader) -> None:
    data = reader.read()
    # reader가 read() 메서드만 있으면 됨 — duck typing
```

```python
# 타입 힌트 기본
def greet(name: str) -> str:
    return f"Hello, {name}"

# 제네릭 (Java의 <T>와 비교)
from typing import TypeVar, Generic

T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

# Union 타입 (Kotlin의 sealed class와 비교)
def find_user(user_id: int) -> User | None:
    ...
```

> **핵심 차이:** Python의 타입 힌트는 런타임에 강제되지 않는다. mypy 같은 도구로 정적 분석할 때만 검증된다.

### 2-2. 데코레이터

**Java annotation과 비교**

```java
// Java: 컴파일 타임 메타데이터
@Transactional
public void updateUser(User user) { ... }
```

```python
# Python: 함수를 감싸는 함수 — 런타임에 동작을 변경
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def upload_file(path: str) -> None:
    ...
```

> **핵심 차이:** Java annotation은 메타데이터이고, Python 데코레이터는 함수를 인자로 받아 새 함수를 리턴하는 고차 함수다.

### 2-3. 컨텍스트 매니저

**Java try-with-resources와 비교**

```java
// Java
try (var stream = new FileInputStream("file.txt")) {
    // stream 자동 close
}
```

```python
# Python: with 문
with open("file.txt") as f:
    content = f.read()
# f가 자동으로 close됨

# 커스텀 컨텍스트 매니저
from contextlib import contextmanager

@contextmanager
def managed_client():
    client = create_client()
    try:
        yield client
    finally:
        client.close()

with managed_client() as c:
    c.do_something()
```

### 2-4. 에러 처리

**Go error return과 비교**

```go
// Go: 에러를 값으로 반환
file, err := os.Open("file.txt")
if err != nil {
    return fmt.Errorf("failed to open: %w", err)
}
```

```python
# Python: 예외 기반 (Java와 유사하지만 checked exception 없음)
try:
    file = open("file.txt")
except FileNotFoundError as e:
    raise ApplicationError(f"failed to open: {e}") from e
except PermissionError:
    ...
finally:
    ...
```

> **핵심 차이:** Go는 에러를 값으로 명시적으로 처리하고, Python/Java는 예외를 던진다. 다만 Python에는 checked exception이 없어서 어떤 예외가 발생할지 문서나 코드를 읽어야 알 수 있다.

### 2-5. dataclass & Pydantic 모델

**Kotlin data class와 비교**

```kotlin
// Kotlin
data class SearchResult(
    val id: String,
    val content: String,
    val score: Double,
    val source: String? = null
)
```

```python
# Python dataclass — Kotlin data class와 거의 동일
from dataclasses import dataclass

@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    source: str | None = None

# Pydantic — 런타임 검증 + 직렬화 지원 (JSON ↔ 객체 변환)
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    source: str | None = None

# API 응답을 바로 파싱
result = SearchResult.model_validate(api_response)
```

> **Pydantic을 선택하는 이유:** Gemini API 응답을 파이썬 객체로 변환할 때 자동 검증과 alias 매핑이 편리하다.

### 실습 내용
- `src/file_search/models/schemas.py`에 Pydantic 모델 정의
- `src/file_search/exceptions.py`에 커스텀 예외 클래스 정의

### 체크리스트
- [x] Pydantic 모델로 JSON 데이터를 파싱할 수 있다
- [x] 커스텀 예외 클래스를 정의하고 raise/except 할 수 있다
- [x] 타입 힌트를 사용한 코드에 `uv run mypy src/`를 실행해 통과한다

---

## Step 3: Gemini API 설정 & 기본 사용

### 학습 목표
- Google AI Studio에서 API 키를 발급받을 수 있다.
- google-genai SDK로 Gemini API를 호출할 수 있다.
- 환경변수로 API 키를 안전하게 관리할 수 있다.

### 사전 준비: API 키 발급

1. [Google AI Studio](https://aistudio.google.com)에 접속
2. "Get API Key" → API 키 생성
3. `.env` 파일에 저장

### 실습 내용

1. **의존성 추가**
   ```bash
   uv add google-genai python-dotenv
   ```

2. **환경변수 설정**
   ```bash
   # .env 파일 생성
   echo "GEMINI_API_KEY=your-api-key-here" > .env
   ```

   ```gitignore
   # .gitignore에 추가
   .env
   ```

3. **Gemini 클라이언트 설정** (`src/file_search/core/client.py`)
   ```python
   import os
   from dotenv import load_dotenv
   from google import genai

   load_dotenv()

   def get_client() -> genai.Client:
       """Gemini API 클라이언트를 반환한다."""
       api_key = os.getenv("GEMINI_API_KEY")
       if not api_key:
           raise EnvironmentError(
               "GEMINI_API_KEY 환경변수가 설정되지 않았습니다. "
               ".env 파일을 확인하세요."
           )
       return genai.Client(api_key=api_key)
   ```

4. **기본 동작 확인** — Gemini가 응답하는지 테스트
   ```python
   # 간단한 확인 스크립트
   from file_search.core.client import get_client

   client = get_client()
   response = client.models.generate_content(
       model="gemini-2.5-flash",
       contents="Hello, Gemini!"
   )
   print(response.text)
   ```

### OAuth vs API Key 비교

| | Google Drive API (OAuth2) | Gemini API (API Key) |
|---|---|---|
| 인증 방식 | OAuth2 플로우 (브라우저 인증) | API 키 (환경변수) |
| 복잡도 | 높음 (token 갱신 등) | 낮음 |
| 사용자 데이터 | 사용자별 Drive 접근 | 프로젝트 레벨 접근 |
| 설정 파일 | client_secret.json + token.json | .env 하나 |

> Gemini File Search는 **API 키만으로** 동작하므로 OAuth2 대비 훨씬 간단하다.

### 체크리스트
- [ ] Google AI Studio에서 API 키를 발급받았다
- [ ] `.env` 파일에 API 키가 저장되고 `.gitignore`에 포함되었다
- [ ] `get_client()`로 Gemini 클라이언트를 생성할 수 있다
- [ ] 간단한 `generate_content` 호출이 정상 동작한다

---

## Step 4: FileSearchStore 생성 & 파일 업로드

### 학습 목표
- Gemini File Search의 핵심 개념(Store, 청킹, 임베딩)을 이해한다.
- FileSearchStore를 생성하고 파일을 업로드할 수 있다.
- Typer로 CLI 서브커맨드 그룹을 정의할 수 있다.

### 핵심 개념: File Search 아키텍처

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  로컬 파일    │ ──▶ │ FileSearchStore  │ ──▶ │  Gemini 모델  │
│ (PDF, TXT..) │     │ (청킹→임베딩→인덱싱) │     │ (RAG 응답)   │
└─────────────┘     └──────────────────┘     └─────────────┘
```

- **FileSearchStore**: 파일을 저장하고 검색 가능하게 인덱싱하는 컨테이너
- 업로드 시 자동으로 **청킹 → 임베딩 생성 → 벡터 인덱싱** 수행
- 별도의 임베딩 모델이나 벡터 DB 설정이 불필요 (완전 관리형)

### 실습 내용

1. **CLI 의존성 추가**
   ```bash
   uv add typer rich
   ```

2. **Typer 앱 설정** (`src/file_search/cli/app.py`)
   ```python
   import typer

   app = typer.Typer(help="Gemini File Search CLI Tool")

   # 서브커맨드 그룹 등록 (git의 서브커맨드와 유사)
   # fsearch store create, fsearch store list, ...
   # fsearch file upload, fsearch file list, ...
   # fsearch query "질문"
   ```

3. **Store 관리 명령어** (`src/file_search/cli/store.py`)
   ```python
   import typer
   from rich.console import Console
   from rich.table import Table

   store_app = typer.Typer(help="FileSearchStore 관리")
   console = Console()

   @store_app.command("create")
   def create_store(
       name: str = typer.Argument(..., help="Store 이름"),
   ) -> None:
       """새로운 FileSearchStore를 생성한다."""
       from file_search.core.client import get_client

       client = get_client()
       store = client.file_search_stores.create(
           config={"display_name": name}
       )
       console.print(f"[green]Store 생성 완료[/green]")
       console.print(f"  Name: {store.name}")
       console.print(f"  Display Name: {store.display_name}")

   @store_app.command("list")
   def list_stores() -> None:
       """모든 FileSearchStore 목록을 조회한다."""
       from file_search.core.client import get_client

       client = get_client()
       stores = client.file_search_stores.list()

       table = Table(title="FileSearchStores")
       table.add_column("Name", style="cyan")
       table.add_column("Display Name", style="green")
       table.add_column("Created", style="yellow")

       for store in stores:
           table.add_row(
               store.name,
               store.display_name or "-",
               str(store.create_time or "-"),
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

       from file_search.core.client import get_client

       client = get_client()
       client.file_search_stores.delete(name=name)
       console.print(f"[red]삭제 완료: {name}[/red]")
   ```

4. **파일 업로드 명령어** (`src/file_search/cli/file.py`)
   ```python
   from pathlib import Path
   import typer
   from rich.console import Console
   from rich.progress import Progress, SpinnerColumn, TextColumn

   file_app = typer.Typer(help="파일 관리")
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

       from file_search.core.client import get_client

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
       from file_search.core.client import get_client
       from rich.table import Table

       client = get_client()
       files = client.file_search_stores.list_files(
           file_search_store_name=store_name,
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
   ```

5. **커스텀 청킹 설정** (선택사항)
   ```python
   # 청킹 설정을 직접 지정할 수도 있다
   store = client.file_search_stores.create(
       config={
           "display_name": name,
           "chunking_config": {
               "white_space_config": {
                   "max_tokens_per_chunk": 200,
                   "max_overlap_tokens": 20,
               }
           },
       }
   )
   ```

### 지원 파일 형식
| 카테고리 | 형식 |
|---------|------|
| 문서 | PDF, DOCX, PPTX, XLSX, TXT, Markdown |
| 코드 | .py, .js, .java, .go, .kt, .rs, .c, .cpp |
| 데이터 | JSON, XML, HTML, CSV, SQL |

### 체크리스트
- [ ] `fsearch store create` 로 FileSearchStore를 생성할 수 있다
- [ ] `fsearch store list` 로 Store 목록이 테이블로 출력된다
- [ ] `fsearch file upload` 로 파일이 Store에 업로드된다
- [ ] `fsearch file list` 로 Store 내 파일 목록을 조회할 수 있다
- [ ] `--help` 로 각 명령어의 도움말이 표시된다

---

## Step 5: 파일 검색 & 질의 (핵심 기능)

### 학습 목표
- File Search Tool을 사용하여 업로드된 문서에 질의할 수 있다.
- Gemini의 RAG 응답과 인용(citation)을 파싱할 수 있다.
- Rich Markdown으로 응답을 예쁘게 출력할 수 있다.

### 핵심 개념: File Search 질의 흐름

```
사용자 질문
    ↓
Gemini API (tools=[FileSearch(store_names=[...])])
    ↓
자동으로 관련 문서 청크 검색 (벡터 유사도)
    ↓
검색된 컨텍스트 + 질문 → Gemini 모델이 답변 생성
    ↓
답변 + 인용(citation) 반환
```

### 실습 내용

1. **검색 명령어** (`src/file_search/cli/search.py`)
   ```python
   import typer
   from rich.console import Console
   from rich.markdown import Markdown
   from rich.panel import Panel
   from google import genai
   from google.genai import types

   console = Console()

   def query(
       question: str = typer.Argument(..., help="검색 질문"),
       store_name: str = typer.Option(..., "--store", "-s", help="Store 리소스 이름"),
       model: str = typer.Option("gemini-2.5-flash", "--model", "-m", help="사용할 모델"),
   ) -> None:
       """문서를 기반으로 질문에 답변한다."""
       from file_search.core.client import get_client

       client = get_client()

       response = client.models.generate_content(
           model=model,
           contents=question,
           config=types.GenerateContentConfig(
               tools=[
                   types.Tool(
                       file_search=types.FileSearch(
                           file_search_store_names=[store_name],
                       )
                   )
               ],
           ),
       )

       # 답변 출력
       console.print(Panel(
           Markdown(response.text),
           title="[bold cyan]Answer[/bold cyan]",
           border_style="cyan",
       ))

       # 인용 출력
       if response.candidates and response.candidates[0].grounding_metadata:
           metadata = response.candidates[0].grounding_metadata
           if metadata.grounding_chunks:
               console.print("\n[bold yellow]Sources:[/bold yellow]")
               for i, chunk in enumerate(metadata.grounding_chunks, 1):
                   source = chunk.retrieved_context
                   console.print(f"  {i}. {source.title or 'Unknown'}")
   ```

2. **대화형 검색 모드** (선택 구현)
   ```python
   @search_app.command("chat")
   def chat(
       store_name: str = typer.Option(..., "--store", "-s"),
   ) -> None:
       """대화형 검색 모드를 시작한다."""
       from file_search.core.client import get_client
       from google.genai import types

       client = get_client()
       console.print("[bold]대화형 검색 모드 (종료: quit/exit)[/bold]\n")

       history: list[types.Content] = []

       while True:
           question = console.input("[bold green]Q:[/bold green] ")
           if question.lower() in ("quit", "exit", "q"):
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
                               file_search_store_names=[store_name],
                           )
                       )
                   ],
               ),
           )

           history.append(types.Content(
               role="model",
               parts=[types.Part(text=response.text)],
           ))

           console.print(f"\n[bold cyan]A:[/bold cyan] {response.text}\n")
   ```

3. **응답 모델 정의** (`src/file_search/models/schemas.py`)
   ```python
   from pydantic import BaseModel

   class Citation(BaseModel):
       title: str | None = None
       content: str | None = None

   class SearchResponse(BaseModel):
       answer: str
       citations: list[Citation] = []
       model: str
   ```

### 체크리스트
- [ ] `fsearch query "질문" --store <name>` 으로 문서 기반 답변을 받을 수 있다
- [ ] 답변에 인용(citation)이 포함된다
- [ ] Rich Markdown으로 답변이 깔끔하게 출력된다
- [ ] 대화형 모드에서 연속 질의가 가능하다

---

## Step 6: 메타데이터 필터링 & 고급 검색

### 학습 목표
- 메타데이터를 활용한 필터링 검색을 구현할 수 있다.
- 여러 Store를 동시에 검색할 수 있다.
- 검색 결과를 구조화하여 출력할 수 있다.

### 핵심 개념: 메타데이터 필터링

```
일반 검색:  "매출 보고서에서 Q3 실적은?" → 모든 문서에서 검색
필터 검색:  "매출 보고서에서 Q3 실적은?" + filter="year=2024" → 2024년 문서만 검색
```

### 실습 내용

1. **메타데이터 포함 업로드**
   ```python
   @file_app.command("upload")
   def upload_file(
       file_path: Path = typer.Argument(...),
       store_name: str = typer.Option(..., "--store", "-s"),
       metadata: list[str] = typer.Option(
           [], "--meta", help="메타데이터 (key=value 형식)"
       ),
   ) -> None:
       """파일을 메타데이터와 함께 업로드한다."""
       from file_search.core.client import get_client

       client = get_client()

       # "author=홍길동" → {"key": "author", "string_value": "홍길동"}
       custom_metadata = []
       for m in metadata:
           key, value = m.split("=", 1)
           # 숫자인 경우 numeric_value 사용
           try:
               custom_metadata.append({
                   "key": key, "numeric_value": float(value)
               })
           except ValueError:
               custom_metadata.append({
                   "key": key, "string_value": value
               })

       sample_file = client.files.upload(file=str(file_path))
       client.file_search_stores.import_file(
           file_search_store_name=store_name,
           file_name=sample_file.name,
           config={"custom_metadata": custom_metadata},
       )
       console.print(f"[green]업로드 완료 (메타데이터 {len(custom_metadata)}개 포함)[/green]")
   ```

2. **필터링 검색**
   ```python
   def query(
       question: str = typer.Argument(...),
       store_name: str = typer.Option(..., "--store", "-s"),
       filter: str = typer.Option("", "--filter", help="메타데이터 필터 (예: author=홍길동)"),
   ) -> None:
       """메타데이터 필터를 적용하여 검색한다."""
       from file_search.core.client import get_client
       from google.genai import types

       client = get_client()

       file_search_config = types.FileSearch(
           file_search_store_names=[store_name],
       )

       # 필터가 있으면 metadata_filter 추가
       if filter:
           file_search_config = types.FileSearch(
               file_search_store_names=[store_name],
               metadata_filter=filter,
           )

       response = client.models.generate_content(
           model="gemini-2.5-flash",
           contents=question,
           config=types.GenerateContentConfig(
               tools=[types.Tool(file_search=file_search_config)],
           ),
       )
       # ... 출력 로직
   ```

3. **여러 Store 동시 검색**
   ```python
   # 여러 Store를 한 번에 검색할 수 있다
   file_search = types.FileSearch(
       file_search_store_names=[
           "fileSearchStores/store-1",
           "fileSearchStores/store-2",
       ],
   )
   ```

4. **실행 예시**
   ```bash
   # 메타데이터 포함 업로드
   fsearch file upload report.pdf --store <name> \
       --meta "author=홍길동" --meta "year=2024" --meta "department=영업"

   # 필터링 검색
   fsearch query "Q3 매출은?" --store <name> --filter "year=2024"
   fsearch query "홍길동이 작성한 보고서 요약" --store <name> --filter "author=홍길동"
   ```

### 체크리스트
- [ ] `--meta key=value` 옵션으로 메타데이터를 포함하여 업로드할 수 있다
- [ ] `--filter` 옵션으로 메타데이터 기반 필터링 검색이 동작한다
- [ ] 여러 Store를 동시에 검색할 수 있다

---

## Step 7: Store & 파일 관리 — 수정, 삭제, 정리

### 학습 목표
- Store와 파일의 수정/삭제를 구현할 수 있다.
- 사용자 확인 프롬프트를 구현할 수 있다.
- CLI 도구의 완성도를 높일 수 있다.

### 실습 내용

1. **Store 이름 변경**
   ```python
   @store_app.command("rename")
   def rename_store(
       name: str = typer.Argument(..., help="Store 리소스 이름"),
       new_name: str = typer.Argument(..., help="새 표시 이름"),
   ) -> None:
       """Store의 표시 이름을 변경한다."""
       from file_search.core.client import get_client

       client = get_client()
       updated = client.file_search_stores.update(
           name=name,
           config={"display_name": new_name},
       )
       console.print(f"[green]이름 변경 완료: {updated.display_name}[/green]")
   ```

2. **파일 삭제**
   ```python
   @file_app.command("delete")
   def delete_file(
       file_name: str = typer.Argument(..., help="파일 리소스 이름"),
       store_name: str = typer.Option(..., "--store", "-s"),
       force: bool = typer.Option(False, "--force", "-f"),
   ) -> None:
       """Store에서 파일을 삭제한다."""
       if not force:
           confirm = typer.confirm(f"'{file_name}'을(를) 삭제하시겠습니까?")
           if not confirm:
               console.print("[dim]삭제가 취소되었습니다.[/dim]")
               raise typer.Exit()

       from file_search.core.client import get_client

       client = get_client()
       client.file_search_stores.delete_file(
           file_search_store_name=store_name,
           file_name=file_name,
       )
       console.print(f"[red]삭제 완료: {file_name}[/red]")
   ```

3. **Store 정보 조회**
   ```python
   @store_app.command("info")
   def store_info(
       name: str = typer.Argument(..., help="Store 리소스 이름"),
   ) -> None:
       """Store의 상세 정보를 조회한다."""
       from file_search.core.client import get_client
       from rich.panel import Panel

       client = get_client()
       store = client.file_search_stores.get(name=name)

       info = (
           f"[bold]Name:[/bold] {store.name}\n"
           f"[bold]Display Name:[/bold] {store.display_name or '-'}\n"
           f"[bold]Created:[/bold] {store.create_time or '-'}\n"
           f"[bold]Updated:[/bold] {store.update_time or '-'}"
       )
       console.print(Panel(info, title="Store Info", border_style="cyan"))
   ```

4. **전체 Store 정리 (일괄 삭제)**
   ```python
   @store_app.command("purge")
   def purge_stores(
       force: bool = typer.Option(False, "--force", "-f"),
   ) -> None:
       """모든 FileSearchStore를 삭제한다."""
       from file_search.core.client import get_client

       client = get_client()
       stores = list(client.file_search_stores.list())

       if not stores:
           console.print("[dim]삭제할 Store가 없습니다.[/dim]")
           return

       if not force:
           console.print(f"[yellow]{len(stores)}개의 Store를 모두 삭제합니다.[/yellow]")
           confirm = typer.confirm("계속하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
           if not confirm:
               raise typer.Exit()

       for store in stores:
           client.file_search_stores.delete(name=store.name)
           console.print(f"  [red]삭제: {store.display_name or store.name}[/red]")

       console.print(f"\n[bold red]{len(stores)}개 Store 삭제 완료[/bold red]")
   ```

### 체크리스트
- [ ] `fsearch store rename` 으로 Store 이름을 변경할 수 있다
- [ ] `fsearch store info` 로 Store 상세 정보를 확인할 수 있다
- [ ] `fsearch file delete` 로 파일을 삭제할 수 있다 (확인 프롬프트 포함)
- [ ] `fsearch store delete` 로 Store를 삭제할 수 있다
- [ ] `fsearch store purge` 로 전체 Store를 일괄 삭제할 수 있다
- [ ] `--force` 옵션으로 확인 없이 삭제할 수 있다

---

## Step 8: 테스트 & 마무리

### 학습 목표
- pytest로 단위 테스트를 작성할 수 있다.
- pytest-mock으로 외부 API를 모킹할 수 있다.
- conftest.py와 fixture를 활용할 수 있다.
- mypy, ruff로 코드 품질을 관리할 수 있다.

### 실습 내용

1. **테스트 의존성 추가**
   ```bash
   uv add --dev pytest pytest-mock mypy ruff
   ```

2. **conftest.py — 공통 fixture** (`tests/conftest.py`)
   ```python
   import pytest
   from unittest.mock import MagicMock

   @pytest.fixture
   def mock_client(mocker):
       """Gemini 클라이언트 모킹 fixture"""
       mock = MagicMock()
       mocker.patch(
           "file_search.core.client.get_client",
           return_value=mock,
       )
       return mock

   @pytest.fixture
   def sample_store():
       """테스트용 Store 데이터"""
       return MagicMock(
           name="fileSearchStores/test-store-123",
           display_name="Test Store",
           create_time="2025-01-01T00:00:00Z",
       )
   ```

3. **Store 테스트** (`tests/unit/test_store.py`)
   ```python
   from typer.testing import CliRunner
   from file_search.cli.app import app

   runner = CliRunner()

   def test_create_store(mock_client, sample_store):
       """store create 명령어가 Store를 생성하는지 테스트한다."""
       mock_client.file_search_stores.create.return_value = sample_store

       result = runner.invoke(app, ["store", "create", "Test Store"])
       assert result.exit_code == 0
       assert "생성 완료" in result.stdout

   def test_list_stores_empty(mock_client):
       """Store가 없을 때 빈 테이블을 출력하는지 테스트한다."""
       mock_client.file_search_stores.list.return_value = []

       result = runner.invoke(app, ["store", "list"])
       assert result.exit_code == 0

   def test_delete_store_requires_confirmation(mock_client):
       """store delete가 확인 프롬프트를 표시하는지 테스트한다."""
       result = runner.invoke(
           app,
           ["store", "delete", "fileSearchStores/test"],
           input="n\n",
       )
       mock_client.file_search_stores.delete.assert_not_called()
   ```

4. **모델 테스트** (`tests/unit/test_models.py`)
   ```python
   from file_search.models.schemas import SearchResponse, Citation

   def test_search_response_parsing():
       """SearchResponse 모델이 올바르게 파싱되는지 테스트한다."""
       data = {
           "answer": "Q3 매출은 100억원입니다.",
           "citations": [
               {"title": "Q3_report.pdf", "content": "3분기 매출 실적..."}
           ],
           "model": "gemini-2.5-flash",
       }
       response = SearchResponse.model_validate(data)
       assert response.answer == "Q3 매출은 100억원입니다."
       assert len(response.citations) == 1
       assert response.citations[0].title == "Q3_report.pdf"

   def test_citation_optional_fields():
       """Citation의 선택적 필드가 None으로 처리되는지 테스트한다."""
       citation = Citation.model_validate({})
       assert citation.title is None
       assert citation.content is None
   ```

5. **pyproject.toml에 도구 설정 추가**
   ```toml
   [tool.mypy]
   python_version = "3.12"
   strict = true
   warn_return_any = true

   [tool.ruff]
   target-version = "py312"
   line-length = 100

   [tool.ruff.lint]
   select = ["E", "F", "I", "N", "UP", "B", "SIM"]

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   ```

6. **실행 명령어 정리**
   ```bash
   # 테스트 실행
   uv run pytest -v

   # 타입 체크
   uv run mypy src/

   # 린트
   uv run ruff check src/

   # 포맷
   uv run ruff format src/

   # 전체 검증 (CI에서 사용)
   uv run ruff check src/ && uv run mypy src/ && uv run pytest -v
   ```

### 체크리스트
- [ ] `uv run pytest`로 모든 테스트가 통과한다
- [ ] API 호출을 모킹하여 외부 의존성 없이 테스트할 수 있다
- [ ] `uv run mypy src/`로 타입 에러가 없다
- [ ] `uv run ruff check src/`로 린트 에러가 없다
- [ ] `uv run ruff format --check src/`로 포맷이 일관적이다

---

## 최종 CLI 명령어 요약

```bash
# Store 관리
fsearch store create <이름>           # Store 생성
fsearch store list                    # Store 목록 조회
fsearch store info <name>             # Store 상세 정보
fsearch store rename <name> <새이름>   # Store 이름 변경
fsearch store delete <name> [-f]      # Store 삭제
fsearch store purge [-f]              # 전체 Store 삭제

# 파일 관리
fsearch file upload <파일> -s <store> [--meta key=value]  # 파일 업로드
fsearch file list -s <store>                               # 파일 목록 조회
fsearch file delete <name> -s <store> [-f]                 # 파일 삭제

# 검색
fsearch query "질문" -s <store> [--filter key=value]  # 문서 기반 질의
fsearch chat -s <store>                                # 대화형 검색 모드
```

## 비용 참고

| 항목 | 비용 |
|------|------|
| 파일 인덱싱 (임베딩 생성) | $0.15 / 1M 토큰 |
| 스토리지 | 무료 |
| 쿼리 시 임베딩 | 무료 |
| 검색된 문서 토큰 | 일반 컨텍스트 토큰 비용과 동일 |

### 용량 제한 (티어별)

| 티어 | 최대 저장 용량 |
|------|-------------|
| Free | 1 GB |
| Tier 1 | 10 GB |
| Tier 2 | 100 GB |
| Tier 3 | 1 TB |

- 파일당 최대 크기: 100 MB

## 참고 자료

- [Gemini File Search 공식 문서](https://ai.google.dev/gemini-api/docs/file-search)
- [Google AI Studio](https://aistudio.google.com)
- [google-genai Python SDK](https://pypi.org/project/google-genai/)
- [Typer 공식 문서](https://typer.tiangolo.com)
- [Rich 공식 문서](https://rich.readthedocs.io)
- [Pydantic 공식 문서](https://docs.pydantic.dev)
- [pytest 공식 문서](https://docs.pytest.org)
- [uv 공식 문서](https://docs.astral.sh/uv/)
- [mise 공식 문서](https://mise.jdx.dev)
- [mypy 공식 문서](https://mypy.readthedocs.io)
- [ruff 공식 문서](https://docs.astral.sh/ruff)
