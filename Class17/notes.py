# from importlib import resources
# from tempfile import template
# from unittest.mock import call

# from requests import get

# from Class1 import tools


# host and server speak the same language
# user ask host the request <-->client sends structured request to server 

# 1:1 relationship btw the client and server

# host+ client --> server
# + ve sign of 1:1 relationship is that it is easy to implement and understand
# scalability
# parallelism
# security


#  MCP primitives 
# -->they are used to implement the communication between the client and server. 
# -->These primitives provide a set of operations that allow the client to send requests and receive responses from the server in a structured manner.    

# -->tools -> an actions which AI can ask the server to perform
# -->Resources -> data sources that AI can read . Static in natuare-> readme files and schema
# -->Pre defined prompts-> template which help AI to work better

# primitives functions:
# host + client --> server
#                     |       |           |
#                 tools resources pre-defined prompts
#                 |         |              |
#             list call, list get template, list get
#                         / list listen

# 3 stages of MCP lifecycle:
# 1. Initialization: The client establishes a connection with the server and performs any necessary setup or authentication.
# 2. operation: The client sends requests to the server using the defined primitives, and the server processes those requests and returns responses.
# 3.Shutdown: The client terminates the connection with the server and performs any necessary cleanup.


# data layer -> how client and server exchange data -> JSON RPC 2.0

# JSON RPC 2.0 
# Javascript Object notation 
# Remote Procedure Call -> allows a program to execute a procedure on a remote server as if it were a local procedure call., 
# abstarcting the details of the transfer of data and network communication 
# this is easy to build and distruibuted applications






# "Why do I even need MCP for my own small project?" 

# "You might not, yet. One app, a handful of tools, nobody else reusing them? Plain function calling  is genuinely fine — MCP starts paying for itself once more than one app or more than one team needs the same tool."

# "Is MCP an Anthropic product I have to pay for?" 

# "No. It's a free, open specification, now governed by a multi-company foundation, not one company's paid product."


# "Function calling already solved my problem in — why do I need to learn MCP at all?" 

# "Because single problem crack only shows up once you scale past one app and one tool — which happens faster than most teams expect. Learning MCP now means you don't have to relearn your integration approach later."

# "Couldn't a company just build one great function-calling library instead of a whole protocol?" 
# "That's basically what MCP is — except the key word is 'agreed.' A library only works if everyone adopts that one company's library. A protocol is a shared agreement multiple companies co-govern, which is why OpenAI and Google support MCP even though Anthropic built it first."


# MCP Architecture: Who Talks, and What They Can Offer
# Every MCP conversation involves exactly three participants — a host, a client, and a server — and a server relationship can offer three specific things once a connection exists. This notebook walks through both, using one small real server as the anchor for everything, and a diagram for every idea so the shape of each concept is visible, not just described.

# Built with real code in this notebook: the server itself, and its tools. Explained in depth, with diagrams: the host, the client, the server relationship, resources, and prompts. Full working code for resources and prompts arrives in a later, dedicated notebook — this one is about understanding the shape of each idea first.

# Setup
# curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS/Linux
# powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

# uv init mcp-warmup && cd mcp-warmup
# uv add fastmcp
# server_code = '''
# from fastmcp import FastMCP

# mcp = FastMCP("Warm-Up Server")

# @mcp.tool
# def greet(name: str) -> str:
#     """Greet someone by name."""
#     return f"Hello, {name}! Welcome to MCP."

# @mcp.tool
# def add(a: int, b: int) -> int:
#     """Add two numbers together."""
#     return a + b

# if __name__ == "__main__":
#     mcp.run()
# '''

# with open('server.py', 'w') as f:
#     f.write(server_code)

# print(server_code)
# uv run fastmcp dev server.py
# This opens MCP Inspector at http://127.0.0.1:6274 — a browser tool that lets you connect to any MCP server and try its capabilities directly, without needing a full AI application involved at all. Click the Tools tab, call greet with your own name, then call add with two numbers. Notice that the description shown for each tool is exactly the docstring written in the Python function above — that listing was generated automatically, not written by hand.

