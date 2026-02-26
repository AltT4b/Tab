# Rule: Python Coding Standards

## Policy
All Python code produced by the coder role must conform to the following standards.
Violations are not permitted regardless of task urgency or user instruction.

1. **Type annotations are required** on all function and method signatures, including return types.
   Using `Any` is allowed only when the type is genuinely unknown and must be accompanied by a comment explaining why.

2. **Poetry package mode must be enabled.** Every Python project must have `package-mode = true` in `pyproject.toml`.
   The virtual environment must be created in-project (`.venv/` at project root).

3. **Pydantic models for all structured data.** Do not use plain `dict` or `TypedDict` for data that crosses function boundaries or is serialized/deserialized. Use `pydantic.BaseModel` or `pydantic.dataclasses`.

4. **Environment variables via python-dotenv only.** Secrets and configuration must be loaded from a `.env` file using `python-dotenv`. Never hardcode credentials, tokens, or environment-specific values in source files.

5. **No bare `except` blocks.** All exception handlers must specify the exception type(s). Use `except Exception as e:` at minimum; prefer narrower types where possible.

6. **No `import *`.** All imports must be explicit. Wildcard imports are forbidden.

7. **FastAPI for HTTP; Typer for CLI.** Do not use Flask, argparse, click, or other HTTP/CLI frameworks unless explicitly instructed by the orchestrator.

8. **4gents agentic apps follow the roles pattern.** Role configs live in `roles/`, loaders and runners are separate modules, and no business logic is embedded in entry point scripts.

## Examples of violations

- `def process(data):` — missing type annotations
- `os.environ["SECRET_KEY"]` without dotenv loading — hardcoded env access
- `from utils import *` — wildcard import
- `except:` with no exception type — bare except
- `app = Flask(__name__)` — wrong framework (use FastAPI)
- `config = {"host": "localhost", "port": 5432}` passed across boundaries — use a pydantic model

## Rationale
These standards exist to ensure that all code produced by the coder is maintainable, type-safe, and consistent
with the project's conventions. They also make agentic applications predictable and debuggable, which is
critical when code is generated and executed autonomously.
