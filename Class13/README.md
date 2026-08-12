# LangChain Middleware — Consolidated Notes

**Course:** Agentic AI 3.0 Specialization | Krish Naik Academy
**Mentor:** Mayank Aggarwal
**Sessions covered:** Class 12 ("Mastering Middleware: Control, Guardrails & Human-in-the-Loop") + Class 13 built-in middleware reference

> This version merges the two source documents, removes duplicated explanations/code blocks, and fills in the built-in middleware types that were only present in one of the two sources.

---

## 1. Why Middleware Exists

Middleware lets you intercept and modify agent execution at defined points instead of hoping the model behaves correctly on its own. Motivating example: nothing stops an agent from replying rudely if provoked, and nothing automatically flags personal information handed to it — the agent already has everything it needs (model, tools, prompts, messages), but developers still need a way to intervene *between* those components.

**Six hook points around the agent loop:**
1. Before the agent runs
2. After the agent runs
3. Before the model is called
4. After the model is called
5. Before a tool is called
6. After a tool is called

This concept isn't LangChain-specific — Google's Agent Development Kit calls the same idea a "callback." It maps to something every developer already does in regular code: deciding what happens before/after a given action. Middleware just applies that pattern formally to an agent's execution flow.

**Reliability note (from Q&A):** telling a model "don't call this tool more than twice" in a prompt is not reliable — models can ignore it, and it breaks if you swap models. Enforcing limits in code (via middleware) is deterministic in a way prompt instructions never are.

---

## 2. Built-in Middleware Reference

### 2.1 Summarization Middleware
**Purpose:** Compress conversation history to manage token usage/cost as a conversation grows.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model=model,
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="anthropic:claude-haiku",   # can be a cheaper model — summarizing is its own task
            trigger=("tokens", 4000),          # or message count, or % of context window (e.g. 80% full)
            keep=("messages", 10),             # fraction, token count, or message count to leave untouched
        )
    ],
)
```

**Key points:**
- `model` — doesn't need to match the main agent model; a cheaper model works fine.
- `trigger` — absolute token count, message count, or fraction of the model's context window.
- `keep` — how much recent conversation stays untouched (multimodal content included) after older messages are folded into a summary.
- Runs against its **own separate context**, not the agent's main running context.
- Does **not** downsample images/audio — store media separately and reference by URL.
- This is the same mechanism behind Claude Code's `/compact` and the "conversation has been compacted" behavior in long chats.
- **Trade-off:** summarization can genuinely lose information, which is part of why long conversations sometimes "forget" things or hallucinate. There's no guaranteed zero-loss summary — if something must be retained exactly, save it to long-term memory separately rather than relying on the summary.

### 2.2 Human-in-the-Loop (HITL) Middleware
**Purpose:** Pause execution so a human can approve, edit, reject, or respond to a proposed tool call before it runs.

**Why it only applies to tool calls:** everything before a tool call is just the model reasoning; the tool call is the "hands" — the moment the agent actually changes something in the real world. That's the point worth pausing on.

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

agent = create_agent(
    model=model,
    tools=[read_email, send_email, cancel_booking],
    checkpointer=InMemorySaver(),  # REQUIRED for HITL
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject", "respond"]},
                "cancel_booking": {"allowed_decisions": ["approve", "edit", "reject", "respond"]},
                "read_email": False,  # auto-approved, no interrupt
            }
        ),
    ],
)

config = {"configurable": {"thread_id": "hitl-demo"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Send an email to my manager saying I won't be in tomorrow."}]},
    config=config,
)

# Resume later with a decision, using the SAME thread_id:
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
# or
result = agent.invoke(Command(resume={"decisions": [{"type": "reject", "message": "Not authorized"}]}), config=config)
```

**Decision types:** `approve` (run as proposed) · `edit` (modify args first) · `reject` (block, send reason to agent) · `respond` (answer instead of executing).

LangChain doesn't ship a UI for resolving interrupts — resume programmatically via `Command(resume=...)` or wire it into a custom approve/reject interface.

**Common mix-up:** a support chatbot escalating to a human agent is **not** HITL — that's a *transfer*, where the agent hands off the whole conversation and steps out. True HITL keeps the agent in the loop, just paused for one decision (e.g., agent proposes a refund amount, human approves/adjusts it, agent continues).

