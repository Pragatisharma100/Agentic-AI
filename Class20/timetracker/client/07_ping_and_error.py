"""
07 -- PING AND A REAL ERROR
=============================
Two of the "special cases" from the Lifecycle video, now actually
happening instead of being a JSON example on a slide.

A NOTE WORTH KNOWING: `ping` is removed as of the newest MCP protocol
revision (2026-07-28) -- it only works under the classic, session-based
handshake. So, same as the elicitation demo, we pin mode="legacy" here
to keep client.ping() working as written.

RUN:
    python3 07_ping_and_errors.py
"""
import asyncio
import sys
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
TRANSPORT = StdioTransport(
    command=str(PROJECT_PYTHON if PROJECT_PYTHON.exists() else sys.executable),
    args=["-m", "timetracker.main"],
    cwd=str(PROJECT_ROOT),
)


async def demo_ping():
    print("--- PING: just checking the connection is alive ---")
    async with Client(TRANSPORT, mode="legacy") as client:
        result = await client.ping()
        print("Server responded:", result)


async def demo_real_error():
    print("\n--- A REAL ERROR, TRIGGERED ON PURPOSE ---")
    async with Client(TRANSPORT, mode="legacy") as client:
        try:
            # "Nonexistent Project" was never logged against -- this makes
            # get_project_summary's own ValueError fire for real, surfacing
            # back to us as a genuine protocol error.
            await client.call_tool("get_project_summary", {"project": "Nonexistent Project"})
        except Exception as e:
            print("Caught a real error response:", e)


async def main():
    await demo_ping()
    await demo_real_error()


if __name__ == "__main__":
    asyncio.run(main())