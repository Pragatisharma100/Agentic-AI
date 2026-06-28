# Class 2 — Actual file list and simple summaries

This folder has only the actual Class 2 files. The previous README listed files that do not exist in this folder.

## Files and short summaries

- [`0 Basics_Python.py`](./0%20Basics_Python.py) — Python basics: variables, types, strings, and control flow.
- [`1 Data Structures.py`](./1%20Data%20Structures.py) — lists, dictionaries, tuples, and loops.
- [`2 OOP.py`](./2%20OOP.py) — classes and objects.
- [`3 Error Handling.py`](./3%20Error%20Handling.py) — try/except examples.
- [`4 Decorators.py`](./4%20Decorators.py) — how decorators work.
- [`5 Calling real api.py`](./5%20Calling%20real%20api.py) — real API call with `requests`.
- [`6 Fake ai call.py`](./6%20Fake%20ai%20call.py) — fake AI-style function.
- [`7 Ai_call_free_and_paid.py`](./7%20Ai_call_free_and_paid.py) — AI provider examples.
- [`8 Pydantic with ai.py`](./8%20Pydantic%20with%20ai.py) — Pydantic validation.
- [`9 Api call with structure.py`](./9%20Api%20call%20with%20structure.py) — API call with Pydantic.

## Why there was an error

The README previously mentioned files named `10 Tool_with_ai_call.py` through `14 Agent_with_memory.py`. Those files do not exist in this folder, so the README was wrong. This file now matches the folder contents exactly.

## How to open a file

Click any linked file name above in the README to open it in VS Code.

## How to run a file

Use `uv run` with quotes around names that have spaces:

```bash
uv run "0 Basics_Python.py"
uv run "8 Pydantic with ai.py"
uv run "9 Api call with structure.py"
```

## Setup

Install the required packages:

```bash
uv add requests pydantic python-dotenv
```

If you also want AI provider support:

```bash
uv add openai
```

Copy the example environment file:

```bash
copy .env.example .env
```

Then add your provider key to `.env` if needed.