### 2.3 Model Call Limit Middleware
**Purpose:** Cap total model calls to control cost and prevent infinite loops. (Same idea as a raw-Python `max_turns` safeguard, formalized with framework-level checks.)

```python
from langchain.agents.middleware import ModelCallLimitMiddleware

agent = create_agent(
    model=model,
    tools=your_tools,
    checkpointer=InMemorySaver(),   # required for thread_limit
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=5,        # max calls across the whole conversation
            run_limit=2,           # max calls per single .invoke()
            exit_behavior="end",   # graceful stop (or "exception")
        ),
    ],
)
```

### 2.4 Tool Call Limit Middleware
**Purpose:** Cap tool execution, especially irreversible operations — e.g. an email-search agent could otherwise dig through years of messages unbounded, and every extra tool call adds cost and context.

```python
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model=model,
    tools=cinebot_tools,
    checkpointer=InMemorySaver(),
    middleware=[
        ToolCallLimitMiddleware(run_limit=8),               # global cap per invoke()
        ToolCallLimitMiddleware(
            tool_name="cancel_booking",
            thread_limit=2,   # per-tool cap across the whole conversation
            run_limit=1,      # per-tool cap per invoke()
        ),
    ],
)
```

**Setting the right number:** this comes from domain knowledge, not a framework default — e.g. a web-search agent rarely needs more than 5–15 searches per task. The developer who understands the business use case should set it, rather than leaving it unbounded or guessing arbitrarily high.

### 2.5 Model Fallback Middleware
**Purpose:** Graceful degradation if the primary model provider fails (outage, expired key, hard error) — the app shouldn't simply stop working.

```python
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="openai:gpt-5.5",              # primary model
    tools=your_tools,
    middleware=[
        ModelFallbackMiddleware(
            "openai:gpt-5.4-mini",       # fallback if primary fails
            # "ollama:llama3.2",         # further fallback (fully local)
        ),
    ],
)
# Chain tries each model in order; silently moves to the next on failure.
```

**What it is not:** it does not route by speed or cost, and it is not a smart dispatcher picking the "best" model for a task — it only activates on genuine failure. The full prior conversation history is passed unchanged to whichever model ends up handling the request.

### 2.6 PII (Personally Identifiable Information) Middleware
**Purpose:** Detect and handle sensitive data before/after it reaches the model — a compliance requirement in healthcare, finance, etc. Data like DOB, phone number, email, government IDs, or passwords generally shouldn't reach the model if avoidable.

**Built-in detectors:** email · credit card (Luhn-validated) · IP address · MAC address · URL

**Strategies:**
| Strategy | Behavior |
|---|---|
| `redact` | Replace with `[REDACTED_TYPE]` — value never reaches the model at all |
| `mask` | Partially obscure (e.g. `****-****-****-1234`) — model can tell something is present without seeing the real value |
| `hash` | Deterministic hashing |
| `block` | Raise an exception |

**Configuration options:**
| Parameter | Description | Default |
|---|---|---|
| `pii_type` | Type of PII to detect (built-in or custom) | Required |
| `strategy` | `"block"`, `"redact"`, `"mask"`, or `"hash"` | `"redact"` |
| `detector` | Custom detector function or regex pattern | `None` (uses built-in) |
| `apply_to_input` | Check user messages before model call | `True` |
| `apply_to_output` | Check AI messages after model call | `False` |
| `apply_to_tool_results` | Check tool result messages after execution | `False` |

```python
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model=model,
    tools=your_tools,
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
# Input:        "Email: john@example.com, Card: 4111-1111-1111-1234"
# Sent to model: "Email: [REDACTED_EMAIL], Card: ****-****-****-1234"
```

**Custom detectors** — needed because country-specific ID formats (Aadhaar, PAN, etc.) can't all ship as built-ins. Two equivalent approaches:

```python
# Regex pattern
import re
aadhaar_pattern = re.compile(r"\b\d{12}\b")
PIIMiddleware("aadhaar", detector=aadhaar_pattern, strategy="mask")

# Custom function (for structured codes like booking references)
def detect_booking_code(content: str) -> list[dict]:
    matches = []
    for match in re.finditer(r"BK\d{4}", content):
        matches.append({"text": match.group(0), "start": match.start(), "end": match.end()})
    return matches

PIIMiddleware("booking_code", detector=detect_booking_code, strategy="mask")
```

