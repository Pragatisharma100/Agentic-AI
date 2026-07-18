# Class 7 - Agentic AI 3.0

## Overview

This class demonstrates a simple LangChain agent setup using a local tool function and the `create_agent` API. The notebook `setup_check.ipynb` verifies that the OpenAI API key is loaded correctly and that the agent can invoke a tool.

## Files

- `setup_check.ipynb`: Jupyter notebook used for environment validation and agent setup.

## Requirements

- Python 3.10+
- `python-dotenv`
- `langchain`
- OpenAI API key set in `.env` as `OPENAI_API_KEY`

## Setup

1. Install dependencies:
   - `pip install python-dotenv langchain`
2. Create a `.env` file in the project root:
   - `OPENAI_API_KEY=your_openai_api_key`

## Usage

- Run `setup_check.ipynb` in Jupyter or VS Code.
- The notebook loads environment variables and prints a sample weather response from the agent.

## Notes

- The `get_weather` tool is a placeholder function.
- The agent configuration uses `model="openai:gpt-5.5"` and a system prompt to define behavior.
- Confirm the API key is loaded correctly before invoking the agent.