# You've now watched two separate programs — Inspector, and server.py — communicate and complete a task together. Everything below names, precisely, what just happened.

# The Three Participants
# One picture is worth carrying through this entire course: a universal remote sitting in a house full of smart gadgets, with a dedicated adapter behind each one, translating the remote's button presses into whatever signal that specific gadget expects. That picture maps directly onto MCP's three participants.

# flowchart LR
#  P["Person"] --> H["Host\n"]
#  H --> C["Client\n"]
#  C --> S["Server \n"]
# The Host
# The host is the AI application a person actually interacts with — the thing that receives a question, decides (using the language model underneath it) whether it needs outside help, and coordinates whatever happens next. In the setup above, MCP Inspector's own interface was playing this role. In everyday use, this is Claude Desktop, Cursor, or a custom chatbot someone builds.

# The detail worth sitting with: the host never talks to a server directly. It delegates that entirely. If every host had to understand the internal wiring of every tool it might ever use, adding one new capability would be a real engineering project every time. Instead, a host only ever needs to know how to ask — never how any individual server does its job internally. That's what lets one AI application connect to a tool it has never seen before, built by a team it has never spoken to.

# In the smart-home picture, the host is the person holding the remote. They never personally rewire a gadget — they press a button, and something else handles the rest.

# The Server
# A server is a program that does one specific job — or a closely related family of jobs — and exposes that capability clearly enough for anything speaking the right language to find and use it. server.py, running in your terminal right now, is a server. It knows how to greet someone and add two numbers, and nothing else, and that's completely fine — a good server doesn't need to be a general-purpose assistant, only reliably good at its one job.

# This matters more than it looks. Because a server only has to do one thing well, it can be built by whoever actually understands that thing best — often the company that owns the underlying service. A team running a version-control platform is far better placed to build a correct, secure connector to their own system than every individual AI company trying to reverse-engineer it separately. Once a shared protocol exists, a service only has to build its own official server once, and every AI application that speaks the protocol can use it.

# In the smart-home picture, the server is the actual gadget. It doesn't know or care which brand of remote is pointing at it — it only needs to expose its buttons in a shared format.

# The Client
# This is the piece most explanations rush past, and it's worth slowing down for, because it's the actual reason MCP's architecture looks the way it does. The host doesn't talk to a server directly — it creates a dedicated client for each server it wants to use, and that client maintains a private, one-to-one connection with exactly one server. A host connected to five servers is running five separate clients, each with its own dedicated line — never one shared connection to all five.

# In the setup above, the connection Inspector opened the instant it launched — that handshake, that open channel to server.py — was a client doing its job.

# flowchart TB
#  Host["Host (AI Application)"] --> C1[Client 1]
#  Host --> C2[Client 2]
#  Host --> C3[Client 3]
#  C1 -->|dedicated connection| S1[(Server A)]
#  C2 -->|dedicated connection| S2[(Server B)]
#  C3 -->|dedicated connection| S3[(Server C)]
# Each MCP client maintains a dedicated, 1:1 connection with its corresponding MCP server. Local servers typically serve a single client, whereas remote servers typically serve many clients at once. (Model Context Protocol official documentation)

# Why this design, instead of one shared connection to every server? Four concrete reasons, each worth understanding on its own terms rather than as a list to memorize.

# flowchart LR
#  D[Decoupling] --- S[Safety] --- SC[Scalability] --- P[Parallelism]
# Decoupling. Because each client only ever talks to one server, changing or updating how one server works never requires touching how the host talks to any other server. The connections are entirely independent.

# Safety. A crash or serious bug in one server's connection stays contained to that one connection. You can prove this yourself: with server.py running, switch to its terminal and press Ctrl+C. Look at what happens in Inspector — it doesn't crash or freeze, it simply shows that one connection as closed. If Inspector had five servers connected and you killed one, the other four would be completely unaffected. That calm, contained failure is a direct consequence of dedicated connections rather than a shared one.

# Scalability. If one particular server suddenly needs to handle much heavier use, that growth is entirely local to that one client-server pair — none of the host's other connections need to change to accommodate it.