### 2.7 Todo List Middleware
**Purpose:** Break a complex user request into actionable steps automatically.

```python
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model=model,
    tools=your_tools,
    middleware=[TodoListMiddleware()],
    system_prompt="You are helpful...",
)
# "Plan a movie night: check what's showing, pick a movie, book 2 seats"
# → agent automatically breaks this into steps and executes them
```

### 2.8 LLM Tool Selector Middleware
**Purpose:** Reduce context (and cost) by only sending the model the tools relevant to the current request; a cheaper model can do the selection.

```python
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model=model,
    tools=cinebot_tools,  # e.g. 6 tools available
    middleware=[
        LLMToolSelectorMiddleware(
            model="gpt-4-mini",                    # can be a cheaper model
            max_tools=2,
            always_include=["check_showtimes"],
        ),
    ],
)
# "Cancel booking" → sends only [check_showtimes, cancel_booking]
# "Check showtimes" → sends only [check_showtimes], if sufficient
```

### 2.9 Tool Error Middleware
**Purpose:** Convert raw tool exceptions into clean, model-facing messages instead of leaking internal details.

```python
from langchain.agents.middleware import ToolErrorMiddleware

def handle_seat_error(exc: Exception, request) -> str | None:
    if isinstance(exc, ValueError):
        return "Invalid seat format. Please use format like 'A12'."
    return None  # other errors propagate normally

agent = create_agent(
    model=model,
    tools=cinebot_tools,
    middleware=[ToolErrorMiddleware(on_error=handle_seat_error)],
)
# Tool raises: "Malformed seat number '12'"
# Agent receives: "Invalid seat format. Please use format like 'A12'."
```

### 2.10 Tool Retry Middleware
**Purpose:** Automatically retry transient tool failures (network blips, timeouts) with exponential backoff.

```python
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model=model,
    tools=[flaky_external_api],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,
            initial_delay=1.0,      # seconds
            backoff_factor=2.0,     # multiplier per retry → 1s, 2s, 4s
            on_failure="continue",  # or "fail" to stop
        ),
    ],
)
```

### 2.11 LLM Tool Emulator Middleware
**Purpose:** Simulate specific tool calls with an LLM instead of executing the real tool — useful for safe testing/dev environments and avoiding costly real API calls.

```python
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model=model,
    tools=[book_seats, cancel_booking, send_email],
    middleware=[
        LLMToolEmulator(
            tools=["book_seats", "cancel_booking"],  # emulated
            model="gpt-4-mini",
        ),
        # send_email still executes for real
    ],
)
```

---

## 3. Custom Guardrails

For validation logic beyond the built-ins, write custom middleware that hooks in **before** or **after** the agent runs. Both class-based and decorator syntax are supported and are equivalent.

### 3.1 Before-Agent Guardrails (deterministic input filter)
Runs once at the start of each invocation — good for auth checks, rate limiting, or blocking disallowed requests before any processing.

```python
# Class syntax
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime

class ContentFilterMiddleware(AgentMiddleware):
    """Deterministic guardrail: block requests containing banned keywords."""

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not state["messages"]:
            return None
        first_message = state["messages"][0]
        if first_message.type != "human":
            return None
        content = first_message.content.lower()
        for keyword in self.banned_keywords:
            if keyword in content:
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end",
                }
        return None

agent = create_agent(
    model=model,
    tools=[search_tool, calculator_tool],
    middleware=[ContentFilterMiddleware(banned_keywords=["hack", "exploit", "malware"])],
)
```

```python
# Decorator syntax (equivalent)
from langchain.agents.middleware import before_agent, AgentState, hook_config
from langgraph.runtime import Runtime

banned_keywords = ["hack", "exploit", "malware"]

@before_agent(can_jump_to=["end"])
def content_filter(state: AgentState, runtime: Runtime) -> dict | None:
    if not state["messages"]:
        return None
    first_message = state["messages"][0]
    if first_message.type != "human":
        return None
    content = first_message.content.lower()
    for keyword in banned_keywords:
        if keyword in content:
            return {
                "messages": [{"role": "assistant", "content": "I cannot process requests containing inappropriate content. Please rephrase your request."}],
                "jump_to": "end",
            }
    return None

agent = create_agent(model=model, tools=[search_tool, calculator_tool], middleware=[content_filter])
```

