"""
09 -- PROGRESS NOTIFICATIONS, WATCHED LIVE
=============================================
main.py's "slow_tool" reports its progress as it works. Here we give the
client a progress_handler, so every update prints the moment it arrives
-- instead of the client just sitting there for 5 seconds wondering if
anything is happening.

NOTE: "progress_handler" is also set when you CREATE the Client, not
per-call -- same rule as timeout in the previous file.

RUN:
    python3 09_progress_notifications.py
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

async def on_progress(progress: float, total: float | None, message: str | None):
    print(f"  progress update: {progress}/{total} -- {message}")


async def main():
    print("--- Calling the 5-second tool, watching progress arrive live ---")
    async with Client(TRANSPORT, progress_handler=on_progress) as client:
        result = await client.call_tool("slow_tool", {})
        print("Final result:", result)


if __name__ == "__main__":
    asyncio.run(main())