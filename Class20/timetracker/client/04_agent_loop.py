"""
04 -- A REAL AGENT LOOP, NO FRAMEWORK
=======================================
This is what "an AI agent using MCP" actually is, underneath every
framework that promises to do it for you. No LangChain, nothing hidden --
just: ask the LLM, check if it wants a tool, call it for real through
MCP, hand the result back, repeat.

SETUP:
    uv add openai python-dotenv
    set GROQ_API_KEY=your-groq-key-here

RUN:
    python3 04_agent_loop.py
"""
import asyncio
import os
import sys
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).with_name(".env"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
SERVER_TRANSPORT = StdioTransport(
    command=str(PROJECT_PYTHON if PROJECT_PYTHON.exists() else sys.executable),
    args=["-m", "timetracker.main"],
    cwd=str(PROJECT_ROOT),
)


def mcp_tools_to_openai_format(mcp_tools) -> list[dict]:
    """
    MCP describes a tool one way. Groq's OpenAI-compatible API expects the
    tool schema inside a function wrapper.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]


async def run_one_tool_call(mcp_client: Client, block) -> dict:
    """Actually calls one tool through MCP, and packages the result the
    way an OpenAI-compatible API expects it to come back."""
    print(f"  -> calling {block.function.name} with {block.function.arguments}")
    import json

    arguments = json.loads(block.function.arguments)
    result = await mcp_client.call_tool(block.function.name, arguments)
    return {
        "role": "tool",
        "tool_call_id": block.id,
        "content": str(result),
    }


async def run_agent_loop(user_message: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add your Groq key to client/.env or the terminal environment.")
    groq_client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    async with Client(SERVER_TRANSPORT) as mcp_client:
        mcp_tools = await mcp_client.list_tools()
        groq_tools = mcp_tools_to_openai_format(mcp_tools)

        # This list is the entire "memory" of the conversation. Every
        # question, every tool result, gets appended here and sent back
        # on the NEXT request -- the LLM itself remembers nothing between
        # calls; this list is doing all the remembering.
        messages = [{"role": "user", "content": user_message}]

        while True:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=1024,
                tools=groq_tools,
                messages=messages,
            )

            message = response.choices[0].message
            if not message.tool_calls:
                final_text = message.content or ""
                print("\nFinal answer:", final_text)
                return

            messages.append(message.model_dump(exclude_none=True))

            tool_results = [
                await run_one_tool_call(mcp_client, block)
                for block in message.tool_calls
            ]

            messages.extend(tool_results)


if __name__ == "__main__":
    asyncio.run(run_agent_loop(
        "Hi."
    ))