# Class 7 - Agentic AI 3.0

## Overview

This module lives in `Class7-Langchain` and includes:
- `setup_check.ipynb` — environment and agent setup validation
- `04_05_prompt_templates_structured_output_student_notes.ipynb` — prompt templates and structured output
- `shortnotes.py` — concise class notes and reminders

## What this class teaches

- How to load environment variables safely with `python-dotenv`
- How to create a simple LangChain agent using `create_agent`
- How to define reusable prompt templates with `ChatPromptTemplate`
- How to enforce structured model output with `with_structured_output()`
- The difference between `ProviderStrategy` and `ToolStrategy`
- Why `.gitignore` is required for sensitive files like `.env`

## Requirements

- Python 3.10+
- `langchain`
- `langchain-openai`
- `python-dotenv`
- `pydantic`

## Setup

1. Install dependencies:
   - `pip install langchain langchain-openai python-dotenv pydantic`
2. Create a `.env` file in the project folder:
   - `OPENAI_API_KEY=your_openai_api_key`
3. Confirm `.env` is listed in `.gitignore`

## Usage

- Open `setup_check.ipynb` and run the cells to verify the environment and agent.
- Open `04_05_prompt_templates_structured_output_student_notes.ipynb` and run the notebook to learn prompt templates and structured output.

## Notes

- `setup_check.ipynb` uses a placeholder tool `get_weather(city: str)` to demonstrate tool binding.
- `04_05_prompt_templates_structured_output_student_notes.ipynb` shows how to:
  - build prompt templates with `{variable}` placeholders
  - chain prompts into a model with `|`
  - convert model output into a validated Pydantic object
- `.gitignore` prevents new sensitive files from being tracked, but it does not remove files already committed.
- If a sensitive file was committed, use:
  - `git rm --cached path/to/file`
  - commit the change
- Keep API keys private and do not commit `.env`.