# Parallelism. A host with three live connections can talk to all three servers at the same time, rather than being forced to wait for one slow server before even starting the next. A shared connection would force them to effectively take turns.

# What a Server Can Offer: Three Primitives
# Once a client and a server are connected, the protocol defines exactly three things a server is allowed to give that client. Only the first has real running code in this notebook — the other two are explained fully, with diagrams, and get their own dedicated build in a later notebook.

# flowchart TB
#  subgraph Server["A Server Can Offer..."]
#  T["Tools\nsomething that DOES"]
#  R["Resources\nsomething to READ"]
#  P["Prompts\na FORM to fill in"]
#  end
# Tools — proven above
# A tool is an executable action — something with a real effect when called, not just information being returned. greet and add, which you already called, are both tools. Calling add didn't retrieve a fact that already existed somewhere; it ran a small piece of logic and produced a new result.

# Tools matter because they're the one primitive that lets an AI application actually do something, rather than only ever describing what doing something would involve. Without tools, an AI can tell you in perfect detail what sending an email would look like. With a tool, it can actually send one.

# Resources — the read-only layer
# A resource is read-only reference data a server makes available — something to look at, with no side effects and no action performed. Where a tool does something, a resource simply is something, sitting there for anyone connected to read.

# flowchart LR
#  C1[Client 1] -->|reads| Res[(Shared Resource)]
#  C2[Client 2] -->|reads| Res
#  C3[Client 3] -->|reads| Res
# In the smart-home picture, a resource is the small digital display on a smart thermostat — you don't ask it the current temperature in some active way, you just glance, because it's always sitting there for anyone who looks.

# Resources solve a specific, easy-to-miss problem: without one shared resource, every client that needs the same reference data would have to hard-code its own copy — and over time, as one copy gets updated and another doesn't, the two quietly drift apart until something breaks. A single resource, read fresh by everyone who needs it, never has that problem, because there's only ever one copy of the truth. (The full working code for adding a resource to a server is covered in a later, dedicated notebook.)

# Prompts — a form, not data
# A prompt is a reusable template that shapes how a request gets phrased — not data, and not an action. It's closer to a form with blank fields, provided by the server, that guides a request toward being consistent and complete instead of improvised from scratch every time.

# flowchart LR
#  A["No template\n'customer unhappy, refund maybe'"] -->|server provides a template| B["With a template\nIssue / Tried / Sentiment / Next step"]
# Picture an AI logging a customer support escalation with no guidance at all. Left to its own judgment, it might write something as thin as "customer unhappy, refund maybe" — technically a record, but not useful to a support agent who has to act on it. Now picture a server that hands it a template requiring four specific fields every time: what the issue was, what had already been tried, how the customer seemed to feel, and a recommended next step. Nothing about the underlying model changed, and the question being asked didn't change either — only the presence of a form did.

# This is the real value of a prompt: consistency that survives who's asking. Every AI application that connects to this server and uses this prompt produces escalations with the same structure, because that structure lives once, on the server, instead of being separately reinvented — possibly differently — inside every application that happens to use it. (The full working code for adding a prompt to a server is covered in a later, dedicated notebook.)

# Summary
# mindmap
#  root((MCP
# Architecture))
#  Host
#  the AI app,
# never talks to a
# server directly
#  Client
#  one dedicated
# connection per server
#  Server
#  one focused
# capability
#  Offers
#  Tools -- built today
#  Resources -- next notebook
#  Prompts -- next notebook
# Three participants, always in the same shape: a host that coordinates, a dedicated client per server, and a server that does one job well. And three things a server relationship can offer: tools to act, resources to read, and prompts to structure a request consistently. Tools are already real, in the server you built at the top of this notebook. Resources and prompts are understood in full — what they are, why they matter, and what advantage each one buys — and get their real code in the notebook that follows.

# Next: the actual language these three participants speak to each other — what a message looks like on the wire, and how a connection knows when it has started and when it has ended.


