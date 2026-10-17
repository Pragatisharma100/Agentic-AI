# 🧠 Class 23: MCP in LangChain Practical & Multi-Agent Architecture Patterns

**Author:** Pragati  
**Course:** Agentic AI Specialization  
**Date:** 27 September 2026

---

## 📋 Table of Contents
1. [Quick Updates](#-quick-updates)
2. [Recap: Where We Are](#-recap-where-we-are)
3. [MCP in LangChain: The Adapter Pattern](#-mcp-in-langchain-the-adapter-pattern)
4. [Connecting to MCP Servers](#-connecting-to-mcp-servers)
5. [Tool Discovery and Invocation](#-tool-discovery-and-invocation)
6. [Authentication Patterns for MCP](#-authentication-patterns-for-mcp)
7. [Multi-Agent Architecture: Why It Matters](#-multi-agent-architecture-why-it-matters)
8. [Context Isolation: The Token-Saving Superpower](#-context-isolation-the-token-saving-superpower)
9. [Common Multi-Agent Patterns (Without Framework)](#-common-multi-agent-patterns-without-framework)
10. [LangChain's Multi-Agent Patterns (Preview)](#-langchains-multi-agent-patterns-preview)
11. [Agent Flow: Visualizing the Agent Graph](#-agent-flow-visualizing-the-agent-graph)
12. [Live Q&A Highlights](#-live-qa-highlights)
13. [Key Pointers to Remember](#-key-pointers-to-remember)
14. [Action Items](#-action-items)
15. [Summary](#-summary)

---

## 📰 Quick Updates

- 🎯 **Today's scope:** Practical implementation of MCP in LangChain (the adapter, connecting to servers, tool discovery, auth), followed by an in-depth look at multi-agent architecture patterns, context isolation, and token savings.
- 🩹 **Health note:** The instructor was unwell (throat infection) and his voice was low, but the class proceeded. A 5-minute break was taken, and the session ran longer than usual.
- 🔄 **Recent LangChain change:** LangChain has moved from `langchain-mcp-adapter` to `langchain-mcp`. The new package is still in **beta** and may produce a warning. Most concepts remain the same.
- 🗺️ **Roadmap:** Next week starts the **Meridian AI project on GCP**. Before that, students were asked to create a GCP free-trial account ($300 credit). After this project, another GCP project, then LangGraph.
- 📦 **New resource:** The complete MCP notebook and code are on GitHub (Weekend 13 folder). `git pull` before starting.

---

## 🧭 Recap: Where We Are

**Analogy:** Think of the course as a **road trip**. We took a detour to deeply explore MCP (Model Context Protocol) – the "universal translator" that lets AI agents connect to external tools. Now we're back on the main road: **Agentic AI with LangChain**.

So far, you have learned:
- How to create agents with LangChain.
- How to give them tools (which we wrote ourselves).
- The core concepts of MCP (client, server, tools, transports, authentication, legacy vs modern protocol).

Now the question is: **How do we connect our LangChain agents to MCP servers that others have created?** That's where the **LangChain MCP adapter** comes in.

> *"We took a bigger detour to MCP, but in that detour, we understood MCP in very much depth. Now we are coming back to LangChain."*

---

## 🔌 MCP in LangChain: The Adapter Pattern

**Analogy:** The MCP adapter is like a **power strip**. Your LangChain agent (the appliance) needs power (tools). The MCP server (the wall outlet) provides power. The adapter is the strip that connects them – it handles the voltage, the plug shape, and any safety switches.

**What it does:**
1. **Connects** to an MCP server (local stdio, remote HTTP, or in-memory).
2. **Discovers** the tools the server offers.
3. **Converts** those tools into standard LangChain tools that your agent can use.

> *"LangChain gives you an MCP adapter. It's like a universal translator. It can connect either with the local one, or it can help you connect with the HTTP one as well."*

**Built on FastMCP:** The adapter internally uses FastMCP, which handles:
- Transport inference (stdio vs HTTP)
- Protocol negotiation (legacy vs modern)
- Connection management
- Authentication

> *"FastMCP handles transport inference, protocol negotiation, connection management, and authentication. We know all these things now."*

**The minimal code:**

```python
from langchain_mcp import MCPAdapter

async with MCPAdapter(server_path_or_url) as adapter:
    tools = await adapter.list_tools()
    agent = create_agent(model, tools=tools)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": "..."}]})
```

> *"That's the whole idea. The adapter brings MCP servers and LangChain agents together."*

---

## 🔗 Connecting to MCP Servers

MCP servers can be connected in **three ways**:

| Connection Type | How It Works | Example |
|---|---|---|
| **Local (stdio)** | Server runs as a subprocess on your machine | `PythonStdioTransport(script_path="server.py")` |
| **Remote (HTTP)** | Server runs on a remote URL | `MCPAdapter(url="https://server/mcp")` |
| **In-memory** | Server created directly in your code | `FastMCP()` instance |

**For multiple servers**, two patterns exist:

| Pattern | Description | When to Use |
|---|---|---|
| **MCP Config Dictionary** | One connection, prefixed tool names, all servers share the oldest protocol | Simple multi-server setups |
| **Client Groups** | One connection per server, each keeps its own protocol and auth | Mixed legacy+modern servers, different auth per server |

> *"If you need several servers behind one connection, use MCP config. If you need several servers with separate auth or protocol pools, use client groups."*

**Protocol negotiation:** The adapter handles legacy (older handshake) and modern (server discover endpoint) automatically. Your agent never needs to know which one the server speaks.

---

## 🛠️ Tool Discovery and Invocation

Once connected, `adapter.list_tools()` returns a list of LangChain-compatible tools.

**Two ways to call a tool:**

1. **Directly** (without an agent):
   ```python
   result = await tool.ainvoke({"param": "value"})
   ```
2. **Through an agent** (the agent decides which tool to call):
   ```python
   agent = create_agent(model, tools=tools)
   result = await agent.ainvoke({"messages": [...]})
   ```

> *"Direct call proves the tool works. Agent call proves the agent can use it. Two debugging steps."*

**Structured output:** When a tool returns a dict (not just text), the adapter attaches it as an `artifact` on the tool message. The `content` field gets a text summary for the LLM; the `artifact` holds the full structured data for your code.

> *"If the artifact is a large JSON, you might not want to send all of it to the LLM. You can use middleware to extract only the needed fields and save tokens."*

---

## 🔐 Authentication Patterns for MCP

**Analogy:** Four levels of building access – a shared office key (bearer token), a badge that logs you in through the lobby (OAuth), a separate key for each door (per-server auth), and a personal keycard that tracks you individually (per-user auth).

| Pattern | How It Works | Best For |
|---|---|---|
| **Bearer Token** | Static token sent with every request | Simple servers, single tenant |
| **OAuth 2.0/2.1** | Browser redirect, user logs in, token is minted and cached | Google, Microsoft, GitHub |
| **Per-Server Auth** | Each server in a client group has its own credentials | Mixed auth across multiple servers |
| **Per-User Auth** | A function mints a token per user at runtime | Multi-tenant, per-user data (Gmail, Salesforce) |

> *"For a simple server like weather, a bearer token is fine. For Gmail or Salesforce, you need per-user OAuth. You don't want one person's Gmail token to be used by everyone."*

**The adapter delegates authentication to FastMCP** – whatever `fastmcp.client` accepts works. This keeps things consistent with what you already know.

---

## 👥 Multi-Agent Architecture: Why It Matters

**Analogy:** A single agent is like a **general practitioner** – tries to handle everything. A multi-agent system is like a **hospital with specialists** – each department has its own tools, knowledge, and focus. Faster, more accurate, and better context management.

**The problem with one agent:**

Imagine you ask one agent (with 20+ tools) to "reply to Sarah confirming I can meet Thursday at 2 PM." It sends the reply without checking the calendar – because it was overwhelmed by the number of tools.

> *"A single agent works for small tasks, but it starts breaking the moment a request touches more than one thing at once."*

**Why multi-agent is better:**

| Advantage | Explanation |
|---|---|
| **Context isolation** | Each agent has its own context window – no pollution from unrelated tasks. |
| **Parallelization** | Independent tasks can run concurrently. |
| **Specialization** | Each agent has its own tools and prompt – better at its job. |
| **Cost savings** | You can use cheaper models for simpler sub-agents. |

> *"Context isolation is the most important use case. If an agent has to read thousands of files, it's better to have a sub-agent do that and return a summary."*

---

## 💰 Context Isolation: The Token-Saving Superpower

**Live demo:** The instructor showed how a single agent analyzing a codebase consumed **178K tokens** in one session, bloating the context. Then he showed the same task delegated to a **sub-agent** – the main agent's context stayed at **11K tokens** because it only received the summary.

**The numbers:**

| Approach | Main Agent Context | Future Cost |
|---|---|---|
| **No sub-agent** | 178K tokens (code + chat) | High – every future message includes all 178K |
| **With sub-agent** | 11K tokens (summary + chat) | Low – future messages only carry the summary |

> *"The sub-agent spent 150K tokens doing the analysis, but returned a 2K summary. My main agent never saw the 150K – it only got the summary. Future calls are now 10x cheaper."*

**Why not just compress the context?**

Compression (or summarization) of a bloated context (where 170K of 178K is code) will produce a summary that is mostly about the code – losing the original chat. By using a sub-agent, the code summary is cleanly separated from the chat context, preserving both.

> *"It's not that compression is bad – it's that when 95% of your context is one thing, compressing it will drown out everything else."*

**Each agent can use a different model** – e.g., Haiku for summarization, Sonnet for coding, Opus for deep analysis. This is another cost saver.

---

## 🧩 Common Multi-Agent Patterns (Without Framework)

These are architectural patterns you can build yourself, regardless of framework.

| Pattern | How It Works | When to Use |
|---|---|---|
| **Chain** | Agent 1 → Agent 2 → Agent 3 | Tasks have a strict sequence (output of one is input to next) |
| **Parallel** | Same request sent to multiple agents; results merged | Independent tasks can run concurrently |
| **Router / Controller** | A routing agent sends the request to the right agent | You have distinct verticals (math, history, coding) |
| **Reactive / Feedback Loop** | Worker agent does the task; evaluator agent checks it; loop until good | Quality-critical tasks needing self-correction |
| **Hierarchical / Subagents** | A main agent calls sub-agents as tools; uses their results | Complex tasks where context isolation is needed |
| **Planner-Executor** | Planner breaks the task into steps; executor agents run them | Large tasks that can be decomposed |

> *"Multi-agent is just when you have more than one agent. You can combine them in any way you want."*

**Router vs Hierarchical:**

| Router | Hierarchical |
|---|---|
| Request goes to one agent, which responds directly | Request goes to a main agent, which may call sub-agents and then combine results |
| The routing agent is out of the picture after routing | The main agent orchestrates and uses sub-agent outputs |

> *"In router architecture, the request doesn't come back to the router. In hierarchical, the main agent waits for the sub-agent and then works on the result."*

---

## 🧠 LangChain's Multi-Agent Patterns (Preview)

LangChain has its own names for these patterns:

| LangChain Pattern | What It Is |
|---|---|
| **Subagents** | Main agent calls sub-agents as tools |
| **Handoffs** | The request is transferred to a specialist who answers directly |
| **Skills** | The agent loads a prompt on demand (like a manual) |
| **Router** | A classifier picks which agent(s) to call, then synthesizes |

**Can you use a classifier like GEPA for routing?** Yes – a small classifier model is faster and cheaper than a full LLM for routing decisions. LangChain's router pattern can use a classifier.

> *"GEPA is just a classifier. It doesn't generate tokens; it just picks the answer. In router architectures, that's perfect."*

The instructor will cover these patterns in depth in the next class. For now, just know the names and the basic idea.

---

## 📊 Agent Flow: Visualizing the Agent Graph

**What it is:** A VS Code extension that visualizes your Claude Code sessions – you can see the main agent, sub-agents, their context sizes, and the flow of messages.

**Install:** Search for "Agent Flow" in the VS Code marketplace.

**Demo:** The instructor showed:
- Main agent with 5K context, doing a simple chat.
- After asking "analyze the codebase," context ballooned to 170K+.
- Then, starting a **sub-agent** for the analysis – main agent stayed at 5K, sub-agent grew to 100K+.
- Once done, the sub-agent returned a summary, and the main agent's context only grew by the summary amount.

> *"This is real, not magic. The sub-agent did the heavy lifting, and the main agent only got the summary."*

**Note:** Agent Flow works with Claude Code and Codex. It may not support GitHub Copilot directly.

---

## 💬 Live Q&A Highlights

| Question | Answer |
|---|---|
| **Why did the code fail with `No module named langchain_mcp`?** | LangChain recently changed from `langchain-mcp-adapter` to `langchain-mcp`. The new package is in beta and requires `langchain-mcp >= 1.4.0`. Install it with `pip install langchain-mcp`. |
| **How does token reduction happen with sub-agents?** | The sub-agent does the heavy work (reading files, analyzing), consuming a lot of tokens, but it returns only a **summary** (e.g., 2K tokens). The main agent's context stays small, so future calls are cheaper. |
| **Can't we just compress/summarize the context to save tokens?** | Compression helps, but if 95% of your context is code, the summary will be mostly about code – losing the original chat. Sub-agents keep the summary separate, preserving both contexts. |
| **What is the difference between router and hierarchical architecture?** | In a router, the request is sent to one agent and the router is out of the picture. In hierarchical, the main agent orchestrates, waits for sub-agent results, and then responds. |
| **How does the orchestrator know which agent to call?** | Each agent has a name and description, just like a tool. The orchestrator's LLM uses that description to decide. Better descriptions = better routing. |
| **Can we use a small model for routing?** | Yes – a classifier like GEPA is faster and cheaper than a full LLM. It just picks a category. |
| **What is LLM router vs agent router?** | They are conceptually the same – both route a request to the right destination. In LLM router, you route to different LLMs; in agent router, you route to different agents. |
| **How does Agent Flow work?** | It hooks into Claude Code and reads the internal state (messages, tools, context sizes) from local files. It's a visualization tool, not a replacement for Claude. |
| **What is the "lost in the middle" problem?** | LLMs tend to remember the beginning and end of a long context better than the middle. It's a known limitation. Strategies: keep important info at edges, use memory, or use sub-agents to summarize. |
| **What is context bloat?** | When irrelevant or excessive information fills the context window, pushing out important details and increasing cost. Sub-agents prevent bloat by keeping only summaries. |
| **What is the difference between summarization and compression?** | In the context of LLMs, both reduce the size of the context. Compression may be more technical (e.g., removing redundant tokens), but in practice, both are about making the context smaller while keeping the important parts. |
| **Do sub-agents cost tokens?** | Yes, the sub-agent itself uses tokens. But it **saves tokens for future calls** in the main session. The trade-off is worth it when the task is complex and repeated. |
| **Can we use multiple models in one agent system?** | Absolutely. You can assign a cheaper model (e.g., Haiku) for summarization, a mid-tier model (Sonnet) for coding, and the strongest (Opus) for deep reasoning. |
| **Why is Claude Code subscription required for Agent Flow?** | Agent Flow is built on top of Claude Code's internal hooks. Claude Code requires a subscription. You can run Claude Code for free with alternative models (video linked in class). |
| **What is GEPA?** | A classifier model. It doesn't generate text; it picks the best option from a list. Fast and cheap. Good for routing. |
| **How to handle conflicting results from two tools?** | This is an advanced topic. In the project, we will see how to combine multiple agents and tools. For now, understand that you can have an evaluator agent that checks for conflicts. |
| **Can I use LangChain with multiple MCP servers?** | Yes. Use MCP config or client groups. Each server's tools are namespaced to avoid collisions. |
| **What is the difference between FastMCP and LangChain MCP?** | FastMCP is the underlying library that handles the protocol. LangChain MCP adapter wraps FastMCP and makes tools compatible with LangChain agents. They are complementary. |

---

## 🔑 Key Pointers to Remember

- **MCP adapter = universal translator.** It connects your LangChain agent to any MCP server (local or remote).
- **LangChain has moved to `langchain-mcp`.** The old `langchain-mcp-adapter` is deprecated. Install `langchain-mcp>=1.4.0`.
- **Two ways to call a tool:** Directly (`await tool.ainvoke()`) or via an agent (`agent.ainvoke()`). Test both.
- **Structured output:** Tools can return dicts. The adapter puts the text summary in `content` (for the LLM) and the full dict in `artifact` (for your code). Use middleware to extract only what's needed to save tokens.
- **Authentication:** Bearer token (simple), OAuth (browser), per-server (client groups), per-user (function). Choose based on the server.
- **Multi-agent is not just "many agents" – it's how they're wired.** Context isolation and token savings are the main benefits.
- **Context isolation:** Sub-agents keep the main agent's context small by returning only summaries. This dramatically reduces future token costs.
- **Common patterns:** Chain, parallel, router, reactive, hierarchical, planner-executor. You can build any of them yourself.
- **LangChain patterns (preview):** Subagents, handoffs, skills, router. Details next class.
- **Router vs hierarchical:** Router sends and forgets; hierarchical orchestrates and uses results.
- **GEPA (classifier) is perfect for routing** – fast, cheap, and doesn't generate tokens.
- **Agent Flow** visualizes Claude Code sessions. Requires Claude Code subscription.
- **"Lost in the middle"** is a real LLM limitation. Sub-agents help by summarizing and keeping contexts small.
- **Compression vs summarization:** Both reduce context size, but sub-agents keep contexts separate, preventing one task from drowning out others.
- **You can use different models for different agents** – cheap for summarization, strong for reasoning.
- **The project code will be shared this week.** Start the Meridian AI project on GCP next weekend.
- **Create a GCP free-trial account** – $300 credit, 90 days. Keep auto-pay off.

---

## ✅ Action Items After Class 23

- [ ] **`git pull`** the Weekend 13 folder from GitHub.
- [ ] **Install the new packages:** `pip install langchain-mcp fastmcp`.
- [ ] **Run the MCP notebook** – connect to a local server, list tools, call a tool directly, call via agent.
- [ ] **Experiment with structured output** – create a tool that returns a dict, inspect `content` and `artifact`.
- [ ] **Add authentication** to a remote MCP server (bearer token or OAuth).
- [ ] **Try connecting to two MCP servers** using MCP config.
- [ ] **Create a GCP free-trial account** if you haven't already.
- [ ] **Read the Meridian AI project code** (will be shared this week).
- [ ] **Watch the Agent Flow demo video** if you missed the live demo.
- [ ] **Write a one-paragraph answer** to "What is context isolation and why does it save tokens?"
- [ ] **Write a one-paragraph answer** to "What is the difference between router and hierarchical multi-agent patterns?"
- [ ] **Review the previous class** on MCP (client/server, transports, protocol negotiation).
- [ ] **Prepare questions** for the project kickoff next week.

---

## 🎯 Summary

**Class 23 was a bridge between the deep MCP theory and practical LangChain implementation, followed by a thorough introduction to multi-agent architecture.**

The class began with a recap: we've learned how to create LangChain agents and give them tools we wrote ourselves. Now we need to connect them to **MCP servers created by others** – the universal protocol for tool sharing. LangChain provides an **MCP adapter** that connects to local (stdio), remote (HTTP), or in-memory servers, discovers their tools, and converts them into LangChain-compatible tools. The adapter is built on **FastMCP**, which handles transport inference, protocol negotiation (legacy vs modern), connection management, and authentication. We saw that tools can be called **directly** (without an agent) or **through an agent**, and that structured outputs are split into `content` (text summary for the LLM) and `artifact` (full dict for your code) – a key optimization for saving tokens. Authentication follows four patterns: bearer token, OAuth, per-server (via client groups), and per-user (via a function). The big change was LangChain's move from `langchain-mcp-adapter` to `langchain-mcp` (still in beta), requiring an updated package.

The second half focused on **multi-agent architecture** – why one agent isn't enough, and how to structure multiple agents. The core problem: a single agent with many tools gets overwhelmed, leading to errors like sending an email without checking the calendar. Multi-agent solves this through **context isolation** – each agent has its own context window, and sub-agents return only summaries to the main agent. A live demo showed a single agent bloating to **178K tokens** while analyzing a codebase, versus a sub-agent approach where the main agent stayed at **11K tokens** because it only received a summary. This dramatically reduces future token costs – the sub-agent burns tokens once, but the main agent's small context persists. We explored common patterns (chain, parallel, router, reactive, hierarchical, planner-executor) and noted that LangChain names its own patterns (subagents, handoffs, skills, router) – which will be covered in depth next class. The **Agent Flow** VS Code extension was demoed to visualize agent graphs and context sizes, showing how sub-agents are spawned with separate contexts. The class ended with a lengthy Q&A covering token reduction, compression vs summarization, routing decisions, model selection, authentication, and the Agent Flow tool.

**The single most important takeaway:** Multi-agent architecture isn't just about having many agents – it's about **managing context and cost**. By isolating tasks into sub-agents that return summaries, you keep the main agent's context small, making every future call cheaper and more focused. This is the core principle you'll apply in the upcoming Meridian AI project.

---