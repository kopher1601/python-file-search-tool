# Python 학습 노트

## 1. `__pycache__/` 란?

Python이 `.py` 파일을 실행할 때, 내부적으로 **바이트코드(bytecode)** 로 컴파일한다.
이 컴파일된 결과물(`.pyc` 파일)을 저장하는 폴더가 `__pycache__/`이다.

```
__pycache__/
├── client.cpython-312.pyc    ← client.py를 Python 3.12로 컴파일한 결과
└── app.cpython-312.pyc
```

### 왜 존재하는가?

- 다음 실행 시 컴파일 과정을 건너뛰어 **실행 속도를 높이기 위해**
- `.py` 파일이 변경되면 Python이 자동으로 다시 컴파일한다

### 신경 써야 하나?

**No.** Python이 알아서 관리한다. 단, `.gitignore`에 추가해서 git에 올라가지 않도록 하자.

```gitignore
__pycache__/
```

---

## 2. `__init__.py` 란?

폴더를 Python **패키지(package)** 로 인식시키는 파일이다.

### 예시

```
file_search/
├── __init__.py      ← 이게 있어야 "file_search"를 패키지로 import 가능
├── core/
│   ├── __init__.py  ← 이게 있어야 "file_search.core"로 import 가능
│   └── client.py
└── cli/
    ├── __init__.py
    └── app.py
```

`__init__.py`가 없으면 아래 같은 import가 동작하지 않을 수 있다:

```python
from file_search.core.client import get_client
```

### 신경 써야 하나?

**약간 Yes.** 패키지 구조를 만들 때 필요하다. 하지만 대부분의 경우 **빈 파일**로 놔두면 된다.

> 참고: Python 3.3+ 에서는 `__init__.py` 없이도 "namespace package"로 동작할 수 있지만,
> 명시적으로 넣어주는 것이 일반적인 관례이다.

---

## 3. `uv` 란?

