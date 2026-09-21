"""
02 -- THE EASY CLIENT, EXPLAINED STEP BY STEP
================================================
Before jumping into the one-line pattern you'll see everywhere in this
course -- "async with Client(...) as client:" -- let's break down
exactly what a client needs to do, in plain English, one step at a time.

WHAT A CLIENT ACTUALLY NEEDS TO DO (five steps, nothing more):
  1. START the server (or connect to one already running)
  2. SAY HELLO -- the handshake from the Lifecycle video
  3. ASK what tools exist
  4. USE one of them
  5. SAY GOODBYE -- close the connection cleanly, even if something broke

That's the whole job. Everything below is just two different ways of
writing those same five steps.

WHY DOES THE CODE LOOK LIKE "async with Client(...) as client:"?
--------------------------------------------------------------------
You could write this the "manual" way, spelling out every step:

    client = Client("../main.py")
    await client.__aenter__()          # steps 1 + 2: start + handshake
    try:
        ... use the client here ...     # steps 3 + 4
    finally:
        await client.__aexit__(None, None, None)   # step 5 -- ALWAYS runs

That works. But it's easy to get wrong -- forget that "finally" block,
and a script that crashes halfway through leaves the server subprocess
running in the background forever, with nobody around to close it.

Python's "async with" does exactly that manual version FOR you,
automatically, and it GUARANTEES step 5 happens no matter what:

    async with Client("../main.py") as client:
        ... use the client here ...
    # step 5 already happened here automatically, even if something above failed

So "async with" isn't a new concept to learn -- it's just "always clean
up properly," written in one line instead of five. Both versions below
do the identical five steps. Run this file and watch them do the same
thing, two different ways.
"""
import asyncio
import sys
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
SERVER_PARAMS = StdioTransport(
    command=str(PROJECT_PYTHON if PROJECT_PYTHON.exists() else sys.executable),
    args=["-m", "timetracker.main"],
    cwd=str(PROJECT_ROOT),
)


async def the_manual_way():
    """Not how you'll normally write this -- shown once, so 'async with' stops looking like magic."""
    print("--- THE MANUAL WAY (for understanding only) ---")
    client = Client(SERVER_PARAMS)

    await client.__aenter__()  # steps 1 + 2: start the server, do the handshake
    try:
        tools = await client.list_tools()  # step 3: ask what's available
        print("Tools:", [t.name for t in tools])

        result = await client.call_tool("list_projects", {})  # step 4: use one
        print("Result:", result)
    finally:
        await client.__aexit__(None, None, None)  # step 5: ALWAYS runs, even on error
        print("Cleaned up properly -- even without 'async with'.")


async def the_real_way():
    """This is what you'll actually write, every time, from here on in this course."""
    print("\n--- THE REAL WAY (what every later file actually uses) ---")
    async with Client(SERVER_PARAMS) as client:  # steps 1, 2, AND 5 (cleanup), handled for you
        tools = await client.list_tools()  # step 3
        print("Tools:", [t.name for t in tools])

        result = await client.call_tool("list_projects", {})  # step 4
        print("Result:", result)
    # step 5 (cleanup) already happened here, automatically, the instant the block ended


async def main():
    await the_manual_way()
    await the_real_way()


if __name__ == "__main__":
    asyncio.run(main())