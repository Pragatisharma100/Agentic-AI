claude supports
- connectors tools/list (we can connect to 3rd party or global MCP servers and connect them to our code via MCP client)
- configuration files (Add our own MCP server which are running locally or normally to add via code/config)


if we are having a local stdio server.andwe make sure that we provide the config to start the same
in host/client like claude/desktop, we can connect to the same server and use the tools provided by it.


MCP (Model Context Protocol) — Complete Study Guide
Built from two sources: a personal notebook on MCP Architecture & Primitives, and a full lecture transcript (Q&A included) that goes step-by-step through the protocol's internals. Goal of this README: be a self-contained, interview-ready reference — every concept explained with a real-world analogy first, then the technical definition, then how it actually looks on the wire.

Table of Contents
Why MCP Exists
The Big Analogy: A Universal Remote
The Three Participants: Host, Client, Server
Why a Strict 1:1 Client–Server Relationship?
MCP Primitives: What a Server Can Offer
Primitive Functions: How the Client Discovers & Uses Them
The MCP Lifecycle
The Data Layer: JSON-RPC 2.0
Version & Capability Negotiation
Building a Server Yourself (FastMCP)
FAQ — Real Questions From the Class
Quick Reference Cheat-Sheet
Class 20 — Connecting a Server to a Host, For Real
Class 20 — The Time Tracker Project
Class 20 — Two Ways to Turn an API Into an MCP Server
Class 20 — Going Public: FastMCP Cloud (Horizon)
Class 20 — FAQ & Action Items
1. Why MCP Exists
Before MCP, if you wanted an AI model to actually do something — send an email, query a database, create a GitHub issue — you had to hand-write a "tool" for every single API, for every single AI app, separately.

Picture 5 AI applications (Claude, VS Code, ChatGPT, Cursor, a custom chatbot) each needing to talk to 5 services (Gmail, GitHub, Slack, Calendar, Drive). Without a shared standard, that's 5 × 5 = 25 separate integrations to write, test, and maintain — and the moment one API changes its parameters, you have to fix it in 25 places.

MCP (Model Context Protocol) turns that into an N + M problem instead of N × M: each service builds one official MCP server, each AI app builds one MCP client implementation, and any client can now talk to any server that speaks the same protocol.

"It went back to the Gmail guys or the GitHub guys, because if they don't build the connector, their application might not get easily integrated with AI going forward."

MCP is a free, open specification, not a paid Anthropic product — it's now governed as a shared standard, which is why OpenAI, Google, and others support it too, even though Anthropic created it first.

2. The Big Analogy: A Universal Remote
Carry this picture through the entire guide — nearly every MCP concept maps onto it directly.

A universal remote sitting in a house full of smart gadgets, with a dedicated adapter behind each gadget that translates button-presses into whatever signal that specific gadget expects.

Smart-home piece	MCP equivalent
The person holding the remote	You, the user
The remote itself	Host (Claude, VS Code, ChatGPT...)
The dedicated adapter behind each gadget	Client (one per server)
The gadget itself	Server (Gmail, GitHub, Slack...)
A button that does something (turns on a light)	Tool
The gadget's small always-on status display	Resource
A manufacturer's built-in "movie night" preset routine	Prompt
You never rewire the gadget yourself — you press a button, and something else handles the rest. That's exactly how a host never talks to a server directly.

3. The Three Participants: Host, Client, Server
🧑 Person

🖥️ Host
(Claude, VS Code, Cursor...)

🔌 Client
(dedicated, 1:1)

⚙️ Server
(Gmail, GitHub, Slack...)

The Host
The AI application a person actually talks to. It receives your question, decides (using the LLM underneath) whether outside help is needed, and coordinates everything that follows. Examples: Claude Desktop, Cursor, VS Code, Codex, a custom chatbot.

Key rule: the host never talks to a server directly. It only ever needs to know how to ask — never how any individual server does its job internally. That's what lets an AI app use a tool it's never seen, built by a team it's never spoken to.

The Server
A focused program that does one job (or a tight family of jobs) well, and exposes that capability in a shared format. A server doesn't need to be a general-purpose assistant — a good server is just reliably good at its one thing (e.g. "send email," "read a repo").

Because a server only has to do one thing well, it's usually best built by whoever owns the underlying service (Google builds the Gmail server, GitHub builds the GitHub server) — built once, usable by every AI application that speaks the protocol.

The Client
The piece most explanations rush past — but it's the actual reason MCP's architecture looks the way it does.

