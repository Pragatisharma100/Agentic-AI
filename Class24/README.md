# 🔌 Class 24: Model Context Protocol (MCP) with LangChain — Hands-On Implementation

**Author:** Pragati  
**Course:** Agentic AI Specialization  
**Date:** 03 October 2026

---

## 📋 Table of Contents
1. [Quick Updates](#-quick-updates)
2. [Why We Moved from Colab to VS Code](#-why-we-moved-from-colab-to-vs-code)
3. [The Big Change: LangChain MCP (New) vs MCP Adapter (Old)](#-the-big-change-langchain-mcp-new-vs-mcp-adapter-old)
4. [Project Setup](#-project-setup)
5. [The CineBot MCP Server](#-the-cinebot-mcp-server)
6. [Connecting to the MCP Server](#-connecting-to-the-mcp-server)
7. [Listing Tools](#-listing-tools)
8. [Calling a Tool Directly (Without an Agent)](#-calling-a-tool-directly-without-an-agent)
9. [Calling a Tool Through an Agent](#-calling-a-tool-through-an-agent)
10. [Structured Output — Content vs Artifact](#-structured-output--content-vs-artifact)
11. [The Language the Agent Speaks](#-the-language-the-agent-speaks)
12. [Error Handling — Two Failure Modes](#-error-handling--two-failure-modes)
13. [Tool Metadata & Annotations](#-tool-metadata--annotations)
14. [Human-in-the-Loop with Destructive Tools](#-human-in-the-loop-with-destructive-tools)
15. [Elicitation — Server-Initiated Questions](#-elicitation--server-initiated-questions)
16. [Connecting to Multiple MCP Servers](#-connecting-to-multiple-mcp-servers)
17. [Authentication — The Four Patterns](#-authentication--the-four-patterns)
18. [Context7 — Real MCP Server Demo](#-context7--real-mcp-server-demo)
19. [One Agent, Three MCP Servers](#-one-agent-three-mcp-servers)
20. [Multi-Agent Patterns — Practical](#-multi-agent-patterns--practical)
21. [Subagents, Handoffs, Skills, Router](#-subagents-handoffs-skills-router)
22. [The Agent Flow Extension](#-the-agent-flow-extension)
23. [What's New vs Deprecated](#-whats-new-vs-deprecated)
24. [Live Q&A Highlights](#-live-qa-highlights)
25. [Key Pointers to Remember](#-key-pointers-to-remember)
26. [Action Items](#-action-items)
27. [Summary](#-summary)

---

## 📰 Quick Updates

- 🎯 **Today's scope:** Full practical implementation of MCP in LangChain — connecting agents to MCP servers, tool discovery, direct tool invocation, agent-driven invocation, structured output, error handling, human-in-the-loop with destructive tools, elicitation, connecting to multiple servers, authentication, and a real Context7 demo.
- 🩹 **The big change:** LangChain moved from `langchain-mcp-adapter` to `langchain-mcp` just a few weeks before class. It's still in **beta** — importing it raises a beta warning. Most code is the same, but the import path and a few APIs changed.
- 🗺️ **Roadmap:** Next class starts the Meridian AI project on GCP. After that project, another GCP project, then LangGraph. The multi-agent patterns are covered practically here as a bridge to the project.
- ⚠️ **Important:** This class was run **in VS Code, not Colab** — because stdio transport and async/sync handling don't work reliably in Colab. All code is on GitHub (Weekend 14 folder). Do a `git pull` before starting.
- 📦 **New content:** Multi-agent notebook with subagents, handoffs, skills, and router — built with Mermaid diagrams and detailed explanations. The Agent Flow extension for Claude Code is also introduced.

---

## 🖥️ Why We Moved from Colab to VS Code

**Analogy:** Think of Colab like a **rented kitchen** — you get the tools, but you can't install your own appliances. VS Code is your **own kitchen** — you can wire up anything, including the pipes (stdio) that Colab doesn't let you touch.

| Reason | What It Means |
|---|---|
| **stdio transport** | Colab runs on a remote machine (not yours). Local MCP servers that use stdio need to run on **your** machine. |
| **Async/sync issues** | Colab's event loop conflicts with async MCP clients. VS Code runs cleanly. |
| **File system access** | Local MCP servers need to read `cinebot_mcp_server.py` from disk. Colab can't do that reliably. |

> *"We are not doing this on Colab because there were a few issues — if you try to run MCP STDIO in STDIO, it is not out-of-the-box supported in the right way in Colab, because it is running on the machine which is not ours, while we use local MCP."*

**The rule:** When you're connecting to **local MCP servers**, use VS Code. When you're connecting to **remote HTTP MCP servers**, Colab is fine.

---

## 🔀 The Big Change: LangChain MCP (New) vs MCP Adapter (Old)

**Analogy:** Think of it like **a library being reorganized**. The books (concepts) are the same, but they moved from one shelf (old package) to another (new package). If you're following old tutorials, you'll look on the wrong shelf.

| Aspect | Old (`langchain-mcp-adapter`) | New (`langchain-mcp`) |
|---|---|---|
| **Package** | `langchain-mcp-adapter` | `langchain-mcp` |
| **Import** | `from langchain_mcp_adapter import MultiServerMCPClient` | `from langchain_mcp import MCPAdapter` |
| **Status** | Stable | **Beta** — raises a warning on import |
| **When it changed** | Earlier in 2026 | ~2-3 weeks before this class |
| **What's supported** | Tools only | Tools only (resources and prompts are NOT exposed via the adapter — you must drop down to the FastMCP client) |
| **What's underneath** | FastMCP | FastMCP (same) |

> *"They have moved away from this LangChain MCP adapter, and now they are using LangChain MCP. And it is so recent that you get a warning that, hey, this is very new, or this is the newer one, and this is how it will happen."*

**Why you should care:** Every tutorial on YouTube, every blog post older than ~3 weeks, is still showing `langchain-mcp-adapter`. If you copy that code, it won't run cleanly. The class uses the **new** `langchain-mcp`.

**The import warning you'll see:**

```
LangChainBetaWarning: The `langchain_mcp` namespace is in beta.
```

This is expected. Ignore it. The code works.

> *"It is still in beta, LangChain is saying that, hey, you can use it. So they will be very, very confident that in maybe two, three weeks, they will be moving out of beta."*

---

## 🛠️ Project Setup

**The files (from the shared repo, Weekend 14 folder):**

| File | Purpose |
|---|---|
| `MCP_in_Langchain.ipynb` | Main notebook — full walkthrough |
| `cinebot_mcp_server.py` | CineBot MCP server with three tools: `check_showtime`, `cancel_booking`, `get_seat_map` |
| `cinebot_error_server.py` | MCP server that raises a validation error for booking IDs not starting with `BK` |
| `cinebot_elicit_server.py` | MCP server that asks the caller for confirmation (elicitation) |
| `.env` | Local secrets — never commit |
| `.env.example` | Template — safe to commit |

**Setup commands:**

```bash
# In the Class24 folder
uv sync

# The first cell in the notebook installs the MCP packages
# Restart the kernel, then run the remaining cells
```

**Requirements:**

```
langchain[mcp]>=1.4.0
langchain-groq
python-dotenv
rich
fastmcp
```

> *"In the latest PyProject.toml which I have given you, there is LangChain MCP >= 1.4.0. So the agenda is understanding MCP multi-agent architecture practically."*

**Note:** The class demo used `OPENAI_API_KEY` as the env var name, but the underlying model call is to Groq's `gpt-oss` (or any OpenAI-compatible endpoint). The exact provider doesn't matter — what matters is the MCP connection.

---

## 🤖 The CineBot MCP Server

**Analogy:** Think of the MCP server like a **smart vending machine**. It has three buttons (tools), and you can press any of them to get a specific result. The server doesn't care who presses the button — it just serves the tool.

**Built with FastMCP:**

```python
from fastmcp import FastMCP

mcp = FastMCP("CineBot")

@mcp.tool
def check_showtime(movie_title: str) -> str:
    """Check showtimes for a movie."""
    # Returns showtimes as text

@mcp.tool
def cancel_booking(booking_id: str) -> str:
    """Cancel a booking. Destructive — requires human confirmation."""
    # Annotated as destructive=True
    # Cancels the booking

@mcp.tool
def get_seat_map(showtime_id: str) -> dict:
    """Get the seat map for a showtime. Returns structured data."""
    # Returns a dict (not a string)
```

**Key points:**

| Aspect | Detail |
|---|---|
| **Transport** | **stdio** — the server runs as a subprocess and communicates over stdin/stdout |
| **No async needed** | The demo is synchronous — FastMCP handles the protocol |
| **Annotation** | `cancel_booking` carries `destructive_hint=True` — this is metadata the client can act on |
| **Structured output** | `get_seat_map` returns a **dict**, not a string — more on this below |

> *"This is just my local MCP server, which I will be starting. We have created it via FastMCP. It will start off an MCP server locally, STDIO. I think we have again done it very much in depth."*

---

## 🔗 Connecting to the MCP Server

**Analogy:** Think of the **MCP adapter** like a **power strip**. It's a bridge between your LangChain agent (the appliance) and the MCP server (the wall outlet). You don't wire the appliance directly to the wall — you go through the strip.

**The imports:**

```python
from pathlib import Path
from langchain_mcp import MCPAdapter
from fastmcp.client.transports import PythonStdioTransport
```

**Create the transport:**

```python
cinebot_transport = PythonStdioTransport(
    script_path="cinebot_mcp_server.py",
)
```

> *"It is just taking up this CineBot MCP server, so that it knows that, hey, this is where my file is present. Exactly the file name should match."*

**Common error you'll hit:**

```
Connection closed. During handling of the exception...
```

**Cause:** The notebook cell that uses `%%writefile` created the server file, but the server process wasn't started. When you run the connection cell, the adapter tries to spawn the server, but the file path resolution can fail if the cell was run out of order.

**Fix:** Run the `%%writefile` cell first, then the transport cell, then the connection cell — in order, without skipping.

> *"What I have done is I have created this file via this particular code. So let me just check it in. You can run the same thing and it will basically have it. If you will notice, `%%writefile` creates the file and simultaneously runs the same as well."*

---

## 📋 Listing Tools

**Once connected, ask the server: "What tools do you have?"**

```python
async with MCPAdapter(cinebot_transport) as adapter:
    tools = await adapter.list_tools()
    for tool in tools:
        print(tool.name, tool.description)
```

**Output:**

```
check_showtime  Check showtimes for a movie
cancel_booking  Cancel a booking (destructive)
get_seat_map    Get the seat map for a showtime
```

> *"Now it is able to connect to Showtime, Booking, and Get Seat Map. So I hope this is clear."*

**What this proves:** The MCP adapter is successfully talking to the MCP server over stdio. The three tools were **discovered** — this is the "tools/list" step of the MCP protocol.

---

## 🎯 Calling a Tool Directly (Without an Agent)

**Analogy:** Think of this like **pressing a button on the vending machine yourself**. No middleman. You know exactly what you want, so you just call the tool.

**The code:**

```python
async with MCPAdapter(cinebot_transport) as adapter:
    tools = await adapter.list_tools()
    showtime_tool = next(t for t in tools if t.name == "check_showtime")

    result = await showtime_tool.ainvoke({"movie_title": "Interstellar"})
    print(result)
```

**Output:**

```
Interstellar is showing at 6:00 PM, 9:15 PM.
```

> *"I am trying to make sure that I can call a tool. So I will just quickly add a markdown here: Call a tool without any AI or agent. Because that thing is a requirement. Before we jump on to say that, hey, our agent can call the tool itself, we should be able to understand the same as well."*

**Why this matters:** It proves the **tool** works, independent of any LLM. If the tool call fails, the problem is in the MCP server or connection — not in the agent. This is your **first debugging step**.

**Async gotcha:** `ainvoke` must be `await`-ed. Forgetting `await` gives `RuntimeError: coroutine was never awaited`. The class debugged this live — the fix is just adding `await` and wrapping the call in `async with`.

---

## 🧠 Calling a Tool Through an Agent

**Analogy:** Now think of the **vending machine with a helpful assistant**. You tell the assistant what you want ("I want chips"), the assistant looks at the menu (tool list), picks the right button, presses it, and hands you the chips. You don't press anything yourself.

**The code:**

```python
from langchain.agents import create_agent

async with MCPAdapter(cinebot_transport) as adapter:
    tools = await adapter.list_tools()

    agent = create_agent(
        model="openai:gpt-5-mini",   # or groq:openai/gpt-oss-120b
        tools=tools,                  # give the agent all MCP tools
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What are the showtimes for Interstellar?"}]}
    )
    print(result["messages"][-1].content)
```

**What happens internally:**

1. The agent receives the user message.
2. The agent looks at the tool list (three tools, with names and descriptions).
3. The agent decides `check_showtime` is the right tool.
4. The agent calls `check_showtime(movie_title="Interstellar")`.
5. The MCP server runs the tool.
6. The tool result comes back as a **tool message**.
7. The agent reads the tool message and writes a natural-language reply.

> *"Our agent is able to understand which tool to call. We specifically asked it, 'What are the showtimes for Interstellar?' It can go in here, it can genuinely understand this check_showtime. Then, of course, it can call the movie title. Because our MCP server is having the three tools, it is able to have the name, etc."*

**Key insight:** The agent doesn't see the MCP server. It only sees the **tool list** and the **tool messages**. The adapter does all the translation.

---

## 📦 Structured Output — Content vs Artifact

**Analogy:** Think of a **receipt with two parts**. The **content** is the summary line at the bottom ("Total: $42.50"). The **artifact** is the itemized breakdown stapled to the back. Same transaction — two levels of detail.

**When a tool returns a dict** (like `get_seat_map`), the adapter splits it into two parts:

| Field | What It Contains | Who Reads It |
|---|---|---|
| `message.content` | A **text summary** of the result | The **LLM** — this is what it "sees" |
| `message.artifact` | The **full structured data** (dict/JSON) | **Your code** — available but not fed to the LLM |

**Demo:**

```python
seat_map_tool = next(t for t in tools if t.name == "get_seat_map")
message = await seat_map_tool.ainvoke({"showtime_id": "SH001"})

print(message.content)    # Human-readable text summary
print(message.artifact)   # Full dict — {"rows": [...], "available": [...]}
```

> *"Normally we have `message.content`, which is what my model sees. When the tool returns a string, `message.content` is the text. But if I do `message.artifact`, it is actually having the exact same output, properly preserved in a JSON kind of thing as well."*

**Why this is a big deal:** If the artifact is a large JSON (say 200 rows of seat data), you might not want to send all of it to the LLM — it burns tokens and distracts the model. Instead, you can:

1. Read the artifact in a **middleware**.
2. Extract only the fields you need (e.g., "available seats count").
3. Send **that** to the LLM instead of the full JSON.

> *"Don't you think that you can just send the available rows to your LLM, by hijacking and middlewearing the concept? It will help you to save lots of tokens, rather than every time sending this complete thing."*

**This is the kind of optimization AI won't do for you.** You have to know it's possible and ask for it.

---

## 🗣️ The Language the Agent Speaks

**Analogy:** Think of it like this — if I explain the same concept in **French**, someone who only speaks English won't understand it. Same concept, wrong language. The LangChain agent only speaks **`tool_message`**. If you give it a plain string, it doesn't understand.

**What the agent understands:**

| Message Type | Understood By Agent? |
|---|---|
| `HumanMessage` | ✅ Yes |
| `AIMessage` | ✅ Yes |
| `ToolMessage` | ✅ Yes — this is how tools report back |
| Plain Python string | ❌ No |

**What the MCP adapter does:** It **converts** the raw MCP response (JSON-RPC) into a LangChain `ToolMessage` — with `type="tool"`, content, artifact, status, and tool_call_id.

> *"Our agent genuinely can just understand tool message. If you are sending me any string, etc., I don't understand it. Because the language which our agent speaks, that is all in the messages part."*

**This is why you must use the LangChain adapter — not any generic MCP client.** If you use a raw FastMCP client and pass the response to the agent as a string, the agent **won't understand it**. The adapter is what "translates French to English."

> *"The reason we need to use LangChain MCP adapter, not any other adapter — because if it doesn't change it into tool message, it is all waste. Because my agent will not be able to understand it."*

**Note on multimodal:** The adapter also converts images and embedded files from MCP into LangChain content blocks. Audio is **not yet supported** — keep an eye on the docs.

---

## ⚠️ Error Handling — Two Failure Modes

**Analogy:** Think of a phone call. If the **call fails to connect**, you get a "network error" and can't talk to anyone. But if the call connects and the **person on the other end gives you wrong info**, you can still hang up and call back. Two different problems, two different fixes.

| Failure Mode | What Happens | How It Surfaces |
|---|---|---|
| **Transport / session failure** | Server crashed, process couldn't start, connection dropped | **Raises a Python exception** — no tool message is created |
| **Tool ran but failed** | Tool ran, returned an error (bad input, business rule violation) | **A `ToolMessage` with `status="error"`** is created — the agent can read it |

**Demo with `cinebot_error_server.py`:**

```python
# Bad booking ID — doesn't start with "BK"
result = await risky_tool.ainvoke({"booking_id": "12345"})

print(result.status)     # "error"
print(result.content)    # "Error calling tool 'risky_lookup': Invalid booking ID..."
```

> *"It raised up an error message. So, content type text, text, error calling tool, risky lookup, invalid text, and everything. So, do you think that your MCP will give a tool error message? No. It will be all on our MCP adapter, which is written by the LangChain people, which changes the same into the type and everything."*

**What you saw on screen:** The MCP server raised a `ValueError`. The MCP adapter **caught** the `ValueError` and **converted** it into a `ToolMessage(status="error")`. Now the agent can read it and **self-correct** — for example, ask the user for the correct booking ID format.

**Why both matter:**

| Mode | Fix |
|---|---|
| **Transport failure** | Wrap in `try/except` — log, retry, or fail gracefully |
| **Tool failure** | Let the agent see the error message — it will try again or explain to the user |

> *"Two ways there could be an error. First is that your call to your MCP server failed because of the transport or session failure — which will be raising an exception. Second is when your tool call fails. I hope you do understand that it will be different to handle both errors."*

---

## 🏷️ Tool Metadata & Annotations

**Analogy:** Think of a **safety label on a power tool**. A drill says "eye protection required" — the label itself doesn't stop you from drilling, but your **supervisor** (middleware) reads the label and can enforce the rule.

**MCP tools can carry annotations** — metadata about the tool:

| Annotation | Meaning |
|---|---|
| `destructive_hint` | The tool **changes** state (booking, cancel, delete) |
| `read_only_hint` | The tool **only reads** (search, get, list) |
| `requires_confirmation` | (Custom) — you define it |

**Reading the annotation:**

```python
for tool in tools:
    meta = tool.metadata or {}
    mcp_meta = meta.get("mcp", {})
    tool_meta = mcp_meta.get("tool", {})
    annotations = tool_meta.get("annotations", {})
    is_destructive = annotations.get("destructive_hint", False)
    print(f"{tool.name}: destructive={is_destructive}")
```

**Output:**

```
check_showtime: destructive=False
cancel_booking: destructive=True
get_seat_map: destructive=False
```

> *"Each adapter tool can carry its MCP provenance under an MCP namespace on the LangChain tool metadata. So MCP tool annotation — I can have destructive hint, read only hint. I can just provide any information which I want. Now based on that information, the whole idea becomes that how I can have any logic."*

**What you can do with it:**

| If annotation says... | You can... |
|---|---|
| `destructive=True` | Require human confirmation before the tool runs |
| `read_only=True` | Skip the confirmation, run it directly |
| `cost_per_call=X` | Log it, throttle, or cache |
| `data_sensitivity=high` | Route through a different model |

**Why this matters:** Without annotations, you'd have to **hard-code** the tool names you consider "destructive." That's brittle — add a new tool tomorrow, and you'd have to update the hard-coded list. Annotations let the **tool itself declare** its own behavior.

---

## 🧑‍⚖️ Human-in-the-Loop with Destructive Tools

**Analogy:** Think of a **bank teller**. If you ask to check your balance (read-only), the teller just does it. If you ask to close your account (destructive), the teller asks you to **confirm** before proceeding. The tool annotation is the "close your account" label that triggers the confirmation.

**The flow:**

1. The agent wants to call `cancel_booking`.
2. Before the call executes, **middleware reads the annotation** — sees `destructive=True`.
3. Middleware **interrupts** and asks the human: "Approve, edit, or reject?"
4. If approved → tool runs. If rejected → tool skipped, agent explains.

**Implementation (conceptual):**

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        tool.name: {"allowed_decisions": ["approve", "edit", "reject"]}
        for tool in tools
        if is_destructive(tool)      # Uses the annotation, not hard-coded names
    }
)

agent = create_agent(model, tools=tools, middleware=[middleware])
```

**The key design choice:** `is_destructive(tool)` reads the annotation. You're **not** saying "interrupt on `cancel_booking`" — you're saying "interrupt on **any tool that declares itself destructive**."

> *"Now do you think that whenever my cancel booking will be called — always and always, no matter the name — I will be able to see and make sure that my HITL, human in the loop, gets called. In this way, you can make your tools a lot better, and that is where this tool annotation is used."*

**Live debugging moment:** The class hit an error because the annotation key was `destructive_hint` (with underscore), but the code was reading `destructive`. A student caught it. The fix: use the exact key from the annotation dict.

> *"You're working on cancel booking, you pasted seat map output. Ah, sorry — thanks for correcting it. I was also checking why I'm not able to see it. Seems like we are getting the annotation — we just need to catch it only."*

**This is the power of metadata:** the logic is **dynamic**, driven by what the tool declares — not by a static list of tool names.

---

## 🗨️ Elicitation — Server-Initiated Questions

**Analogy:** Think of a **customer service call where the agent puts you on hold** to check with their supervisor. The conversation doesn't end — it pauses, the server asks something, and resumes with your answer. That's elicitation.

**Normal tool call:**

```
Client → Server: "Cancel booking BK123"
Server → Client: "Done"
```

**Elicitation:**

```
Client → Server: "Cancel booking BK123"
Server → Client: "Are you sure? Confirm cancellation of BK123."
Client → Server: "Yes"
Server → Client: "Done"
```

The **server** asks the question, not the agent. That's the defining property.

**Implementation (deprecated, but conceptually useful):**

```python
@mcp.tool
async def cancel_booking_confirm(ctx, booking_id: str) -> str:
    """Cancel a booking after confirmation."""
    response = await ctx.elicit(
        message=f"Confirm cancellation of {booking_id}?",
        schema={"type": "object", "properties": {"confirm": {"type": "boolean"}}},
    )
    if response.get("confirm"):
        return f"Booking {booking_id} cancelled."
    return "Cancellation aborted."
```

**Current status:** The `ctx.elicit()` API is **deprecated** in the new LangChain MCP library. Running it gives:

```
Elicitation via server-initiated request is unavailable.
```

> *"Honestly, I will still go with the earlier approach — the human-in-the-loop middleware. Elicitation is a different concept: the server asks the question, not the agent. But since it has been deprecated, and LangChain is picking up the HITL middleware, that is what I recommend."*

**When will it come back?** When the LangChain MCP library stabilizes, or when you use a **legacy** client mode (see below). For now, prefer **human-in-the-loop middleware** for confirmation flows.

**The distinction to remember:**

| Pattern | Who asks the question? |
|---|---|
| **Human-in-the-loop middleware** | The **client** (LangChain) interrupts before the tool runs |
| **Elicitation** | The **server** asks mid-call, then continues |

---

## 🌐 Connecting to Multiple MCP Servers

**Analogy:** Think of a **conference call**. You can dial one person (single server), or you can dial multiple people on the same call (MCP config), or set up separate lines with separate security settings (client groups). Same conversation, different plumbing.

**Two patterns:**

| Pattern | How It Works | Best For |
|---|---|---|
| **MCP Config Dictionary** | One connection, one aggregate namespace, all servers share the **oldest protocol** | Simple setups where all servers speak the same protocol |
| **Client Groups** | One connection **per server**, each keeps its own protocol version and auth | Mixed legacy + modern servers, different auth per server |

**MCP Config (the older, more common pattern):**

```python
from langchain_mcp import MCPAdapter

config = {
    "mcpServers": {
        "cinebot": {
            "command": "python",
            "args": ["cinebot_mcp_server.py"],
            "transport": "stdio",
        },
        "timetrack": {
            "url": "https://your-timetrack-server.com/mcp",
            "transport": "http",
        },
    }
}

async with MCPAdapter.from_config(config) as adapter:
    tools = await adapter.list_tools()
    # Tools are prefixed: cinebot__check_showtime, timetrack__log_time, etc.
```

**Client Groups (the newer pattern):**

```python
from langchain_mcp import MCPAdapter, ClientGroup

group = ClientGroup()

group.add_client("cinebot", cinebot_transport, mode="legacy")
group.add_client("timetrack", timetrack_url, mode="modern", auth=...)

async with MCPAdapter(group) as adapter:
    tools = await adapter.list_tools()
```

**Which to choose?**

> *"First, try to connect with MCP config. If everything works, just quickly check the protocol. And then check — if there is any error or warning coming — then maybe you can move on to client group. Let's keep it simple, let's not unnecessarily complicate it."*

**Why client groups matter:** If one server is on the **old** MCP protocol and another on the **new** one, they can conflict when aggregated. Client groups keep each on its **own negotiated protocol**, so legacy and modern can run side by side.

---

## 🔐 Authentication — The Four Patterns

**Analogy:** Think of four levels of **building access**: a shared office key (bearer token), a badge that logs you in through the lobby (OAuth), a separate key for each door (per-server auth), and a personal keycard that tracks you individually (per-user auth).

| Pattern | How It Works | Best For |
|---|---|---|
| **Bearer Token** | You paste a token in the config; every request sends it | Simple auth, single tenant |
| **OAuth 2.1** | Browser redirect, user logs in, token is minted and stored | Google, Microsoft, GitHub integrations |
| **Per-Server Auth** | Each server in a client group has its own credentials | Mixed auth across multiple servers |
| **Per-User Auth** | A function mints a token per user at runtime | Multi-tenant, per-user data (Gmail, Salesforce) |

**Bearer token:**

```python
async with MCPAdapter(url="https://server/mcp", auth={"bearer": "your-token"}) as adapter:
    tools = await adapter.list_tools()
```

**OAuth:** The adapter opens a browser, the user logs in, the token is cached. Subsequent runs reuse the cached token.

**Per-server auth (client groups):**

```python
group = ClientGroup()
group.add_client("cinebot", transport_a, auth=token_a)
group.add_client("timetrack", transport_b, auth=token_b)
```

**Per-user auth (conceptual):**

```python
def get_user_token(user_id: str) -> str:
    # Look up or mint a token for this user
    return token_store.get(user_id)

async with MCPAdapter(url=..., auth=get_user_token(current_user)) as adapter:
    ...
```

**The key distinction:**

| Scenario | Use |
|---|---|
| **Simple server** (weather, docs) | Bearer token — one shared key, everyone can use it |
| **Gmail / Outlook / Salesforce** | **Per-user OAuth** — each user must authenticate their own account |

> *"If you're saying OTP-based authentication, you just need to authenticate your user. It makes much better sense that we authenticate him on a separate website — like we open Gmail or any other — and have the flow there. To create the OTP-based flow in some authorization, it is possible, but it will be very, very less secure."*

**Where does the server tell you which to use?** Every MCP server documents its auth. The Context7 example (below) says: "Pass Context7 API key as a bearer token if you have one. Higher limits. Works without one for quick demo." You don't have to guess — the server tells you.

---

## 📚 Context7 — Real MCP Server Demo

**Analogy:** Think of Context7 as a **librarian who read every book yesterday**. If you ask about a library that updated its API last week, the librarian knows the new API. A regular search engine might give you last year's answer.

**What it is:** Context7 is a public MCP server that provides **up-to-date documentation** for 142,000+ libraries. It's one of the top 5 most-used MCP servers.

**Why it exists:** LLMs are trained on old data. If you ask Claude Code to fix your LangChain code, it might use `langchain-mcp-adapter` (the old one) because that's what was in its training. Context7 feeds the **latest docs** to the model at query time.

**Demo flow:**

1. Connect to Context7 MCP server (no key needed for basic use).
2. Ask the agent: "Use Context7 and tell me about the latest LangChain MCP library."
3. The agent calls `resolve_library_id(libraryName="langchain")` → gets the ID.
4. The agent calls `query_docs(libraryId=..., query="MCP adapter")` → gets 10,000 tokens of the latest docs.
5. The agent synthesizes an answer using **current** documentation, not stale training data.

**Without key vs with key:**

| | Without Key | With Key |
|---|---|---|
| **Access** | Works, but limited | Higher limits |
| **Use case** | Quick demo | Production |
| **Sign-up** | None | Sign up at context7.com, get API key |

**When the agent doesn't have the key:** It still works — just with lower rate limits.

> *"Context7 says that, hey, if you want to use a higher limit, please log in — we want to have users, we want to give a user base. Otherwise you can use it, but yes, we will give you less limits."*

**One Agent, Three MCP Servers**

The class showed an agent connected to **three** MCP servers at once:

| Server | Tools | Purpose |
|---|---|---|
| **CineBot (local, stdio)** | `check_showtime`, `cancel_booking`, `get_seat_map` | Demo local server |
| **TimeTrack (remote, HTTP)** | `log_time`, `get_timesheet` | Demo time tracking |
| **Context7 (remote, HTTP)** | `resolve_library_id`, `query_docs` | Real documentation lookup |

**The result:** One agent, one question box, eleven tools (some duplicated because the demo re-added servers multiple times — see below).

**Why 11 tools instead of 6?** The notebook's demo loop appends tools each run. Duplicates aren't automatically removed. **In production, use a `set` to dedupe.**

> *"Same tool added multiple times — it won't remove duplicates. Because I'm maintaining a dictionary or list and appending it. What could I have used in Python to remove duplicates? **Set.** These things should be kind of in your brain now."*

**The power of this demo:** The same agent can now answer questions about **movies, timesheets, and LangChain docs** — because all three are exposed as tools.

> *"This is where AI apps become usable by everyone, like no matter what. If you have created an application like this and you create an MCP server, people will be much more likely to use it, because all they have to do is just use MCP."*

---

## 🤝 Multi-Agent Patterns — Practical

**Analogy:** Think of a **hospital**. Some patients need one specialist (subagent). Some need to be transferred to a different department entirely (handoff). Some need to be told "read this brochure" (skill). Some need a triage nurse to route them (router). Same hospital, different flow.

**The four patterns (practical notebook):**

| Pattern | One-Line Summary |
|---|---|
| **Subagent** | Main agent calls a subagent **as a tool**, then presents the subagent's answer as its own |
| **Handoff** | The request is **transferred** to a specialist, who answers directly — no orchestrator in between |
| **Skill** | The agent **loads a prompt** (a "skill") on demand — same agent, expanded instructions |
| **Router** | A **classifier** picks which agent to call, usually in parallel — then synthesizes |

**The notebook:** `LangChain_MultiAgent_Patterns_VSCode.ipynb` — runs all four patterns end-to-end with **deterministic fakes** so you don't burn API tokens.

---

## 🧩 Subagents, Handoffs, Skills, Router

**Subagent** — main agent uses the subagent like a tool:

```
User → Main Agent → calls subagent as tool → subagent runs → returns to Main Agent → Main Agent replies to User
```

> *"I am the orchestrator, and you have V3R also there. Let's say we get a request, and what I do is I send you the request and tell, 'Work on this, give me the results.' Then I work on top of it and present you with the results. That is where I've used you as a sub-agent."*

**Handoff** — the specialist answers the user directly:

```
User → Triage Agent → hands off to Specialist Agent → Specialist replies to User
```

> *"Handoff is like a consultancy. If I get the requirement, I will just transfer it to you. I am out of the picture. You will complete it, give back the result. I am not going to do anything. That, in essence, is what Handoff is."*

**Skill** — the agent loads a prompt at runtime:

```python
@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized skill prompt. Available skills: refund_policy, loyalty_program"""
    return SKILLS.get(skill_name, f"Unknown skill: {skill_name}")
```

**Router** — a classifier picks the destination:

```python
def classify_query(state: RouterState) -> dict:
    structured_llm = router_llm.with_structured_output(ClassificationResult)
    return {"classifications": structured_llm.invoke(state["query"]).classifications}
```

**Can you use GEPA (a classifier) in the router?** Yes — a small classifier model is faster and cheaper than a full LLM for routing decisions.

> *"GEPA says, 'I don't have to do anything, I will just directly say the answer which I feel.' GEPA is just like that. It's a classification-based LLM. The architecture is different, but that is how GEPA is defined."*

**Handoff vs Subagent — the crucial difference:**

| | Subagent | Handoff |
|---|---|---|
| **Who replies to the user?** | The **main agent** (after the subagent returns) | The **specialist** (directly) |
| **Can the main agent modify the answer?** | ✅ Yes | ❌ No |
| **Can you evaluate the subagent's output?** | ✅ Yes — it's a tool result | ❌ Harder — the answer goes straight to the user |
| **Context isolation** | ✅ Full — subagent has its own context | ❌ Partial — shares state |

**LangChain's implementation note:**

> *"LangChain is a little bit bad, honestly, with this approach. I like the AutoGen approach the best here, because AutoGen directly allows you to create teams. AutoGen says, if you want to use multi-agent, you can create a team. But LangChain — since there is no concept of team — you will be doing it via state."*

**Evaluation with handoff:** The evaluator still works — the specialist's output is a message in the graph, so you can score it. You just can't intercept it before the user sees it.

---

## 🔍 The Agent Flow Extension

**Analogy:** Think of a **glass cockpit for an airplane**. You can fly with analog gauges (the terminal), or you can see everything on one screen (Agent Flow). Same flight, clearer view.

**What it does:** Visualizes Claude Code's agent graph in real time — you can see when a subagent spawns, what it's doing, its context size, and when it returns.

**Install:** Search "Agent Flow" in the VS Code marketplace.

**Demo:** Ask Claude Code to "spawn a subagent and explore the codebase." The extension shows two agents (main + subagent), each with its own context — proving that subagents have **separate context windows**.

> *"It is showing two agents. This is having 5K tokens, this is having 7K, because it is going through my codebase. Now I can stop it off if I want. That should not be a problem."*

**Alternative:** There's also a "Pixel Agents" view — more fun, less technical. The Agent Flow is better for debugging.

---

## ⚠️ What's New vs Deprecated

| Feature | Status | Notes |
|---|---|---|
| `langchain-mcp-adapter` | ❌ Deprecated (recent) | Replaced by `langchain-mcp` |
| `langchain-mcp` | ✅ Current, **BETA** | Import warns you — ignore it |
| `MCPAdapter` | ✅ Current | The new connection class |
| `MultiServerMCPClient` (old) | ❌ Deprecated | Replaced by MCP config or client groups |
| **Resources & Prompts** via adapter | ❌ Not supported | Drop down to FastMCP client if you need them |
| **Tools** via adapter | ✅ Supported | Fully functional |
| **Structured output → artifact** | ✅ Supported | Use it to save tokens |
| **Elicitation** (`ctx.elicit()`) | ❌ Deprecated | Use human-in-the-loop middleware instead |
| **Client Groups** | ✅ Current | Best for mixed legacy + modern servers |
| **Bearer / OAuth auth** | ✅ Supported | Different patterns for different servers |

**The resources & prompts limitation:**

> *"LangChain is saying, 'I know that people use it for tools only. I'm not supporting anything beyond tools in the latest one. If you want, you create your own FastMCP client and get the resources and prompts.' Can you create that? Yes, or no? I think you should be able to. We have done that actually — we have done that live in the last-to-last class."*

**Because it's beta, anything can change:**

> *"Since it is in beta, it can change. Tomorrow, actually, LangChain can have 1.4.1, where it is saying that many people were asking for resources and prompts, so we are bringing it back. So don't come to me saying, 'You said no.' No, no — it is still in beta. That is how it happens."*

---

## 💬 Live Q&A Highlights

| Question | Answer |
|---|---|
| **What's changed in LangChain MCP since last class?** | Only the import path — from `langchain-mcp-adapter` to `langchain-mcp`. Concepts are the same. |
| **What's the difference between `invoke` and `ainvoke`?** | `ainvoke` is async — used with `await`. `invoke` is sync. Same result, different execution model. |
| **Why call the tool both directly and through the agent?** | Direct call proves the **tool** works. Agent call proves the **agent** can use it. Two debugging steps. |
| **Can the client know if a tool will return structured output?** | Yes — MCP servers document their tools. Look at `tool.metadata` or the server docs. |
| **How does `message.artifact` save tokens?** | You read the artifact in middleware, extract only what you need, and send **that** to the LLM — not the full JSON. |
| **Why use `set` to dedupe tools?** | Because the demo appended tools in a loop — same tool added multiple times. `set` dedupes. |
| **Is `MCPAdapter` built on FastMCP?** | Yes — FastMCP handles transport, protocol negotiation, connection, and auth underneath. |
| **What is the difference between `message.content` and `message.artifact`?** | `content` is the **text summary** the LLM sees. `artifact` is the **full structured data** your code can access. |
| **What happens if the MCP server crashes mid-call?** | The adapter raises a Python exception. Wrap in `try/except`. No tool message is created. |
| **What happens if a tool returns an error?** | The adapter creates a `ToolMessage(status="error")`. The agent can read it and self-correct. |
| **What is `destructive_hint`?** | An MCP tool annotation. If `True`, the tool changes state (booking, delete). Used to trigger human-in-the-loop. |
| **Why not hard-code `cancel_booking` as destructive?** | Because tomorrow you add `delete_user` — with annotations, you don't have to update the code. |
| **What is the difference between elicitation and HITL middleware?** | Elicitation: the **server** asks. HITL middleware: the **client** interrupts before the tool runs. |
| **Why is elicitation deprecated?** | The new library doesn't support it yet. Use HITL middleware. It may come back in a future version. |
| **How do I connect to two servers?** | Use MCP config (one connection, prefixed tool names) or client groups (one connection per server, independent auth/protocol). |
| **Which should I use — config or client groups?** | Start with config. If you hit protocol conflicts, move to client groups. |
| **What is the difference between bearer token and OAuth?** | Bearer token: paste a static token. OAuth: browser redirect, user logs in, token is minted. |
| **How do I do per-user auth?** | Use `auth=lambda: get_user_token(current_user)` in the adapter — the token is minted per request. |
| **What is Context7?** | A public MCP server that provides up-to-date library documentation. 142K+ libraries. 34% cheaper, 37% fewer tokens than web search. |
| **Why is Context7 one of the most-used MCP servers?** | Because LLMs are trained on old data. Context7 feeds them **current** docs so they don't write stale code. |
| **Can I use GEPA as the router?** | Yes — a small classifier is faster and cheaper than a full LLM for routing. |
| **Why does handoff make evaluation harder?** | Because the specialist replies directly to the user — you can still score the output, but you can't intercept it. |
| **What is the Agent Flow extension?** | A VS Code extension that visualizes the agent graph — you can see subagents spawn, their context, and their output. |
| **What is the difference between subagent and handoff?** | Subagent returns to the orchestrator. Handoff transfers — the specialist answers directly. |
| **Why is AutoGen better for handoffs?** | AutoGen has a native "team" concept. LangChain uses state-based middleware, which is more complex. |
| **Will LangChain MCP get out of beta?** | Soon — the class instructor predicted "two, three weeks." |
| **Can I use LangGraph instead of LangChain?** | Yes — LangGraph is the lower-level graph API. LangChain is built on top of it. Both are required to know. |
| **What about Databricks?** | Out of scope for this course — will be covered separately. Keep your data engineering skills intact; add AI on top. |
| **Why is there no audio support in MCP adapter?** | As of class time, only text and images are supported. Audio is not yet converted to LangChain content blocks. |
| **What is the use case for client groups?** | Mixed legacy + modern servers, different auth per server, or per-server protocol negotiation. |
| **What's the difference between `mode="legacy"` and `mode="modern"` in client groups?** | Legacy = old MCP protocol. Modern = new protocol. Client groups let you run both side by side. |
| **Why does `create_agent` need tools as a parameter?** | Because the agent needs to know what tools exist to decide which one to call. Without tools, the agent can't use them. |
| **What is the "French" analogy in the class?** | The agent only understands LangChain message types (HumanMessage, AIMessage, ToolMessage). A plain string is "French" — it doesn't understand it. |
| **Why do I need a `%pip` cell at the top of the notebook?** | To install dependencies into the notebook kernel. Run it once, restart the kernel, then run the rest. |
| **What happens if I skip the `%%writefile` cell?** | The server file won't exist. The connection cell will fail with "Connection closed." Run the cells in order. |

---

## 🔑 Key Pointers to Remember

- **MCP is framework-agnostic.** The concepts are the same whether you use LangChain, AutoGen, CrewAI, or raw FastMCP. Only the adapter code changes.
- **LangChain moved from `langchain-mcp-adapter` to `langchain-mcp`.** New package, new import. Still beta. Ignore the warning.
- **Only run local MCP servers in VS Code.** Colab can't do stdio reliably.
- **The adapter is the bridge.** It translates MCP JSON-RPC into LangChain `ToolMessage` objects. Without it, the agent can't understand the response.
- **`message.content` = what the LLM sees.** `message.artifact` = full structured data for your code. Use the artifact to **save tokens**.
- **Two error modes:** transport failure (exception) vs tool failure (tool message). Handle them differently.
- **Tool annotations are metadata.** `destructive_hint=True` → trigger human-in-the-loop. Don't hard-code tool names.
- **HITL middleware = the client interrupts.** Elicitation = the server asks. Elicitation is deprecated; use HITL.
- **Multiple servers:** MCP config (simple) vs client groups (advanced). Start with config.
- **Auth patterns:** bearer token (simple), OAuth (browser), per-server (client groups), per-user (function).
- **Context7 is a real, production-grade MCP server.** It solves the "LLM trained on stale docs" problem. 34% cheaper than web search.
- **One agent can connect to many MCP servers.** This is the power of MCP — your agent can use any tool that speaks the protocol.
- **Set dedupes tools.** If you loop over servers and append tools, use a `set` to avoid duplicates.
- **Subagent vs handoff:** Subagent returns to the orchestrator; handoff transfers to the specialist. Evaluate accordingly.
- **Skills are just prompts loaded on demand.** Not RAG. Not tools. Just instructions.
- **Router = classifier + fan-out + synthesize.** GEPA (or any small classifier) can do the routing.
- **The Agent Flow extension visualizes the agent graph.** Great for debugging subagent behavior.
- **Resources & prompts are NOT exposed via the LangChain MCP adapter.** Drop down to FastMCP client if you need them.
- **Beta means it can change.** LangChain MCP is in beta — expect new features and breaking changes.
- **The concepts are what matter, not the syntax.** Libraries change every few weeks. The underlying patterns (tools, messages, context, protocols) are stable.
- **The GitHub repo is the source of truth.** `git pull` before starting. The notebook has the exact working code.
- **Revise the last class.** MCP architecture, FastMCP, stdio vs HTTP, JSON-RPC — these were covered in depth. This class is the practical application.

---

## ✅ Action Items After Class 24

- [ ] **`git pull` the latest code** from the Weekend 14 folder on GitHub.
- [ ] **Run `uv sync`** in the Class24 directory to install dependencies.
- [ ] **Open `MCP_in_Langchain.ipynb`** in VS Code (not Colab).
- [ ] **Add your API key** to `.env` — do **not** commit it.
- [ ] **Run the `%pip` cell once**, restart the kernel, then run the rest of the notebook.
- [ ] **Run the `%%writefile` cell first**, then the transport cell, then the connection cell — in that order.
- [ ] **Call a tool directly** (`ainvoke` on the tool) — prove the tool works without the agent.
- [ ] **Call the same tool through an agent** — prove the agent can use the tool.
- [ ] **Print `message.content` and `message.artifact`** — understand the difference.
- [ ] **Trigger the error server** (`cinebot_error_server.py`) — see how a tool error becomes a tool message.
- [ ] **Read the `destructive_hint` annotation** on `cancel_booking` — verify it's `True`.
- [ ] **Add human-in-the-loop middleware** for destructive tools — test approve/edit/reject.
- [ ] **Connect to Context7** — ask it about a library you use. See the difference vs a regular LLM answer.
- [ ] **Connect to two MCP servers** — use MCP config, then try client groups if needed.
- [ ] **Run the multi-agent notebook** — go through subagents, handoffs, skills, router.
- [ ] **Install the Agent Flow extension** in VS Code — visualize a subagent spawn.
- [ ] **Write a one-paragraph answer** to "What is the difference between a subagent and a handoff?"
- [ ] **Write a one-paragraph answer** to "What are the two failure modes in MCP, and how do you handle each?"
- [ ] **Create your GCP account** (if you haven't already) — the next class starts the project.
- [ ] **Read the Meridian AI project code** — the next class jumps straight into it.

---

## 🎯 Summary

**Class 24 was the full practical implementation of MCP in LangChain** — the code that makes everything you learned conceptually in the previous class actually run. The class opened by moving from Colab to VS Code (because local stdio MCP servers need to run on your machine, not a remote one), and immediately flagged the biggest recent change: LangChain replaced `langchain-mcp-adapter` with `langchain-mcp` just a few weeks before class. The new package is still in **beta** — importing it raises a warning — but it's the current standard, so all code was rewritten against it.

The centerpiece was the **CineBot MCP server** — a small FastMCP server exposing three tools (`check_showtime`, `cancel_booking`, `get_seat_map`) over stdio. The class connected to it via `MCPAdapter` with `PythonStdioTransport`, listed the tools, then demonstrated the two calling paths: **direct tool invocation** (proving the tool works independent of any LLM) and **agent-driven invocation** (giving the tools to a LangChain agent and asking a natural-language question, watching the agent pick the right tool and synthesize a reply). The debugging moments were real — a missing `await` raised `RuntimeError: coroutine was never awaited`, and a missing `%%writefile` cell caused "Connection closed." Both were fixed live.

The **structured output** discussion introduced the `content` vs `artifact` distinction: when a tool returns a dict, the adapter creates a text summary in `content` (what the LLM sees) and preserves the full structured data in `artifact` (what your code can access). The class showed how middleware can read the artifact, extract only the needed fields, and send those to the LLM — a real token-saving pattern that AI won't implement unless you know it's possible.

**Error handling** was broken into two distinct modes: transport failures (server crashed, connection dropped → Python exception) and tool failures (tool ran but returned an error → `ToolMessage(status="error")`). The `cinebot_error_server.py` demo showed a `ValueError` on a malformed booking ID being converted by the adapter into a tool message the agent could read and self-correct from.

**Tool metadata and annotations** unlocked the human-in-the-loop discussion. The `cancel_booking` tool carries `destructive_hint=True`. The class built middleware that reads the annotation (not hard-coded tool names) and triggers an approve/edit/reject prompt before the tool runs. A live debugging moment caught a typo in the annotation key (`destructive` vs `destructive_hint`).

**Elicitation** — the server-initiated question pattern — was covered but flagged as **deprecated** in the new library. The class recommended human-in-the-loop middleware as the current best practice.

**Multiple MCP servers** were covered in two patterns: MCP config (one connection, prefixed tool names) and client groups (one connection per server, independent protocol/auth). The class demonstrated connecting to CineBot, TimeTrack, and Context7 simultaneously, then caught a real bug — duplicate tools were being appended instead of deduped. The fix is a Python `set`.

**Authentication** was mapped to four patterns: bearer token, OAuth, per-server (via client groups), and per-user (via a function). The distinction between "shared server key" (fine for weather) and "per-user OAuth" (required for Gmail, Salesforce) was emphasized.

**Context7** was demoed as a real production MCP server — one of the top 5 most-used MCP servers, providing up-to-date docs for 142K+ libraries. The demo showed an agent fetching current LangChain docs to correct code that would otherwise use the deprecated `langchain-mcp-adapter`.

The class closed with the **multi-agent practical notebook** — subagents (orchestrator calls a subagent as a tool, then presents the result), handoffs (the specialist replies directly to the user), skills (prompts loaded on demand), and router (a classifier picks the destination, fans out, then synthesizes). The **Agent Flow extension** was introduced for visualizing Claude Code's agent graph, proving that subagents have separate context windows.

**The single most important takeaway:** MCP is a protocol, and libraries change every few weeks. What doesn't change is the architecture — a server that exposes tools, an adapter that bridges to your framework, an agent that sees tools as messages, and error handling that distinguishes "connection broke" from "tool said no." Learn the concepts deeply, and any library change becomes a small syntax update.