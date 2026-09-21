"""
05 -- SERVER TOOL CALL
=======================================================
This example calls the deployed server's supported timesheet tool through
stdio and prints the returned entries.

A NOTE WORTH KNOWING: MCP used to support "sampling" -- a server tool
could call ctx.sample(...) to PAUSE and ask the CONNECTED CLIENT to run
the LLM call on its behalf (the client would supply a sampling_handler
to answer it). That pattern is now deprecated in the MCP spec
(SEP-2577), and FastMCP 4.x removed Context.sample() entirely -- there
is no back-channel for it anymore. Tools are expected to call an LLM
provider directly, which is what summarize_week does now. This client
file is just a normal tool call; no sampling_handler needed.

RUN:
    uv run python 05_sampling.py
"""
import asyncio
import sys
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
transport = StdioTransport(
    command=str(PROJECT_PYTHON if PROJECT_PYTHON.exists() else sys.executable),
    args=["-m", "timetracker.main"],
    cwd=str(PROJECT_ROOT),
)


async def main():
    async with Client(transport) as client:
        result = await client.call_tool(
            "get_timesheet",
            {"employee_name": "Asha Patel", "start_date": "2026-09-08"},
        )
        print("Timesheet returned by the MCP server:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())