### 3.2 After-Agent Guardrails (model-based safety check)
Runs once on the final response — good for LLM-judged safety checks, quality validation, or compliance scans on the complete answer.

```python
# Class syntax
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.messages import AIMessage
from langchain.chat_models import init_chat_model

class SafetyGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: use an LLM to evaluate response safety."""

    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("gpt-5.4-mini")

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict | None:
        if not state["messages"]:
            return None
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None
        safety_prompt = f"""Evaluate if this response is safe and appropriate.
        Respond with only 'SAFE' or 'UNSAFE'.

        Response: {last_message.content}"""
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])
        if "UNSAFE" in result.content:
            last_message.content = "I cannot provide that response. Please rephrase your request."
        return None

agent = create_agent(model=model, tools=[search_tool, calculator_tool], middleware=[SafetyGuardrailMiddleware()])
```

*(Decorator equivalent: `@after_agent(can_jump_to=["end"])` wrapping a plain function — same logic, no class needed.)*

### 3.3 Combining Multiple Guardrails
Guardrails stack by adding them to the `middleware` list; they run in the order declared, building layered protection:

```python
agent = create_agent(
    model=model,
    tools=[search_tool, send_email_tool],
    middleware=[
        ContentFilterMiddleware(banned_keywords=["hack", "exploit"]),        # 1. before-agent filter
        PIIMiddleware("email", strategy="redact", apply_to_input=True),      # 2. PII on input
        PIIMiddleware("email", strategy="redact", apply_to_output=True),     #    PII on output
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),         # 3. human approval
        SafetyGuardrailMiddleware(),                                         # 4. after-agent safety check
    ],
)
```

---

## 4. Guardrail vs. Middleware

Recurring point of confusion, resolved simply: **a guardrail is the concept** (the goal — protecting the agent from doing something undesirable). **Middleware is the mechanism** used to implement that goal. They are not two competing systems — guardrails need to be applied *as* middleware.

## 5. Middleware Ordering

Multiple middlewares can be attached to a single agent without issue — no need for a separate agent per concern. They don't run in random order: either a defined priority applies, or they run in the order declared. Middlewares are generally written not to collide with each other (e.g., PII redaction should run before the model call).

## 6. LangChain vs. LangGraph

Middleware as a concept exists in LangGraph too — it isn't unique to LangChain. LangGraph becomes worth reaching for when an application needs very precise, deterministic control internally — deeper control over checkpointers, stores, and interrupts than LangChain's abstractions expose by default. LangChain sits on top of LangGraph as a more convenient, somewhat abstracted interface to the same machinery.

For most simple agents — even something like an enterprise RAG chatbot handling a handful of question types — LangChain with built-in middleware is generally sufficient; middleware might not even be strictly necessary for a straightforward RAG setup.

**On frameworkless tools (Claude Code, Cursor):** these use MCP connections and plain instructions rather than LangChain, but are doing essentially the same thing under a different name — "hooks" instead of "middleware." The meaningful difference: agents built this way generally aren't deployable as standalone applications; they stay local, developer-facing tools rather than production services.

---

## 7. Real-World Applications

- **Fraud detection (fintech):** rate-limiting hooks around transaction tools
- **Healthcare compliance:** PII middleware for HIPAA
- **Customer support:** HITL approval before refunds/account changes
- **Audit logging:** wrap tool calls to track who did what and when
- **Cost management:** model fallback, tool selector, and tool emulator middleware

## 8. Key Principles

1. **Checkpointer required** — HITL and persistent (`thread_limit`) limits need `InMemorySaver()` or another checkpoint store.
2. **Stack multiple middlewares** — order matters (e.g., PII redaction before the model call).
3. **Thread safety** — use `config={"configurable": {"thread_id": "unique_id"}}` for persistence across interrupts/resumes.
4. **Graceful degradation** — prefer `exit_behavior="end"` for limits and `on_failure="continue"` for retries over hard exceptions, unless a hard stop is actually desired.