The host doesn't talk to a server directly. Instead, it spins up a dedicated client for every server it wants to use, and that client maintains a private, one-to-one connection with exactly one server. A host connected to 5 servers is running 5 separate clients — never one shared pipe to all five.

Client and server speak the same language (JSON-RPC 2.0 — see Section 8). The host doesn't need to speak that language at all; it delegates entirely to its clients.

4. Why a Strict 1:1 Client–Server Relationship?
dedicated connection

dedicated connection

dedicated connection

Host (AI Application)

Client 1

Client 2

Client 3

Server A – Gmail

Server B – GitHub

Server C – Calendar

Four concrete, non-negotiable benefits of "one client per server," instead of one shared connection to everything:

Benefit	What it means
Decoupling	Changing how one server works never requires touching how the host talks to any other server. Each connection is fully independent.
Safety	A crash in one server's connection stays contained. Kill one MCP server and the host shows that one connection as broken — the other four keep working fine.
Scalability	If one server suddenly needs to handle heavier load, that growth is entirely local to that one client–server pair.
Parallelism	A host with 3 live connections can talk to all 3 servers at the same time — e.g. "check my calendar and send an email" can run in parallel instead of waiting in a queue.
Extra rules worth remembering from the Q&A:

It's always 1 : 1, never N : 1 or 1 : N. Two Gmail accounts? You need two servers (and two clients), not one client juggling two accounts.
If a server goes down, only that client's connection is affected — the host reconnects it independently; nothing else needs to restart.
There's no hard limit on how many clients a host can run — these are lightweight connections, not heavy resource hogs.
5. MCP Primitives: What a Server Can Offer
Once a client and server are connected, the protocol defines exactly three things a server is allowed to give that client.

A Server Can Offer...

🛠️ Tools
something that DOES

📄 Resources
something to READ

📋 Prompts
a FORM to fill in

Going back to the universal-remote analogy: a gadget can do exactly three kinds of things — something it does when you press a button, something you can just glance at (a status display), and a pre-built routine the manufacturer set up for you (a "movie night" preset).

🛠️ Tools — something the AI does
An executable action with a real side effect — not just information coming back. send_email, create_issue, add(a, b) are all tools. Calling add didn't retrieve a pre-existing fact; it ran logic and produced a new result.

Tools are the one primitive where the AI itself is "holding the wheel" — every other primitive is initiated by someone/something else first (the application, or the user).

Real example: a GitHub-connected server exposing create_issue. Nobody calls this by hand — the AI decides to, the moment it judges from the conversation that logging a bug is the right next step.

📄 Resources — something to read
Read-only reference data, with no side effects. Where a tool does something, a resource simply is something, sitting there for anyone connected to read. Normally static in nature — it doesn't change often (though it can change occasionally).

Good real-world homes for a resource:

A GitHub repo's README.md
A database server's schema file
A travel-booking server's passport PDF, visa checklist, or country guidelines
A team's shared style guide (Google Drive)
Why this matters: without one shared resource, every client that needs the same reference data would hard-code its own copy — and over time those copies quietly drift apart until something breaks. One resource, read fresh by everyone, never has that problem.

📋 Prompts — a form to fill in, not data and not an action
A reusable, ready-made template that shapes how a request gets phrased, so the AI produces consistent, complete output instead of improvising from scratch every time.

Before/after example from the notebook:

Without a prompt template	With a prompt template
"customer unhappy, refund maybe"	Issue Summary: Order #4521 arrived damaged
What Was Tried: Emailed support once, no reply in 3 days
Customer Sentiment: Frustrated, considering refund
Recommended Next Action: Escalate to logistics, offer expedited replacement
Nothing about the underlying model changed — only the presence of a form did. The value of a prompt is consistency that survives who's asking: every AI application that uses this prompt produces the same structure, because the structure lives once, on the server, instead of being reinvented (possibly differently) inside every app.

Why not just rely on tools + resources? A tool's description tells the AI what arguments it takes — it doesn't tell the AI the best way to use it for a given situation. A send_email tool is one thing; "send a leave request to your manager" vs. "send a professional client update" are different use cases of that same tool. A prompt can encode "ask for leave" / "professional communication" / "customer escalation" as separate, reusable templates — that's a job tools and resources don't do.

6. Primitive Functions: How the Client Discovers & Uses Them
Every primitive exposes a small, symmetric pair (or trio) of operations. This is what lets a client, the very first time it connects, ask a server: "what exactly can you do?"