[uv](https://docs.astral.sh/uv/)는 Rust로 만든 **초고속 Python 패키지 매니저 & 프로젝트 관리 도구**이다.
기존의 `pip`, `pip-tools`, `virtualenv`, `poetry` 등을 **하나로 통합**한 도구라고 보면 된다.

### uv가 하는 일

| 기능 | 기존 도구 | uv 명령어 |
|---|---|---|
| 패키지 설치 | `pip install` | `uv add` |
| 가상환경 생성 | `python -m venv` | `uv venv` (또는 자동 생성) |
| 의존성 잠금 (lock) | `pip-tools`, `poetry lock` | `uv lock` |
| 스크립트 실행 | `python` | `uv run python ...` |
| Python 버전 관리 | `pyenv` | `uv python install 3.12` |

### 왜 uv를 쓰는가?

1. **빠르다** — Rust로 작성되어 pip보다 10~100배 빠름
2. **통합** — 가상환경 생성, 패키지 설치, lock 파일 관리를 하나의 도구로
3. **재현성** — `uv.lock` 파일로 모든 의존성 버전을 정확히 고정

### `uv run` 이란?

```bash
uv run python script.py
```

이 명령은 내부적으로 다음을 수행한다:

1. `.venv` 가상환경이 없으면 **자동으로 생성**
2. `pyproject.toml`에 명시된 의존성이 설치 안 되어 있으면 **자동으로 설치**
3. 가상환경 안에서 `python script.py`를 **실행**

즉, `uv run`은 "환경 세팅 + 실행"을 한 번에 해주는 명령이다.

### 주요 파일들

- **`pyproject.toml`** — 프로젝트 설정과 의존성을 정의하는 파일 (Java의 `build.gradle`, Go의 `go.mod`에 해당)
- **`uv.lock`** — 의존성의 정확한 버전을 고정하는 lock 파일 (Go의 `go.sum`에 해당)

---

## 4. `mypy` 란?

[mypy](https://mypy-lang.org/)는 Python의 **정적 타입 검사 도구**이다.

### Python은 동적 타입 언어다

```python
x = 10       # x는 int
x = "hello"  # 갑자기 str로 바뀜 — Python은 허용함
```

Java나 Go에서는 이런 코드가 컴파일 에러가 나지만, Python은 실행 시점까지 에러를 모른다.

### mypy의 역할

Python 3.5+에서 추가된 **타입 힌트(type hint)** 를 분석해서, 실행하기 전에 타입 오류를 찾아준다.

```python
def get_client() -> genai.Client:   # 반환 타입을 명시
    api_key: str = os.getenv("GEMINI_API_KEY")  # 변수 타입을 명시
    return genai.Client(api_key=api_key)
```

```bash
$ uv run mypy src/
# 타입이 맞지 않는 코드가 있으면 에러를 출력
```

### 다른 언어와 비교

| 언어 | 타입 검사 | 시점 |
|---|---|---|
| Java | 컴파일러가 강제 | 컴파일 시 |
| Go | 컴파일러가 강제 | 컴파일 시 |
| Python | **선택적** (mypy 같은 도구 사용) | 실행 전 별도 실행 |
| TypeScript | tsc 컴파일러 | 컴파일 시 |

mypy는 Python에 Java/Go 같은 **컴파일 타임 타입 안전성**을 부분적으로 가져다주는 도구이다.
사용은 선택이지만, 규모가 큰 프로젝트에서는 거의 필수로 쓰인다.

---

## 5. Python 가상환경 (Virtual Environment)

### 가상환경이란?

프로젝트마다 **독립된 Python 패키지 공간**을 만드는 것이다.

### 왜 필요한가?

```
프로젝트 A: google-genai 1.60 필요
프로젝트 B: google-genai 2.0 필요
```

가상환경 없이 전역으로 패키지를 설치하면, 두 프로젝트가 **같은 패키지의 다른 버전**을 동시에 사용할 수 없다.
가상환경은 프로젝트마다 독립된 `site-packages` 폴더를 만들어서 이 문제를 해결한다.

### 다른 언어와 비교

#### Java (Gradle/Maven)

```
my-java-project/
├── build.gradle       ← 의존성 정의
└── .gradle/           ← 로컬 캐시
```

- Java는 프로젝트별로 의존성을 `build.gradle`에 선언하고, 빌드 도구가 알아서 관리한다.
- 전역 `.m2/repository`에 캐시하지만, **클래스패스(classpath)** 로 프로젝트별 격리가 된다.
- JDK 자체의 버전 관리는 별도 (SDKMAN 등)

#### Go (Go Modules)

```
my-go-project/
├── go.mod             ← 의존성 정의
├── go.sum             ← 버전 잠금
└── vendor/            ← (선택) 로컬 의존성 복사
```

- Go는 `go.mod`로 프로젝트별 의존성을 관리한다.
- 전역 `$GOPATH/pkg/mod`에 캐시하지만, **모듈 시스템이 자동으로 버전을 격리**한다.
- 가상환경 같은 별도의 개념이 필요 없다.

#### Python

```
my-python-project/
├── pyproject.toml     ← 의존성 정의
├── uv.lock            ← 버전 잠금
└── .venv/             ← 가상환경 (독립된 패키지 공간)
```

- Python은 기본적으로 패키지를 **전역(시스템)** 에 설치한다.
- 프로젝트별 격리를 하려면 **가상환경을 명시적으로 만들어야** 한다.
- 이것이 Java나 Go와의 가장 큰 차이점이다.

### 핵심 차이 요약

| 언어 | 의존성 격리 방식 | 별도 환경 필요? |
|---|---|---|
| Java | 클래스패스로 자동 격리 | No |
| Go | 모듈 시스템으로 자동 격리 | No |
| Node.js | `node_modules/` 폴더로 자동 격리 | No |
| **Python** | **가상환경을 직접 만들어야 함** | **Yes** |

Python의 가상환경은 다른 언어에서는 빌드 도구가 자동으로 해주는 일을
개발자가 명시적으로 해야 하는 것이다. `uv`를 쓰면 이 과정이 자동화된다.

---

## 6. `.venv/` 란?

`.venv/`는 가상환경의 **실제 폴더**이다. 프로젝트 루트에 생성된다.

```
.venv/
├── bin/               ← 가상환경의 python, pip 등 실행 파일
│   ├── python         ← 이 프로젝트 전용 Python 인터프리터 (심볼릭 링크)
│   └── activate       ← 가상환경 활성화 스크립트
├── lib/
│   └── python3.12/
│       └── site-packages/   ← 이 프로젝트에 설치된 패키지들
│           ├── google/
│           ├── pydantic/
│           └── dotenv/
└── pyvenv.cfg         ← 가상환경 설정
```

### 가상환경 활성화/비활성화

```bash
# 수동 활성화
source .venv/bin/activate

# 비활성화
deactivate

# uv를 쓰면 활성화 없이 바로 실행 가능
uv run python script.py
```

### 신경 써야 하나?

- `.venv/`는 `.gitignore`에 추가해야 한다 (용량이 크고 환경마다 다르므로)
- `uv run`을 쓰면 가상환경을 직접 활성화할 필요가 없다
- 환경이 꼬이면 `.venv/` 폴더를 삭제하고 `uv sync`로 재생성하면 된다
