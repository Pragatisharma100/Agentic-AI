# 🛡️ LangChain Middleware & Guardrails — Complete Reference

**Author:** Pragati  
**Course:** Agentic AI Specialization   
**Date:** 9 August 2026

---

## 📋 Table of Contents
1. [Why Middleware Exists](#-why-middleware-exists)
2. [Built-in Middleware Reference](#-built-in-middleware-reference)
   - [Summarization](#21-summarization-middleware)
   - [Human-in-the-Loop (HITL)](#22-human-in-the-loop-hitl-middleware)
   - [Model Call Limit](#23-model-call-limit-middleware)
   - [Tool Call Limit](#24-tool-call-limit-middleware)
   - [Model Fallback](#25-model-fallback-middleware)
   - [PII Detection](#26-pii-personally-identifiable-information-middleware)
   - [Todo List](#27-todo-list-middleware)
   - [LLM Tool Selector](#28-llm-tool-selector-middleware)
   - [Tool Error](#29-tool-error-middleware)
   - [Tool Retry](#210-tool-retry-middleware)
   - [LLM Tool Emulator](#211-llm-tool-emulator-middleware)
3. [Custom Guardrails](#-custom-guardrails)
4. [Middleware vs. Guardrails](#-guardrail-vs-middleware)
5. [Middleware Ordering](#-middleware-ordering)
6. [Real-World Applications](#-real-world-applications)
7. [Live Q&A Highlights](#-live-qa-highlights)
8. [Action Items](#-action-items)

---

## 🎯 Why Middleware Exists

**Analogy:** Think of middleware as the security checkpoint at an airport. Before you board the plane (the agent does something), your luggage is screened, your ID is checked, and certain actions are approved or blocked. Just like an airport has multiple checkpoints (baggage screening, passport control, security scan), middleware gives you multiple places to intercept and control an agent's behavior.

Middleware lets you intercept and modify agent execution at defined points instead of hoping the model behaves correctly on its own. 

**The problem it solves:** Nothing stops an agent from replying rudely if provoked, and nothing automatically flags personal information handed to it. The agent already has everything it needs (model, tools, prompts, messages), but developers still need a way to intervene *between* those components.

**Six hook points around the agent loop:**
1. Before the agent runs
2. After the agent runs
3. Before the model is called
4. After the model is called
5. Before a tool is called
6. After a tool is called

This concept isn't framework-specific — it's the same pattern developers already use in regular code: deciding what happens before/after a given action. Middleware just applies that pattern formally to an agent's execution flow.

---

## 🛠️ Built-in Middleware Reference

### 2.1 Summarization Middleware

**Purpose:** Compress conversation history to manage token usage/cost as a conversation grows.

**Analogy:** Think of this like taking meeting notes. After a 2-hour meeting, you don't need every word — you need a summary. Similarly, as a conversation gets long, older messages get condensed into a summary to save tokens and keep the agent focused on recent context.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model=model,
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="anthropic:claude-haiku",   # Can be a cheaper model — summarizing is its own task
            trigger=("tokens", 4000),          # Triggers at 4000 tokens
            keep=("messages", 10),             # Keep last 10 messages untouched
        )
    ],
)
```

**Key points:**
- `model` — doesn't need to match the main agent model; a cheaper model works fine
- `trigger` — absolute token count, message count, or fraction of the model's context window
- `keep` — how much recent conversation stays untouched after older messages are folded into a summary
- Runs against its **own separate context**, not the agent's main running context
- Does **not** downsample images/audio — store media separately and reference by URL

**Trade-off:** Summarization can genuinely lose information — that's why long conversations sometimes "forget" things. If something must be retained exactly, save it to long-term memory separately.

---

### 2.2 Human-in-the-Loop (HITL) Middleware

**Purpose:** Pause execution so a human can approve, edit, reject, or respond to a proposed tool call before it runs.

**Analogy:** Imagine you're a manager and your assistant drafts an important email. Before sending it, you review it, make edits, approve it, or reject it. HITL middleware gives you that same review power over your agent's actions.

**Why it only applies to tool calls:** Everything before a tool call is just the model reasoning; the tool call is the "hands" — the moment the agent actually changes something in the real world. That's the point worth pausing on.

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
```

**Decision types:**
- `approve` — run as proposed
- `edit` — modify arguments first
- `reject` — block, send reason to agent
- `respond` — answer instead of executing

**Common mix-up:** A support chatbot escalating to a human agent is **not** HITL — that's a *transfer*, where the agent hands off the whole conversation and steps out. True HITL keeps the agent in the loop, just paused for one decision.

---

### 2.3 Model Call Limit Middleware

**Purpose:** Cap total model calls to control cost and prevent infinite loops.

**Analogy:** Think of this like a data plan on your phone. You have a limited number of API calls you can make before you exceed your budget. This middleware is like setting a monthly data cap to prevent surprise bills.

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

---

### 2.4 Tool Call Limit Middleware

**Purpose:** Cap tool execution, especially irreversible operations.

**Analogy:** Imagine you're at an all-you-can-eat buffet. The run limit is like "you can only take 2 plates per trip to the buffet," while the thread limit is "you can only eat 10 plates total for the entire meal." This prevents a single user from getting too many tool calls.

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

**Run Limit vs. Thread Limit (The Meal Analogy):**
- **Run limit:** Like how many chapatis you can eat in one sitting (a single conversation turn)
- **Thread limit:** Like how many chapatis you can eat across the entire day (multiple turns in the same conversation)

**Setting the right number:** This comes from domain knowledge, not a framework default — e.g., a web-search agent rarely needs more than 5–15 searches per task.

---

### 2.5 Model Fallback Middleware

**Purpose:** Graceful degradation if the primary model provider fails.

**Analogy:** Think of this like having a backup generator for your house. When the main power fails, the backup kicks in automatically — your lights stay on, and you don't even notice the switch. This middleware is your AI's backup generator.

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

**What it is not:** It does not route by speed or cost, and it is not a smart dispatcher picking the "best" model for a task — it only activates on genuine failure.

---

### 2.6 PII (Personally Identifiable Information) Middleware

**Purpose:** Detect and handle sensitive data before/after it reaches the model — a compliance requirement in healthcare, finance, etc.

**Analogy:** Think of this like a redaction pen you'd use on legal documents. Before sharing a document, you black out sensitive information like social security numbers or addresses. This middleware does the same thing automatically for your AI conversations.

**Built-in detectors:** email · credit card (Luhn-validated) · IP address · MAC address · URL

**Strategies:**

| Strategy | Behavior | Analogy |
|---|---|---|
| `redact` | Replace with `[REDACTED_TYPE]` | Like covering a name with black marker |
| `mask` | Partially obscure (e.g., `****-****-****-1234`) | Like showing only the last 4 digits of a credit card |
| `hash` | Deterministic hashing | Like a secret code — the same input always produces the same output |
| `block` | Raise an exception | Like a gate that stops you completely |

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

**Custom detectors** — needed because country-specific ID formats can't all ship as built-ins:

```python
# Regex pattern
import re
aadhaar_pattern = re.compile(r"\b\d{12}\b")
PIIMiddleware("aadhaar", detector=aadhaar_pattern, strategy="mask")

# Custom function (for structured codes)
def detect_booking_code(content: str) -> list[dict]:
    matches = []
    for match in re.finditer(r"BK\d{4}", content):
        matches.append({"text": match.group(0), "start": match.start(), "end": match.end()})
    return matches

PIIMiddleware("booking_code", detector=detect_booking_code, strategy="mask")
```

---

### 2.7 Todo List Middleware

**Purpose:** Break a complex user request into actionable steps automatically.

**Analogy:** Think of this like a personal assistant who, when you say "I need to plan a party," creates a checklist: "1. Choose date, 2. Book venue, 3. Send invitations, 4. Order food." The assistant then checks off items as they're completed.

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

**Why not just prompt for it?** Plain instructions don't reliably produce a maintained, structured object the model keeps updating turn over turn. This middleware gives the agent a structured planning object that persists and updates across turns.

---

### 2.8 LLM Tool Selector Middleware

**Purpose:** Reduce context (and cost) by only sending the model the tools relevant to the current request.

**Analogy:** Imagine a mechanic with 50 different tools in their toolbox. When a customer brings in a flat tire, the mechanic doesn't pull out all 50 tools — they only bring the ones needed for changing a tire. This middleware does the same filtering for your agent.

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

**Under the hood:** This middleware uses structured output — it asks a (potentially cheaper) model which tools are actually relevant to the current query, and only forwards that filtered subset to the main model call.

---

### 2.9 Tool Error Middleware

**Purpose:** Convert raw tool exceptions into clean, model-facing messages instead of leaking internal details.

**Analogy:** Think of this like a friendly waiter who, when the kitchen makes a mistake, tells you "I'm so sorry, your dish will be ready in 5 more minutes" instead of shouting "The chef burned the steak!" to the entire restaurant.

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

**Key insight:** Tools are often third-party or shared, so you can't always change their internal definition — handling the failure gracefully at the middleware level is the more general solution.

---

### 2.10 Tool Retry Middleware

**Purpose:** Automatically retry transient tool failures (network blips, timeouts) with exponential backoff.

**Analogy:** Imagine you're at a restaurant and the waiter tries to bring your food, but the door is temporarily blocked. They try again after 1 second, then 2 seconds, then 4 seconds. This middleware does the same thing for failed API calls.

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

**The Backoff Math:**
```
delay = initial_delay × (backoff_factor ^ retry_number)
```
- Retry 0: 1 second
- Retry 1: 2 seconds
- Retry 2: 4 seconds

**Why this matters:** If a service is briefly down, hammering it with instant retries doesn't help — waiting a little longer between attempts gives the underlying issue a real chance to resolve.

**A Surprising Behavior:** With `max_retries=3` and `on_failure="continue"`, the middleware itself tries 4 times. But if all fail, the model sees the error and might independently decide to try again — triggering a second full cycle of attempts. This is the model's fuzzy, non-deterministic behavior, not a bug.

---

### 2.11 LLM Tool Emulator Middleware

**Purpose:** Simulate specific tool calls with an LLM instead of executing the real tool — useful for safe testing.

**Analogy:** Think of this like using a flight simulator instead of actually flying a plane. You get the experience and can practice scenarios without the real risk or cost.

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

**When to use:** Testing and development — validating an agent's overall logic without the cost, risk, or side effects of real external actions.

---

## 🛡️ Custom Guardrails

For validation logic beyond the built-ins, write custom middleware that hooks in **before** or **after** the agent runs.

### Before-Agent Guardrails (Deterministic Input Filter)

Runs once at the start of each invocation — good for auth checks, rate limiting, or blocking disallowed requests.

**Analogy:** Like a bouncer at a club checking IDs before letting anyone in.

```python
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

**Decorator Syntax (Equivalent):**

```python
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

### After-Agent Guardrails (Model-Based Safety Check)

Runs once on the final response — good for LLM-judged safety checks, quality validation, or compliance scans.

**Analogy:** Like a quality control inspector checking products before they ship out.

```python
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

### Combining Multiple Guardrails

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

## 🔑 Guardrail vs. Middleware

**Analogy:** Think of guardrails as the *goal* (keeping the car on the road) and middleware as the *mechanism* (the actual metal barrier installed on the road). They aren't competing systems — guardrails need to be implemented *as* middleware.

| Concept | Definition |
|---|---|
| **Guardrail** | The goal — protecting the agent from doing something undesirable |
| **Middleware** | The mechanism — a specific way to achieve that goal |

Even something as simple as a tool call limit already counts as a guardrail, since it's a deliberate constraint on behavior.

**Where compliance comes from:** Compliance itself isn't defined by the framework — it's defined externally, by company policy, government regulation, or industry certification (HIPAA, GDPR, SOC 2, etc.).

---

## 📋 Middleware Ordering

Multiple middlewares can be attached to a single agent without issue — no need for a separate agent per concern.

**Analogy:** Like layers in a cake. Each layer adds something different, and the order matters — you don't put the frosting before the cake layers. Similarly, PII redaction should run before the model call, not after.

- They don't run in random order: either a defined priority applies, or they run in the order declared
- Middlewares are generally written not to collide with each other
- Example: PII redaction should run before the model call

---

## 🏢 Real-World Applications

| Industry | Application | Middleware Used |
|---|---|---|
| **Fintech** | Fraud detection hooks | Rate-limiting middleware |
| **Healthcare** | HIPAA compliance | PII middleware |
| **Customer Support** | Refund approval gates | HITL middleware |
| **Internal Tools** | Audit logging | Custom tool-call wrappers |
| **E-commerce** | Cost management | Model fallback, tool selector |
| **Development** | Safe testing | Tool emulator middleware |

---

## 💬 Live Q&A Highlights

| Question | Answer |
|---|---|
| **What's the difference between Tool Error and Tool Retry middleware?** | Tool Error handles a failure gracefully once, converting it into a readable tool message without retrying. Tool Retry actively retries the failed call itself, with configurable backoff. |
| **Why does a tool call limit produce a tool message instead of an interrupt?** | An interrupt exists to ask a human for a decision; a call-limit rejection needs no human input — it's simply refused and reported back as information. |
| **Do always_include tools count against max_tools in the LLM Tool Selector?** | No — they're always sent and don't count against the limit. |
| **If PII is hashed, can the agent still complete a real booking using that value?** | Not directly from the hash — a separate lookup step, outside the model's view, resolves the hash back to a real value only when a tool genuinely needs it. |
| **Can onError support more than one handler function?** | No — a single function is expected, but it has full access to the exception, tool name, and request. |
| **Is tool selection the same as dynamic tool loading from the earlier class?** | No — dynamic tool loading filters based on known state (e.g., user type); tool selection filters based on the current query's content. |
| **Why did the flaky tool get called 8 times instead of 4 with max_retries=3?** | The middleware's own cycle accounts for 4 calls; the model, seeing the failure tool message, independently asked for the tool to be retried again — a consequence of the model's fuzzy, non-deterministic behavior, not a bug. |
| **Why wrap tool errors as a tool message instead of just fixing the tool itself?** | Tools are often third-party or shared, so you can't always change their internal definition — handling the failure gracefully at the middleware level is the more general solution. |
| **What's the difference between LangChain and LangGraph?** | LangChain sits on top of LangGraph as a more convenient, somewhat abstracted interface. LangGraph becomes worth reaching for when an application needs very precise, deterministic control internally — deeper control over checkpointers, stores, and interrupts. |
| **Is PII handled by guardrails or middleware?** | Guardrail is the concept; middleware is the mechanism — not competing systems. |

---

## ✅ Action Items

- [ ] **Summarization:** Recreate the `SummarizationMiddleware` example with your own `trigger`/`keep` values; watch it fire on a long conversation.
- [ ] **HITL:** Build the `HumanInTheLoopMiddleware` send-email demo; resolve the interrupt both via `Command(resume=...)` and your own approve/reject logic.
- [ ] **Limits:** Add a model call limit and a tool call limit to an existing agent; deliberately trigger both.
- [ ] **Fallback:** Set up `ModelFallbackMiddleware` and simulate a primary-model failure to confirm fallback fires.
- [ ] **PII:** Write one custom PII detector (`re`-based) for an ID format relevant to your own use case; try all four strategies (block, redact, mask, hash).
- [ ] **Todo List:** Add `TodoListMiddleware` to an existing multi-tool agent and give it a genuinely multi-step request — watch the plan populate and update live.
- [ ] **Tool Selector:** Build the `show_tools` custom middleware using `@wrap_model_call` yourself, and use it to verify `LLMToolSelectorMiddleware`'s filtering on at least three different queries.
- [ ] **Tool Error:** Write a tool that deliberately raises a ValueError, then wrap it with `ToolErrorMiddleware` and confirm the agent no longer crashes.
- [ ] **Tool Retry:** Set up `ToolRetryMiddleware` on a tool that always fails, and manually verify the backoff timing matches `initial_delay × (backoff_factor ^ retry_number)`.
- [ ] **Tool Emulator:** Try `LLMToolEmulator` on a tool you don't want to actually call yet, and compare its fabricated response against what the real tool would return.
- [ ] **Custom Guardrails:** Write one `before_agent` and one `after_agent` custom guardrail from scratch.
- [ ] **Concept Review:** Be ready to explain, in your own words, the difference between a guardrail and middleware (recurring interview-style question).

---

## 📚 Additional Resources

- [Middleware Documentation](https://docs.langchain.com/oss/python/langchain/middleware) — Complete guide to custom middleware
- [Middleware API Reference](https://reference.langchain.com/python/langchain/middleware/)
- [Human-in-the-Loop Guide](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Testing Agents](https://docs.langchain.com/oss/python/langchain/test/) — Strategies for testing safety mechanisms

---

## 📝 Key Principles

1. **Checkpointer required** — HITL and persistent (`thread_limit`) limits need `InMemorySaver()` or another checkpoint store
2. **Stack multiple middlewares** — order matters (e.g., PII redaction before the model call)
3. **Thread safety** — use `config={"configurable": {"thread_id": "unique_id"}}` for persistence across interrupts/resumes
4. **Graceful degradation** — prefer `exit_behavior="end"` for limits and `on_failure="continue"` for retries over hard exceptions, unless a hard stop is actually desired