Primitive	Discover	Fetch / Act	Watch for changes
Tools	tools/list	tools/call	—
Resources	resources/list (+ resources/templates/list)	resources/read	resources/subscribe
Prompts	prompts/list	prompts/get	—
Server
AI (Host + Client)
Server
AI (Host + Client)
tools/list
["create_issue", "send_email", ...]
tools/call(create_issue, {title, body})
issue created,
How it plays out in practice: the moment a client connects to a server, it immediately asks for the full menu (*/list for tools, resources, and prompts). From then on, whenever the AI decides an action, read, or template is needed, it uses the matching call / read / get operation — it never has to guess blindly what a server supports.

list vs get (resources) — list tells you what exists ("I have a schema file, a README..."); get/read actually fetches the content of one specific item.
Templates (for resources) let one definition answer for a whole family of things (e.g. one template covering every customer record) instead of listing each individually.
Subscriptions/Listen let a client get notified the moment a resource changes, instead of re-reading it on a timer.
7. The MCP Lifecycle
Every MCP connection that has ever existed follows exactly these three stages, in exactly this order — just like real life, you can't skip straight to a conversation before anyone's been introduced.

1️⃣ Initialization
Handshake & introduction

2️⃣ Operation
The actual conversation

3️⃣ Shutdown
Saying goodbye

Stage	Analogy	What actually happens
Initialization	Meeting for the first time, agreeing what language you'll speak	Client and server agree on a protocol version, exchange capabilities, share implementation details
Operation	The actual conversation	Client discovers and calls tools, reads resources, fetches prompts — any number of times, in any order
Shutdown	Leaving the room	Either side closes the connection (usually the client, e.g. closing Claude Desktop)
Initialization, step by step (the exact handshake)
Server
Client
Server
Client
Connection is now sealed. Normal operation can begin.
initialize (JSON-RPC id:1, protocolVersion, capabilities, clientInfo)
result (id:1, protocolVersion, capabilities, serverInfo)
notifications/initialized (no id — fire and forget)
Client speaks first — sends exactly 3 things: protocol version it supports, its capabilities, and client info.
Server answers, matching the same request ID, with its own protocol version + capabilities (does it support tools? resources? prompts?) + server name/info.
Client seals the handshake with a notification — notifications/initialized. No ID, no reply expected. This is only possible because JSON-RPC supports "fire and forget" messages — a plain REST call always expects a response.
Two hard rules from the spec:

The client must not send anything but a ping before the server responds to initialize.
The server must not send anything but a ping or log before receiving notifications/initialized.
This is exactly why, in Claude's "Connectors" panel, a broken MCP server shows a warning icon even if you've never used it yet — the host tried this handshake in the background at startup and it failed (expired auth, dead server, etc.), so it already knows something's wrong before you ever call a tool.

8. The Data Layer: JSON-RPC 2.0
Data layer = the rules and grammar client and server use to exchange information — just like two humans need a shared language (English, Hindi, whatever) and its grammar to actually understand each other.

MCP's shared language is JSON-RPC 2.0.

JSON — JavaScript Object Notation, the familiar { "key": "value" } format.
RPC — Remote Procedure Call: lets a program execute a function on another machine as if it were a local call, abstracting away the network/transport details. This is what makes it easy to build distributed applications.
Important trivia: JSON-RPC is not an MCP invention. It's a pre-existing, general-purpose lightweight RPC spec used elsewhere in networking. Anthropic simply chose it as MCP's wire format because of the advantages below.

Message shape
Every message, in either direction, shares this shape:

// Client → Server (request)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": { "protocolVersion": "...", "capabilities": {...}, "clientInfo": {...} }
}
// Server → Client (response)
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { "protocolVersion": "...", "capabilities": {...}, "serverInfo": {...} }
}
Field	Meaning
jsonrpc	Always "2.0" — the shared format version. Must match exactly, or it errors out.
id	Uniquely identifies which request a response belongs to — critical because responses can arrive out of order or asynchronously.
method / params	What to do, and with what arguments (requests only)
result or error	The outcome (responses only) — never both
Notifications are a special JSON-RPC message with no id — you fire it and expect nothing back (e.g. notifications/initialized). This is impossible in a plain REST call, where a request always implies a response.

