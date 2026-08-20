"""Class 12: Mastering Middleware — Control, Guardrails & Human-in-the-Loop

 Day 12 (8 August 2026)

========================================
Quick Updates
========================================
- Today's focus is middleware as the control layer around an agent.
- We move from simple agent behavior to decision-making, safety, and human oversight.
- The class also reinforces that LangChain has now been the main framework for several weeks,
  which is intentional: once you understand LangChain well, other agent frameworks become easier.
- The notebook follows the same flow as the lecture: setup, tool definitions, middleware examples,
  and practical guardrails.

========================================
Why Middleware Exists
========================================
Middleware exists to give developers control over what happens inside an agent.
Before middleware, an agent could already reason, call tools, and answer questions,
but developers still needed a structured way to intervene between the model, tools,
prompts, and messages.

Middleware hooks into the agent loop at critical points:
- before the agent runs,
- after the agent runs,
- before the model is called,
- after the model is called,
- before a tool is called,
- and after a tool is called.

A simple flow looks like this:

```mermaid
flowchart LR
    A[Request] --> M1[before model]
    M1 --> B[Model call]
    B --> M2[after model]
    M2 --> C[Tool call]
    C --> M3[after tool]
    M3 --> D[Final result]
```

The important takeaway is that middleware is the same basic idea as regular code control flow:
you decide what should happen before or after an action runs.

========================================
Middleware #1: Summarization
========================================
Summarization middleware helps solve the growing-context problem.
As a conversation grows longer, the agent history becomes larger and more expensive to carry.
Summarization compresses older history so the conversation stays manageable.

Example:
```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model=model,
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="anthropic:claude-haiku",
            trigger=("tokens", 4000),
            keep=("messages", 10),
        )
    ],
)
```

Key configuration ideas:
- model: the model used for summarizing older context; it does not need to be the same as the main model.
- trigger: when summarization begins, such as token count, message count, or context fullness.
- keep: how much recent conversation remains untouched after summarization.

Why it matters:
- long conversations can become too expensive,
- context windows can fill up,
- and the model may lose track of important detail.

Trade-off:
Summarization can lose information, so if important details must survive, they should be saved in
long-term memory instead of only relying on the summary.

========================================
Middleware #2: Human-in-the-Loop (HITL)
========================================
Human-in-the-Loop (HITL) middleware pauses agent execution so a human can approve,
edit, or reject a proposed tool call before it actually runs.

This is essential for actions that change the real world, such as:
- sending an email,
- deleting a record,
- cancelling an order,
- spending money,
- or changing data.

Why it only applies to tool calls:
The model's reasoning itself is not the risky part; the tool call is the point where the agent
actually acts. That is the moment worth pausing on.

Example:
```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model=model,
    tools=[read_email, send_email],
    checkpointer=checkpointer,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                "read_email": False,
            }
        )
    ],
)
```

The flow is:
Request -> Brain -> Tool -> HITL interrupt -> human decision -> continue or stop

The four common decision types are:
- approve: run the tool as proposed,
- edit: change the arguments before running,
- reject: skip the tool call and return feedback,
- respond: return a human message directly for ask-user style tools.

The notebook demonstrates this with a cancel-booking example. The agent wants to cancel a booking,
but the middleware pauses to ask for approval before the side effect occurs.

Important note:
This is not the same as a support chatbot handing the whole conversation to a human. That is a transfer.
True HITL keeps the agent in the loop and pauses only the risky action.

========================================
Middleware #3 & #4: Model Call Limit and Tool Call Limit
========================================
The idea behind these middlewares is cost and control.
If an agent loops indefinitely or makes too many calls, the cost rises fast and the workflow becomes noisy.

Model call limit:
- limits how many times the model is called during a run.
- useful for preventing runaway reasoning loops.

Tool call limit:
- limits how many tool calls are allowed.
- useful for preventing repeated or excessive tool use.

The right limit depends on domain knowledge.
For example, a web-search agent might need only a handful of searches, while a business workflow may require
many more. The developer should set the limit based on the use case, not arbitrary guesswork.

========================================
Middleware #5: Model Fallback
========================================
Model fallback middleware allows the agent to switch to a secondary model if the primary one fails.

Example:
```python
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model=model,
    middleware=[
        ModelFallbackMiddleware(
            model="openai:gpt-5.4-mini",
        )
    ],
)
```

This is useful when:
- the primary provider is down,
- an API key expires,
- a 404 or hard error happens,
- or the main model cannot be reached.

Important distinction:
Fallback is not routing based on speed or cost. It only kicks in when the primary model genuinely fails.

========================================
Middleware #6: PII Detection
========================================
PII stands for Personally Identifiable Information.
Examples include:
- email addresses,
- phone numbers,
- dates of birth,
- government IDs,
- passwords,
- credit card numbers.

PII middleware helps prevent these values from reaching the model.

Example:
```python
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model=model,
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

Two strategies are commonly used:
- redact: remove the sensitive value entirely,
- mask: hide part of it while keeping the presence of the value visible.

Custom PII detection is also possible with regex patterns.
Example:
```python
import re
from langchain.agents.middleware import PIIMiddleware

aadhaar_pattern = re.compile(r"\b\d{12}\b")

agent = create_agent(
    model=model,
    middleware=[
        PIIMiddleware("aadhaar", detector=aadhaar_pattern, strategy="mask"),
    ],
)
```

A key distinction:
- guardrail is the concept: protect the agent from doing something unsafe.
- middleware is the mechanism used to implement that guardrail.

========================================
Multiple Middlewares Together
========================================
It is normal to attach several middlewares to one agent at the same time.
For example, an agent can have:
- summarization for context compression,
- HITL for approval,
- a tool limit for safety,
- and PII detection for privacy.

The middlewares generally work well together, and their order is either defined or follows declaration order.

========================================
LangChain vs LangGraph
========================================
A common question is: when should we use LangChain + middleware, and when should we move to LangGraph?

The simple answer is:
- LangChain is great for convenient agent building with built-in abstractions.
- LangGraph becomes important when you need deeper control over state, checkpoints, interrupts, and deterministic execution.

For many simple agents, especially basic RAG and small tool-using systems, LangChain middleware is enough.
LangGraph becomes more valuable when the workflow must be very precise and stateful.

========================================
What Comes Next
========================================
The next class moves from built-in middleware to custom middleware.
That means we will learn how to write our own middleware from scratch instead of only using LangChain's provided ones.

========================================
Live Q&A Highlights
========================================
Q: Why not just instruct the model to avoid repeated tool use?
A: Prompts are not reliable enough. Code-level control is stronger and more dependable.

Q: Does middleware add latency?
A: Sometimes yes, especially if it calls another model such as summarization does. Pure code checks add very little overhead.

Q: Can I configure multiple approval levels for HITL?
A: Not out of the box. That requires custom middleware.

Q: Is PII handling a guardrail or middleware?
A: It is a guardrail concept implemented through middleware.

Q: Can multiple middlewares be attached to one agent?
A: Yes, absolutely.

Q: When should I use LangChain plus middleware versus LangGraph?
A: Use LangChain for most straightforward agents. Use LangGraph when precise state and control are needed.

========================================
Action Items After Class 12
========================================
- Recreate the SummarizationMiddleware example with your own trigger and keep settings.
- Build a HumanInTheLoopMiddleware example and manually resolve the interrupt.
- Add a model call limit and a tool call limit to an existing agent.
- Set up ModelFallbackMiddleware and simulate a primary-model failure.
- Write one custom PII detector using regex.
- Be ready to explain the difference between a guardrail and middleware.
- Prepare for custom middleware in the next class.

========================================
Key Takeaway
========================================
Middleware turns a basic model into a more controlled, safer, and more reliable agent.
It adds safety, memory management, approval steps, fallback behavior, and cost control.
"""