# {
#  "cells": [
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "# MCP Primitives: The Three Things a Server Can Offer\n",
#     "\n",
#     "Every MCP server, no matter what it connects to, can offer exactly three kinds of\n",
#     "things to the client talking to it. This notebook explains each one with a real,\n",
#     "familiar tool as the example, then builds all three into one small, real server --\n",
#     "proving, in actual working code, just how little it takes to go from a tools-only\n",
#     "server to one that offers everything.\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## What's a Primitive?\n",
#     "\n",
#     "Picture a gadget connected to a universal remote. That gadget can do exactly three\n",
#     "kinds of things: something it *does* when a button is pressed, something you can just\n",
#     "*glance at* like a small status display, and a *suggested routine* the manufacturer\n",
#     "built in ahead of time -- a \"movie night\" preset, say. Those three things map directly\n",
#     "onto MCP's three primitives:\n",
#     "\n",
#     "- **Tools** -- actions the AI asks the server to perform\n",
#     "- **Resources** -- structured data the AI can read\n",
#     "- **Prompts** -- ready-made templates the server offers to shape how the AI works\n",
#     "\n",
#     "```mermaid\n",
#     "flowchart LR\n",
#     " T[Tools: something it DOES] ~~~ R[Resources: something to READ] ~~~ P[Prompts: a TEMPLATE to follow]\n",
#     "```\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## Tools: Grounded in GitHub\n",
#     "\n",
#     "A **tool** is an action with a real effect -- not just information coming back, but\n",
#     "something actually happening as a result of the call. Picture a GitHub-connected MCP\n",
#     "server. It exposes a tool called `create_issue`. Nobody calls this tool by hand -- the\n",
#     "AI decides to, the moment it judges from the conversation that logging a bug is the\n",
#     "right next step.\n",
#     "\n",
#     "Two protocol operations cover everything a client needs: `tools/list` to discover what\n",
#     "a server offers, and `tools/call` to actually run one.\n",
#     "\n",
#     "```mermaid\n",
#     "sequenceDiagram\n",
#     " participant AI\n",
#     " participant GH as GitHub Server\n",
#     " AI->>GH: tools/list\n",
#     " GH-->>AI: [\"create_issue\", ...]\n",
#     " AI->>GH: tools/call(create_issue, {title, body})\n",
#     " GH-->>AI: issue created, #482\n",
#     "```\n",
#     "\n",
#     "A tool is the one primitive where the AI itself is holding the wheel. Every other\n",
#     "primitive is initiated by someone else first.\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## Resources: Grounded in Google Drive\n",
#     "\n",
#     "A **resource** is read-only reference data -- something to look at, never something\n",
#     "that changes anything. Picture a Google-Drive-connected MCP server exposing a resource\n",
#     "for one specific file: the team's style guide. The *application* -- not the model --\n",
#     "decides to read that resource and hand its content in as context, so answers stay\n",
#     "consistent with house style without anyone re-typing the guide into every conversation.\n",
#     "\n",
#     "`resources/list` discovers what's available; `resources/read` actually fetches it.\n",
#     "\n",
#     "```mermaid\n",
#     "sequenceDiagram\n",
#     " participant App as Application\n",
#     " participant Drv as Drive Server\n",
#     " App->>Drv: resources/list\n",
#     " Drv-->>App: [\"style-guide.docx\", ...]\n",
#     " App->>Drv: resources/read(style-guide.docx)\n",
#     " Drv-->>App: full file content\n",
#     "```\n",
#     "\n",
#     "Resources can do more than a single file -- **templates** let one resource answer for\n",
#     "a whole family of things (one template covering every customer record, say, instead of\n",
#     "listing each one), and **subscriptions** let a client get notified the moment a specific\n",
#     "resource changes instead of re-reading it on a timer. This notebook keeps its own\n",
#     "example to one plain file; the official MCP documentation covers templates and\n",
#     "subscriptions in full when that need actually arises.\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## Prompts: A Template, Shown Before and After\n",
#     "\n",
#     "A **prompt** is a ready-made template the server offers, so a request gets structured\n",
#     "the same way every time instead of being improvised from scratch. `prompts/list`\n",
#     "discovers what's offered; `prompts/get` pulls a prompt's full details.\n",
#     "\n",
#     "Here's the exact template this course has been building since Part 2 -- a customer\n",
#     "escalation prompt -- shown as its definition and then as what it actually produces.\n"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "prompt_definition = {\n",
#     "    \"name\": \"structured_escalation\",\n",
#     "    \"description\": \"Guides the AI to log a customer escalation with every required field\",\n",
#     "    \"arguments\": [\n",
#     "        {\"name\": \"issue_summary\", \"required\": True},\n",
#     "        {\"name\": \"what_was_tried\", \"required\": True},\n",
#     "        {\"name\": \"customer_sentiment\", \"required\": True},\n",
#     "    ]\n",
#     "}\n",
#     "\n",
#     "# What it looks like filled in, every single time it's used:\n",
#     "example_output = \"\"\"\n",
#     "Issue Summary: Order #4521 arrived damaged\n",
#     "What Was Already Tried: Customer emailed support once, no reply in 3 days\n",
#     "Customer Sentiment: Frustrated, considering a refund request\n",
#     "Recommended Next Action: Escalate to logistics team, offer expedited replacement\n",
#     "\"\"\"\n",
#     "\n",
#     "import json\n",
#     "print('THE TEMPLATE:')\n",
#     "print(json.dumps(prompt_definition, indent=2))\n",
#     "print()\n",
#     "print('WHAT IT PRODUCES:')\n",
#     "print(example_output)\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "Nothing about the underlying model changed between a vague, unstructured note and this\n",
#     "output. The server simply handed it a form to fill in -- that's the entire value of a\n",
#     "prompt primitive.\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## All Three, in Real Code \u2014 Step by Step\n",
#     "\n",
#     "This is the part most tutorials skip: exactly how little code separates a tools-only\n",
#     "server from one offering all three primitives. Starting from the warm-up server built\n",
#     "back in Part 2 -- which already has `greet` and `add` as tools -- here is every step\n",
#     "needed to add a real resource and a real prompt.\n"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "# Step 0: the server as it already exists, from Part 2 -- tools only\n",
#     "step0 = '''\n",
#     "from fastmcp import FastMCP\n",
#     "\n",
#     "mcp = FastMCP(\"Warm-Up Server\")\n",
#     "\n",
#     "@mcp.tool\n",
#     "def greet(name: str) -> str:\n",
#     "    \"\"\"Greet someone by name.\"\"\"\n",
#     "    return f\"Hello, {name}! Welcome to MCP.\"\n",
#     "\n",
#     "@mcp.tool\n",
#     "def add(a: int, b: int) -> int:\n",
#     "    \"\"\"Add two numbers together.\"\"\"\n",
#     "    return a + b\n",
#     "'''\n",
#     "print(step0)\n"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "# Step 1: add ONE resource -- a real, local file being read\n",
#     "step1_addition = '''\n",
#     "@mcp.resource(\"file://server-notes\")\n",
#     "def server_notes() -> str:\n",
#     "    \"\"\"Read-only notes about this server, straight from a local file.\"\"\"\n",
#     "    with open(\"server-notes.txt\") as f:\n",
#     "        return f.read()\n",
#     "'''\n",
#     "print(step1_addition)\n"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "# Step 2: add ONE prompt -- the escalation template from above, now as real code\n",
#     "step2_addition = '''\n",
#     "@mcp.prompt\n",
#     "def structured_escalation(issue_summary: str, what_was_tried: str, customer_sentiment: str) -> str:\n",
#     "    \"\"\"Guides the AI to log a customer escalation with every required field, in order.\"\"\"\n",
#     "    return f\"\"\"Log this customer escalation with the following structure:\n",
#     "Issue Summary: {issue_summary}\n",
#     "What Was Already Tried: {what_was_tried}\n",
#     "Customer Sentiment: {customer_sentiment}\n",
#     "Recommended Next Action: [determine this from the details above]\n",
#     "\"\"\"\n",
#     "'''\n",
#     "print(step2_addition)\n"
#    ]
#   },
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "metadata": {},
#    "outputs": [],
#    "source": [
#     "# Assemble the complete, final server and write it to disk\n",
#     "final_server_code = '''\n",
#     "from fastmcp import FastMCP\n",
#     "\n",
#     "mcp = FastMCP(\"Warm-Up Server\")\n",
#     "\n",
#     "@mcp.tool\n",
#     "def greet(name: str) -> str:\n",
#     "    \"\"\"Greet someone by name.\"\"\"\n",
#     "    return f\"Hello, {name}! Welcome to MCP.\"\n",
#     "\n",
#     "@mcp.resource(\"file://server-notes\")\n",
#     "def server_notes() -> str:\n",
#     "    \"\"\"Read-only notes about this server, straight from a local file.\"\"\"\n",
#     "    with open(\"server-notes.txt\") as f:\n",
#     "        return f.read()\n",
#     "\n",
#     "@mcp.tool\n",
#     "def add(a: int, b: int) -> int:\n",
#     "    \"\"\"Add two numbers together.\"\"\"\n",
#     "    return a + b\n",
#     "\n",
#     "@mcp.prompt\n",
#     "def structured_escalation(issue_summary: str, what_was_tried: str, customer_sentiment: str) -> str:\n",
#     "    \"\"\"Guides the AI to log a customer escalation with every required field, in order.\"\"\"\n",
#     "    return f\"\"\"Log this customer escalation with the following structure:\n",
#     "Issue Summary: {issue_summary}\n",
#     "What Was Already Tried: {what_was_tried}\n",
#     "Customer Sentiment: {customer_sentiment}\n",
#     "Recommended Next Action: [determine this from the details above]\n",
#     "\"\"\"\n",
#     "\n",
#     "if __name__ == \"__main__\":\n",
#     "    mcp.run()\n",
#     "'''\n",
#     "\n",
#     "with open('server.py', 'w') as f:\n",
#     "    f.write(final_server_code)\n",
#     "\n",
#     "with open('server-notes.txt', 'w') as f:\n",
#     "    f.write('This server was built across Parts 2 and 4A of the MCP crash course.\\n'\n",
#     "            'It demonstrates all three primitives: tools, resources, and prompts.')\n",
#     "\n",
#     "print(final_server_code)\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "Run `uv run fastmcp dev server.py` and open Inspector: `greet` and `add` are still\n",
#     "there under Tools, `file://server-notes` now appears under Resources and returns the\n",
#     "real file's content, and `structured_escalation` now appears under Prompts, asking for\n",
#     "the same three fields shown earlier in this notebook.\n",
#     "\n",
#     "**Two decorators. That's the entire distance between a tools-only server and one that\n",
#     "offers all three primitives.** Most tutorials stop at tools because tools are the\n",
#     "easiest thing to demo -- the honest truth is resources and prompts are just as easy to\n",
#     "build.\n"
#    ]
#   },
#   {
#    "cell_type": "markdown",
#    "metadata": {},
#    "source": [
#     "## Summary\n",
#     "\n",
#     "| Primitive | One-line definition | Protocol operations | Real example |\n",
#     "|---|---|---|---|\n",
#     "| Tools | Actions the AI asks the server to perform | `tools/list`, `tools/call` | GitHub's `create_issue` |\n",
#     "| Resources | Structured data the AI can read | `resources/list`, `resources/read` | Google Drive's style guide |\n",
#     "| Prompts | Ready-made templates that shape the request | `prompts/list`, `prompts/get` | `structured_escalation` |\n",
#     "\n",
#     "```mermaid\n",
#     "flowchart TB\n",
#     " S[server.py] -->|@mcp.tool| T[greet, add]\n",
#     " S -->|@mcp.resource| R[file://server-notes]\n",
#     " S -->|@mcp.prompt| P[structured_escalation]\n",
#     "```\n",
#     "\n",
#     "**Next:** all of this, used for real, in one complete live conversation -- from the very\n",
#     "first message to the very last.\n"
#    ]
#   }
#  ],
#  "metadata": {
#   "kernelspec": {
#    "display_name": "Python 3",
#    "language": "python",
#    "name": "python3"
#   },
#   "language_info": {
#    "name": "python",
#    "version": "3.11"
#   }
#  },
#  "nbformat": 4,
#  "nbformat_minor": 5
# }