---

## 9. Live Q&A Highlights

| Question | Answer |
|---|---|
| Why not just prompt "don't call the tool more than twice" instead of a limit middleware? | Unreliable — the model can ignore it, and it breaks if the model is swapped. Code-enforced limits are deterministic. |
| Will middleware add latency? | Depends on type. Model-calling middleware (e.g. summarization) adds some latency; pure code-logic middleware (e.g. a call-limit check) has minimal overhead. |
| Can I configure multiple HITL approval levels (e.g. two sign-offs)? | Not out of the box — requires custom middleware. |
| Does model-calling middleware (e.g. summarization) share the agent's main context? | No — it runs against its own separate context. |
| Is PII handled by guardrails or middleware? | Guardrail is the concept; middleware is the mechanism — not competing systems. |
| Can multiple middlewares be attached to one agent? | Yes, passed in as a list, no issue. |
| Do middlewares run in random order? | No — either a defined priority applies, or declaration order; they're designed not to collide. |
| When LangChain + middleware vs. dropping to LangGraph? | LangChain + middleware suffices for most agents, including simple RAG. LangGraph is worth it when precise, deterministic control over state/checkpointing/interrupts is genuinely needed. |
| What to use for observability (LangFuse, OpenTelemetry, etc.)? | No universal answer — depends on the app. LangFuse integrates easily with the LangChain family; for RAG specifically, test dedicated evaluation frameworks rather than assuming defaults are enough — early results are often deceptively easy. |

---

## 10. Action Items

- [ ] Recreate the `SummarizationMiddleware` example with your own `trigger`/`keep` values; watch it fire on a long conversation.
- [ ] Build the `HumanInTheLoopMiddleware` send-email demo; resolve the interrupt both via `Command(resume=...)` and your own approve/reject logic.
- [ ] Add a model call limit and a tool call limit to an existing agent; deliberately trigger both.
- [ ] Set up `ModelFallbackMiddleware` and simulate a primary-model failure (e.g. an intentionally wrong API key) to confirm fallback fires.
- [ ] Write one custom PII detector (`re`-based) for an ID format relevant to your own country/use case.
- [ ] Be ready to explain, in your own words, the difference between a guardrail and middleware (recurring interview-style question).
- [ ] Try `TodoListMiddleware`, `LLMToolSelectorMiddleware`, `ToolErrorMiddleware`, `ToolRetryMiddleware`, and `LLMToolEmulator` on a small test agent.
- [ ] Write one `before_agent` and one `after_agent` custom guardrail from scratch.
- [ ] Come back ready for custom middleware — building your own from scratch is the focus of the next class.

---

## 11. Additional Resources

- [Middleware documentation](/oss/python/langchain/middleware) — complete guide to custom middleware
- [Middleware API reference](https://reference.langchain.com/python/langchain/middleware/)
- [Human-in-the-loop guide](/oss/python/langchain/human-in-the-loop)
- [Testing agents](/oss/python/langchain/test/) — strategies for testing safety mechanisms

---

### What was removed as duplicate
- Two near-identical `SummarizationMiddleware`, `HumanInTheLoopMiddleware`, `ModelCallLimitMiddleware`/`ToolCallLimitMiddleware`, `ModelFallbackMiddleware`, and `PIIMiddleware` code examples (one from each source doc) were merged into single canonical versions, keeping the more complete parameter set from each.
- Repeated "guardrail vs. middleware" and "middleware ordering" explanations were consolidated into single sections (§4–5).
- Duplicate mentions of checkpointer requirements were folded into Key Principles (§8).

### What was added (present in only one source, now included for completeness)
- Todo List, LLM Tool Selector, Tool Error, Tool Retry, and LLM Tool Emulator middleware (§2.7–2.11) — these were missing from the narrative transcript but present in the reference doc.
- The full custom guardrails section (§3) with `before_agent`/`after_agent` hooks, class and decorator syntax, and the combined-guardrails stacking example — present only in the reference doc.
- The PII configuration options table and MAC address/URL detectors — present only in the reference doc.
- The Q&A table and action items (§9–10) — present only in the transcript notes.