Why JSON-RPC over plain REST/HTTP?
Reason	Explanation
Lightweight	Plain, human-readable JSON. No extra headers, no XML/SOAP-style bloat.
Transport-agnostic	Works the same whether the transport is local (STDIO) or remote (HTTP/SSE).
Two-way by design	Either side can send a request — not just client→server. A long-running server task can proactively tell the client "40% done," rather than the client having to poll repeatedly. Plain REST/HTTP is fundamentally one-way: only the client ever initiates a call.
Notifications built in	"Fire and expect nothing back" is a first-class message type — no such thing exists cleanly in REST.
Standard error codes	Just like HTTP has 404/500, JSON-RPC has its own small set of standard error codes, which MCP inherits wholesale.
Bidirectional, clarified: "two-way" doesn't mean "client calls server, server replies" (that's still one-way / unidirectional — the server never initiates). It means the server can itself open a new request to the client, unprompted — e.g. to report progress on a long task. That's the genuine difference from HTTP REST.

9. Version & Capability Negotiation
Happens right inside the initialize exchange, before anything else can proceed.

Version negotiation — one counteroffer, then done
Yes

No

Yes

No

Client sends its LATEST supported protocol version

Server supports it?

Server responds with the SAME version ✅ Connected

Server responds with its own latest supported version

Client supports that version?

❌ Client disconnects

Analogy: like asking a stranger at a conference "do you work in tech?" — if the answer is no, you don't negotiate further, you just move on. Same here: it's exactly one counteroffer, not a retry loop. If versions still don't line up, the connection is dropped — that's the only fallback.

Another analogy used in class: it's like Windows supporting older software (an app built for Windows 7 still runs on Windows 11) — backward compatibility is a deliberate design decision made by whoever builds the client or the server, not something that happens automatically. If you're building a client that must support 2-year-old servers, you are responsible for handling every version's quirks — that's a real system-design question interviewers ask.

Capability negotiation
Beyond just the version number, client and server also declare what they can actually do: does the server support prompts? Resources? Subscriptions? Does the client support sampling, elicitation, roots? This is exchanged in the same initialize request/response pair described in Section 7.

10. Building a Server Yourself (FastMCP)
Setup
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS/Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

uv init mcp-warmup && cd mcp-warmup
uv add fastmcp
A complete server — all three primitives, in ~25 lines
from fastmcp import FastMCP

