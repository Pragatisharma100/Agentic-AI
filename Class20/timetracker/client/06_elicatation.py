"""
06 -- CLIENT CONNECTION AND TOOL CALL
=====================================================
This client uses the current TimeTrack server and demonstrates a safe
MCP connection. The current server does not expose an elicitation tool.

A NOTE WORTH KNOWING: the newest MCP protocol revision (2026-07-28) is
stateless -- it has no back-channel at all for server-initiated requests,
so ctx.elicit() raises an error on a connection negotiated at that
version. Elicitation itself isn't gone (there's a modern "return an
InputRequiredResult and get re-invoked" pattern for it), but the simple
imperative ctx.elicit() this demo relies on only works on the classic,
session-based handshake. So we pin the client to mode="legacy" below to
force that older handshake and keep this demo working as written.

RUN:
    uv run python 06_elicatation.py
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


async def elicitation_handler(message: str, response_type, params, context):
    """
    Called BY the server, through the client, whenever a tool calls
    ctx.elicit(). In a real app with a UI, this is where you'd show a
    real dialog box. For this demo, we print the question and auto-confirm.
    """
    print(f"\n[The server is asking]: {message}")
    print("[Auto-confirming for this demo -- swap this for real input() or a UI in your own client]")
    return True


async def main():
    async with Client(TRANSPORT) as client:
        print("Connected to the current TimeTrack MCP server.")
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools])
        result = await client.call_tool("list_projects", {})
        print("Projects:", result)


if __name__ == "__main__":
    asyncio.run(main())