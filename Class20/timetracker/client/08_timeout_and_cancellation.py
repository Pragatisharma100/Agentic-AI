"""
08 -- TIMEOUT, WHICH TRIGGERS A REAL CANCELLATION
====================================================
main.py's "slow_tool" deliberately takes about 5 seconds. Here, we
connect with a much shorter timeout on purpose, so it actually times
out -- and watch what that triggers.

NOTE: "timeout" is set when you CREATE the Client, not as an argument
to call_tool() itself -- verified against FastMCP's own current
documentation.

RUN:
    python3 08_timeout_and_cancellation.py
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

async def main():
    print("--- Connecting with a 1-second timeout, calling a ~5-second tool ---")
    async with Client(TRANSPORT, timeout=1.0) as client:
        try:
            await client.call_tool("slow_tool", {})
        except Exception as e:
            print("Timed out and was cancelled, exactly as expected:", e)


if __name__ == "__main__":
    asyncio.run(main())