mcp = FastMCP("Warm-Up Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP."

@mcp.resource("file://server-notes")
def server_notes() -> str:
    """Read-only notes about this server, straight from a local file."""
    with open("server-notes.txt") as f:
        return f.read()

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.prompt
def structured_escalation(issue_summary: str, what_was_tried: str, customer_sentiment: str) -> str:
    """Guides the AI to log a customer escalation with every required field, in order."""
    return f"""Log this customer escalation with the following structure:
Issue Summary: {issue_summary}
What Was Already Tried: {what_was_tried}
Customer Sentiment: {customer_sentiment}
Recommended Next Action: [determine this from the details above]
"""

if __name__ == "__main__":
    mcp.run()
Run it and inspect it live:

uv run fastmcp dev server.py
This opens MCP Inspector at http://127.0.0.1:6274 — a browser tool that lets you connect to any MCP server and try its capabilities directly, without a full AI application involved. Note that the description shown for each tool is exactly the Python docstring — auto-generated, not hand-written.

The whole point of this demo: going from a tools-only server to one offering all three primitives took exactly two decorators (@mcp.resource, @mcp.prompt). Most tutorials stop at tools because tools are the easiest thing to demo — resources and prompts are just as easy to build.

Frameworks & SDKs
Official Anthropic MCP SDK — the base library.
FastMCP — the most widely used, higher-level wrapper on top of the base SDK.
Analogy used in class: FastMCP is to the official MCP SDK what Keras is to TensorFlow — same underlying engine, much easier ergonomics.
11. FAQ — Real Questions From the Class
Q: Why do I need MCP for my own small project? You might not, yet. One app, a handful of tools, nobody else reusing them? Plain function calling is genuinely fine. MCP starts paying for itself once more than one app, or more than one team, needs the same tool.

Q: Is MCP an Anthropic product I have to pay for? No — it's a free, open, multi-company-governed specification.

Q: Couldn't a company just build one great function-calling library instead of a whole protocol? That's basically what MCP is — except the key word is "agreed." A library only works if everyone adopts that one company's library. A protocol is a shared agreement multiple companies co-govern, which is why OpenAI and Google support MCP even though Anthropic built it first.

Q: What's the difference between a tool description and a README-style resource? A tool description tells the AI what arguments a specific action needs. A resource (like a README) is separate, static reference material the AI can read for broader context. They solve different problems.

Q: Are resources and prompts mandatory for a server? No. Only tools tend to be the "must-have" — resources and prompts are optional extras a server can offer.

Q: How is MCP different from RAG? Totally different. RAG is about retrieving relevant chunks of a large knowledge base to ground a model's answer. A resource is simple, small, relatively static reference data (a schema file, a README) — not a retrieval system.

Q: Can one MCP server call another MCP server? Yes — an MCP server is just a server; nothing stops it from acting as a client to another MCP server internally.

Q: Can I have two clients connect to one server, or one client connect to two servers? No to both — it's strictly 1 : 1. Two Gmail accounts need two separate servers (and two clients), not one client managing two connections.

Q: Does a host cache the list of tools? In the current spec, yes — tool lists are cached rather than re-fetched on every single call.

Q: If the client disconnects due to version mismatch, what's next? You simply can't use that MCP server until the mismatch is fixed via development (supporting the missing version, or upgrading).

Q: Is JSON-RPC's "two-way" the same as WebSockets? Not discussed as equivalent — WebSockets are a constantly-open connection; MCP's bidirectionality is about either side being able to initiate a request, independent of the underlying transport being always-on.

12. Quick Reference Cheat-Sheet
Concept	One-line definition
Host	The AI application you talk to (Claude, VS Code, Cursor). Never talks to a server directly.
Client	A dedicated, 1:1 connection the host spins up for each server.
Server	A focused program exposing one capability (or a tight family of them).
Tool	An action with a real effect — tools/list, tools/call
Resource	Read-only reference data — resources/list, resources/read
Prompt	A reusable request template — prompts/list, prompts/get
Initialization	Handshake: agree on protocol version + capabilities
Operation	The actual back-and-forth: calling tools, reading resources, fetching prompts
Shutdown	Closing the connection cleanly
JSON-RPC 2.0	The shared "language" client and server speak — lightweight, transport-agnostic, two-way, has built-in notifications
Notification	A JSON-RPC message with no id — fire and forget
Version negotiation	Client sends its latest version; server matches or counters once; mismatch → disconnect
MCP

Host

the AI app, never talks to a server directly

Client

one dedicated connection per server

Server

one focused capability

Tools -- actions

Resources -- read-only data

Prompts -- reusable templates

Lifecycle

Initialization

Operation

Shutdown

Data Layer

JSON-RPC 2.0

Part 2 — Class 20: Wrapping a Real API in MCP
Class 20 · Agentic AI 3.0 Specialization | Krish Naik Academy Mentor: Mayank Aggarwal · ~4.5 hours · 13 September 2026

Everything in Part 1 was theory and a toy warm-up server. Class 20's whole point is to prove the theory holds up against a real product — a real SQLite database, a real REST API, two different ways to wrap it in MCP, and a real path to making it public. Think of Part 1 as learning the grammar of a language; this class is the first real conversation held in it.

A framing worth remembering, repeated throughout the class: using AI assistance (pasting code into ChatGPT to understand or debug it) is treated as a normal, professional habit in this course — not a shortcut to be ashamed of. The goal is understanding architecture and decisions deeply, not memorizing syntax by hand.

Session resources:

https://www.mcpjam.com/
https://mcp-lifecycle.netlify.app/
https://mcp-lifecycle-simulator.netlify.app/
https://ai-automation-with-mayank.netlify.app/#mcp
https://github.com/mayank953/Live-Class-2026/tree/main/Complete%20MCP
https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro
13. Class 20 — Connecting a Server to a Host, For Real
Section 3 explained the host→client→server relationship in the abstract. This section is the plumbing underneath it — how a server actually ends up connected, in practice, on your machine.

Two doors into the same room
There are two ways to add a server to a host, and the key insight is that they are not actually two different mechanisms — they're two interfaces onto the exact same underlying file.

Method	Who it's for	What it really is
Connectors (UI)	The layperson — click "Add," paste a name and a hosted URL, done	A friendly form that, behind the scenes, writes an entry into the config file below
Config file (claude_desktop_config.json on Mac, equivalent on Windows)	Developers running their own locally-built server	The actual source of truth every host reads from — you edit it directly because a local server has no public URL to just paste into a box
Analogy: the Connector UI is the "Add a new gadget" wizard on a smart-home app; the config file is the wiring closet the wizard is secretly editing on your behalf. A developer who's building their own gadget skips the wizard and goes straight to the wiring closet.

A real look at the config file makes the structure concrete — it's just a JSON object, one entry per server, naming the exact command used to start it:

"RecipeBox_Updated": {
  "command": "/opt/homebrew/bin/uv",
  "args": ["run", "--with", "fastmcp", "fastmcp", "run", ".../recipebox_fastmcp.py"],
  "transport": "stdio"
},
"demo-filesystem-wiretapped": {
  "command": "python3",
  "args": ["mcp_wiretap.py", "--log", "wiretap-live.log", "--", "npx", "-y", "@modelcontextprotocol/server-filesystem", "..."]
}
Two hard-won practical lessons
1. The "bare command" trap. Writing just "command": "uv" often fails silently inside Claude Desktop, because the host doesn't necessarily know where uv lives on your machine — it isn't reading your shell's $PATH the way a terminal does. The fix:

which uv     # → /opt/homebrew/bin/uv
which python # same idea, for python-based servers
Swap that full path into the config's "command" field, restart the host, and the server appears under Connectors. This is flagged as one of the most common real-world setup bugs — common enough to be its own action item below.

2. Wiretapping a server. The demo-filesystem-wiretapped entry is a real example of a technique for when a host's own on-disk logs aren't detailed enough: run the server through a small relay script that transparently forwards every message through to the real server, while independently logging the full JSON-RPC conversation on the side.

Client

🕵️ Wiretap relay script
(logs everything, forwards everything)

Real MCP Server
(@modelcontextprotocol/server-filesystem)

This is the same architectural pattern as the "man-in-the-middle" logging proxies used in ordinary networking — the relay is completely transparent to both sides, it just happens to be nosy.

The same pattern in VS Code
Proof that this isn't a Claude-specific quirk: VS Code follows an identical logical flow, through a different door.

Cmd/Ctrl+Shift+P → "MCP: Add Server" → choose STDIO → provide the exact command to run the server file
This generates VS Code's own mcp.json (its equivalent of claude_desktop_config.json). Restart the connection, and the same tools become available to VS Code's own AI features. Every host — Claude, VS Code, Cursor, ChatGPT — runs through the exact same underlying architecture; only the settings screen wrapped around it differs.

A doubt worth settling clearly
Who decides which tool gets called — the server, or something else? The MCP server never decides. A server just sits there, waiting to be asked. The client sends a tools/call request naming exactly which tool and which arguments. All the "deciding" happens on the model/brain side, before the request is ever sent — the server's whole job is to execute, not to choose.

This is consistent with Section 5's definition of a tool: the AI decides whether and when to call a tool; the server's role is purely to expose what it can do and then execute exactly what's asked.

14. Class 20 — The Time Tracker Project
Rather than another toy example, the class built something with a genuinely real shape: a time-tracking application — the same category of product as Toggl or Clockify — with real employees logging real hours against real projects.

The Database Layer
A SQLite database with a time_entries table: auto-incrementing ID, employee name, project, entry date, hours, and a description of the work done. It's seeded with sample data on first run, so the app never starts genuinely empty. A small row_to_dict helper converts SQLite's native row objects into plain Python dictionaries — the shape every API endpoint actually needs to return.

The API Layer (FastAPI — deliberately not MCP yet)
This layer has nothing to do with MCP. That's the point: it's the same kind of ordinary REST API that Gmail, Google Calendar, or any real product already has, long before anyone thinks about wrapping it for AI.

from fastapi import FastAPI
import database as db

app = FastAPI(title="Time Track", description="A simple time tracking app with REST and MCP endpoints")

db.init_db()  # creates the table and seeds sample data if empty

@app.get("/api/entries")
def list_all_entries():
    return db.list_all_entries()

@app.get("/api/projects")
def list_projects():
    return db.list_projects()

@app.get("/api/projects/{project}/summary")
def get_project_summary(project: str):
    return db.get_project_summary(project)

class NewEntry(BaseModel):
    employee_name: str
    project: str
    entry_date: str
    hours: float
    description: str

@app.post("/api/entries")
def log_time(entry: NewEntry):
    return db.log_time(entry.employee_name, entry.project, entry.entry_date, entry.hours, entry.description)
Running it:

uv run fastapi dev main.py
This produces a working Swagger docs page (/docs) — every endpoint testable directly in the browser — plus a real front-end (plain HTML/CSS + app.js handling fetch calls) that lets someone log time and see project summaries through a normal web UI. The browser's Network tab was used live to show exactly which REST calls fire when a new entry gets logged.

The point made explicitly: this is the same starting position almost every real MCP integration begins from — a working product with its own REST API, built with zero awareness that MCP will ever sit on top of it. Nothing about a real company's Gmail or Slack API was designed "for AI." MCP is what gets bolted on afterward.

not yet built

SQLite
time_entries table

FastAPI REST layer
/api/entries, /api/projects...

Plain HTML/CSS/JS front-end

MCP layer
(next section)

15. Class 20 — Two Ways to Turn an API Into an MCP Server
With the Time Tracker's API working end to end, the class built the MCP layer on top of it two different ways, with an explicit discussion of when to reach for each.

Option 1 — Manual Tools: Full Control
from fastmcp import FastMCP
import database as db

mcp = FastMCP("Time Tracker")

@mcp.tool
def log_time(employee_name: str, project: str, entry_date: str, hours: float, description: str) -> dict:
    """Log a new time entry for an employee against a project."""
    return db.log_time(employee_name, project, entry_date, hours, description)

@mcp.tool
def get_timesheet(employee_name: str, week_start: str) -> list[dict]:
    """Get all time entries for one employee for a given week."""
    return db.get_timesheet(employee_name, week_start)

@mcp.tool
def get_project_summary(project: str) -> dict:
    """Get total hours and a per-employee breakdown for one project."""
    return db.get_project_summary(project)

@mcp.tool
def list_projects() -> list[str]:
    """List every known project name."""
    return db.list_projects()

@mcp.prompt
def generate_weekly_report(employee_name: str, week_start: str) -> str:
    """A template guiding the AI to pull an employee's week and write a clean summary report."""
    return f"Generate a weekly report for {employee_name} starting {week_start}, using their timesheet and project summaries..."

if __name__ == "__main__":
    mcp.run()
Confirmed live via MCP Inspector: the exact same lifecycle steps from Section 7 — initialize, discovery of tools/resources/prompts, then a real tools/call — showed up identically for this brand-new, genuinely custom-built server. That's the payoff of learning the protocol in depth: it's not different for a "real" server, it's the same handshake every time.

The generate_weekly_report prompt is the standout here — it's something a plain API alone cannot replicate. It's a template that guides the AI to combine multiple tool calls (get_timesheet + get_project_summary) into a single, well-structured output. This is exactly the primitive described in Section 5: a form, not data, not an action — the value a hand-written MCP layer adds beyond just mirroring existing endpoints.

Option 2 — Automatic Conversion: Speed
from fastmcp import FastMCP

mcp = FastMCP.from_fastapi(app)  # 'app' is the exact FastAPI instance already defined above
In four lines, every existing FastAPI endpoint became a callable MCP tool automatically — confirmed live in MCP Inspector, with tools mapped straight from the REST routes. Notably: no prompts, no resources — because those don't exist as a concept in plain REST, so there's nothing to auto-convert them from.

Choosing Between Them — the real question, answered directly
A learner working with real production Java APIs asked exactly the right question: when should a team auto-convert existing APIs versus build tools by hand?

Get already-trusted APIs
in front of AI, fast

Need finer control

Goal?

✅ Auto-convert
FastMCP.from_fastapi(app)

✅ Build manually
@mcp.tool / @mcp.prompt

Combine 2+ API calls
into one named tool

Write richer, AI-friendly
descriptions

Add prompts
(impossible via auto-conversion)

Situation	Recommendation
Just making already-working, already-trusted APIs available to AI, quickly, with no interest in reshaping them	Auto-convert
Combining two or more API calls into a single, well-named tool	Build manually
Writing richer, more AI-friendly descriptions/argument docs than the original API needed for human developers	Build manually
Wanting prompts at all	Build manually — auto-conversion cannot produce them, since REST has no equivalent concept
Real-company risk aversion: teams are reluctant to touch an already-working, already-deployed API just to make it "more AI-friendly"	Build manually, as a separate layer — this avoids touching code that's already trusted in production
16. Class 20 — Going Public: FastMCP Cloud (Horizon)
A server running on your own laptop is only useful to you. The final piece of Class 20 is the path from "works on my machine" to "a URL anyone's AI host can connect to."

Horizon, built by Prefect (the same company behind FastMCP itself), is the hosting platform FastMCP's own documentation recommends.

Free tier detail	Value
Developers	1
MCP servers	up to 200
Log retention	1 hour
Deployment	Connected via GitHub — any future code push deploys automatically
Resulting URL shape	your-project.fastmcp.app/mcp
auto-deploy

💻 Local server
(works on your machine)

GitHub repo

☁️ Horizon (by Prefect)

🔗 your-project.fastmcp.app/mcp

Paste into any host's connector settings:
Claude Desktop · Claude Web · ChatGPT · Cursor

This closes the full loop of the session: a locally-built, fully-understood server (Section 14–15) becomes something anyone in the world can add to their own AI, in a single paste — exactly the same mechanism used earlier in the class to add the public Firecrawl connector (Section 13). Nothing new to learn on the "connecting" side — it's the same Connector door from Section 13, just now pointing at a URL you control instead of someone else's.

17. Class 20 — FAQ & Action Items
Live Q&A
Question	Answer
For production APIs already deployed, should we use the 4-line auto-conversion or build tools manually to expose them internally?	Auto-conversion is the faster, safer starting point specifically because it doesn't require touching already-trusted production code. Manual tools are worth it once finer control (better descriptions, combined calls, prompts) is genuinely needed.
If I have 5 connectors, do they all need to be defined in one config file?	Yes — each connector is its own separate server entry; the host starts each one independently, exactly like the multiple servers shown running side by side earlier.
How does an MCP server decide which tool to call for a given request?	It doesn't. The server only executes whatever tool a client's request explicitly names. The decision happens on the model/client side, before the request is even sent.
Is the GitHub → Horizon deployment step similar to a Java developer deploying to Kubernetes?	Conceptually yes — same underlying idea of taking working local code and making it a reachable running service, just via a platform built specifically for MCP servers rather than a general container orchestrator.
Will authorization be added to this project?	Yes — planned as a natural next step once the server is properly hosted, since a publicly reachable time-tracking server for a real company needs real access control.
Is writing code without AI assistance still expected in interviews?	No — using AI to write and understand code is a normal, expected professional skill in this course. What matters is understanding the resulting architecture and decisions well enough to explain and defend them.
🔑 Key Pointers to Remember
A connector and a config-file entry are the same underlying thing — connectors are just the friendly UI for what's really stored in a config file every host maintains.
The MCP server never decides which tool to call. It only executes what a client's tools/call request explicitly names — all the deciding happens upstream, in the model.
A UV/Python path failure inside a host's config is one of the most common real setup bugs — which uv (or which python) gives the exact full path a config often needs spelled out.
Real products already have APIs before anyone thinks about MCP. Building an MCP layer is something added afterward, on top of infrastructure that was never designed with AI in mind.
FastMCP.from_fastapi(app) auto-converts an entire existing API into MCP tools in four lines — genuinely useful, but it produces no prompts, no custom descriptions, no combined multi-API tools.
Manual @mcp.tool definitions are worth the extra effort when you need control: better AI-facing descriptions, combining multiple API calls into one tool, or adding prompts — none of which auto-conversion can give you.
Teams often prefer a separate, hand-built MCP layer specifically to avoid touching already-trusted production API code.
Horizon (by Prefect) is FastMCP's own recommended free hosting path, connected via GitHub, turning a local server into a real public URL any AI host can use.
✅ Action Items
 🔌 Open your own host's config file (Claude Desktop, VS Code, or similar) and identify the exact command/path structure for at least one connected server
 🩹 Deliberately break a server's config with a bare uv/python command (no full path) and fix it using which uv / which python
 🏗️ Build a small FastAPI backend with at least two endpoints and a SQLite-backed database, exactly like the Time Tracker's entries/projects tables
 🛠️ Wrap that same API in MCP two ways: manually with @mcp.tool, and automatically with FastMCP.from_fastapi(app) — compare the resulting tool lists in MCP Inspector
 📋 Add one @mcp.prompt to your manually-built server that combines two or more of your tools into a single guided output
 ☁️ Look into Horizon's free tier and understand, at a high level, the GitHub-to-live-URL deployment flow
 📖 Come back ready for building a real MCP client and completing the public deployment
🗺️ What's Next
Client creation and completing the live hosting are the two pieces explicitly left for the next session, with a return to LangChain — and understanding the newest MCP architecture's changes — targeted for the following weekend.

Sources
Personal course notebook: "MCP Architecture: Who Talks, and What They Can Offer" + "MCP Primitives" notebook (FastMCP code, diagrams, definitions).
Class 19 full lecture transcript (live class recording) — architecture recap, primitives, the complete lifecycle, JSON-RPC deep dive, version/capability negotiation, plus live student Q&A.
Class 20 full lecture transcript + structured class notes (live class recording, 13 September 2026) — connecting servers to hosts, the Time Tracker project (FastAPI + SQLite + FastMCP), manual vs. automatic MCP conversion, and FastMCP Cloud (Horizon) deployment.