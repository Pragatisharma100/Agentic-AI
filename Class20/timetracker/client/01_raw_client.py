"""
01 -- THE RAW CLIENT
=====================
The most explicit, most verbose way to talk to an MCP server. Nothing
here is hidden -- every step the protocol actually needs is written out
by hand, so you can see exactly what happens.

!! KNOWN BUG, PLEASE READ BEFORE RUNNING !!
There is a real, currently open bug where the line `stdio_client(...)`
below hangs FOREVER on macOS specifically (official SDK issue #1452).
If this script just sits there and never prints anything, that is why --
it is not a mistake in this code. Skip straight to 02, which does the
exact same thing safely.

SETUP:
    pip install mcp

RUN:
    uv run python 01_raw_client.py
"""
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

# This describes HOW to start the server -- it does not start it yet.
server_params = StdioServerParameters(
    command=str(PROJECT_PYTHON if PROJECT_PYTHON.exists() else sys.executable),
    args=["-m", "timetracker.main"],
    cwd=str(PROJECT_ROOT),
)


async def main():
    # STEP 1: open the connection.
    async with stdio_client(server_params) as (read_stream, write_stream):
        # STEP 2: wrap a "session" around those two raw streams.
        async with ClientSession(read_stream, write_stream) as session:
            # STEP 3: the handshake.
            await session.initialize()
            print("Connected! Handshake complete.")

            # STEP 4: ask what tools exist.
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]
            print("Tools this server offers:", tool_names)

            # STEP 5: call one of them for real.
            result = await session.call_tool("list_projects", arguments={})
            print("Result of calling list_projects:", result)


if __name__ == "__main__":
    asyncio.run(main())