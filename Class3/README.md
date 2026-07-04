# Class 3 — Pydantic and Structured Data for AI

This folder focuses on one of the most important tools in modern AI development: Pydantic.

Pydantic helps you validate, shape, and trust data coming from users, APIs, and large language models.

## What you will learn

- why Pydantic exists and why validation matters
- how to define models with BaseModel
- how to add field constraints and custom validators
- how to work with nested models
- how to use computed fields and serialization
- how to use Pydantic with FastAPI
- how to validate LLM outputs for safer AI applications

## Files in this class

- [Pydantic_Complete_Reference.ipynb](./Pydantic_Complete_Reference.ipynb) — a notebook version of the same guide with step-by-step examples.
- [LLM_Foundation_Notes.ipynb](./LLM_Foundation_Notes.ipynb) — beginner-friendly notes about LLM basics such as tokens, embeddings, context window, and parameters.

## How to open the files

- Open any file directly in VS Code.
- For notebooks, use the Python kernel in Jupyter support.

## How to run the Python file

From the project root, run:

```bash
uv run "Class3/Pydantic_Complete_Reference"
```

## Setup

Install the required packages if needed:

```bash
uv add pydantic pydantic-settings fastapi
```

If you want to experiment with LLM-related examples, you can also add:

```bash
uv add openai anthropic
```

## Notes

- Pydantic is especially useful when working with AI outputs because LLMs often return messy or inconsistent data.
- The notebooks are designed to be read like study notes and run like mini examples.
