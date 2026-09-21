"""
03 -- CONNECTING TO A REAL, DEPLOYED SERVER OVER HTTP
========================================================
Every file so far launched main.py as a LOCAL subprocess over stdio.
This file connects to the EXACT SAME TimeTrack server -- except this one
is already running, permanently, on the actual internet. It was deployed
earlier in this course and is live right now at the URL below.

THE ONLY THING THAT CHANGES: you pass a URL instead of a file path.
FastMCP detects the difference automatically and switches from stdio to
Streamable HTTP -- same tools, same behavior, completely different road,
exactly like the Transport Layer video explained.

No local server to start. No subprocess. Just a URL, reachable from
anywhere, by anyone -- not just you.

SETUP:
    pip install fastmcp

RUN:
    uv run python 03_fastmcp_client_http.py
"""
import asyncio
from fastmcp import Client

# This is the deployed TimeTrack MCP endpoint.
# The /mcp suffix is required because FastAPI mounts the MCP app there.
#   list_projects()        -> ["Client Onboarding", "Internal Tools", "Website Redesign"]
#   get_project_summary("Website Redesign")
#                           -> total_hours: 19.0, Asha Patel: 13.5, Rahul Mehta: 5.5
SERVER_URL = "https://time-tracker-steel-psi.vercel.app/mcp"


async def main():
    # Same five steps as every previous file -- start, handshake, ask,
    # use, clean up. The ONLY difference from 02's "the_real_way()" is
    # what's inside Client(...): a URL instead of "../main.py".
    async with Client(SERVER_URL) as client:
        print(f"Connected to {SERVER_URL}")
        print("(over the real internet -- no subprocess was started)")

        tools = await client.list_tools()
        print("\nTools this remote server offers:", [t.name for t in tools])

        projects = await client.call_tool("list_projects", {})
        print("\nProjects, straight from the live deployment:", projects)

        summary = await client.call_tool("get_project_summary", {"project": "Website Redesign"})
        print("Live project summary:", summary)


if __name__ == "__main__":
    asyncio.run(main())