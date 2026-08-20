# 🐚 Class 14 — Shell Tools & Custom Middleware

## 📌 Overview

Class 14 focuses on **Shell Tool Middleware** and **Custom Middleware** in LangChain agents.

The session covers how AI agents can interact with real file systems and terminals, how middleware intercepts agent execution, the six major middleware hooks, decorator-based and class-based middleware, state management, execution order, dynamic model selection, dynamic tool selection, retries, tracing, and production-oriented middleware design.

The practical goal is to understand how frameworks such as Claude Code, Cursor, and GitHub Copilot combine an LLM with controlled access to a real execution environment.

---

## 🎯 Learning Objectives

By the end of this class, you should understand:

* How `ShellToolMiddleware` gives an agent shell access
* Where shell commands actually execute
* How workspace isolation works
* Host vs Docker-based execution policies
* What custom middleware is and why it is needed
* Node-style vs wrap-style hooks
* All six major middleware hooks
* `before_agent`
* `before_model`
* `wrap_model_call`
* `after_model`
* `wrap_tool_call`
* `after_agent`
* Decorator-based middleware
* Class-based middleware
* Custom agent state
* State updates using reducers
* `Command` and `ExtendedModelResponse`
* Middleware execution order
* Agent jumps
* Dynamic model selection
* Dynamic prompt modification
* Dynamic tool selection
* Tool-call monitoring
* Middleware inheritance
* Error handling and retry logic
* Middleware tracing
* Production best practices

---

# 🐚 1. Shell Tool Middleware

One of the most important demonstrations of the session was connecting an agent to a real shell.

Coding agents such as Claude Code, Cursor, and GitHub Copilot fundamentally need access to an execution environment to:

* Create files
* Read files
* Modify files
* Delete files
* Execute scripts
* Run commands
* Build applications
* Test code

The LLM decides **what should happen**, while the shell environment performs the actual operation.

---

## Basic Shell Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
)

cinebot_shell_agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/content/cinebot_workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ],
)
```

---

## 🧠 Where Does the Agent Execute?

If the agent is running inside Google Colab:

```text
LLM
 │
 │ Decides which command to execute
 ▼
Agent
 │
 │ Shell tool call
 ▼
Google Colab Machine
 │
 ├── Create files
 ├── Modify files
 ├── Execute scripts
 └── Delete files
```

The model provider supplies the **reasoning capability**.

The actual command executes on the machine where the agent is running.

For example:

```python
workspace_root="/content/cinebot_workspace"
```

restricts the agent's file operations to that workspace.

---

# 🔐 2. Execution Policies

| Policy                  | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `HostExecutionPolicy()` | Direct access to the host machine            |
| Docker-based policy     | Runs operations inside an isolated container |
| Codex sandbox policy    | Uses an existing Codex CLI sandbox           |

For trusted development environments:

```python
HostExecutionPolicy()
```

can be appropriate.

For production or untrusted workloads, isolation is significantly safer.

---

# 🧪 3. Shell Agent Examples

The shell agent can perform tasks such as:

```text
Create a reports folder
```

```text
Research the NBA and save it to nba_research.txt
```

```text
Create Hello_world.py
```

```text
Create two folders, execute a script, and delete it
```

```text
Create and run a calculator application
```

The execution pattern is:

```text
User Request
     ↓
LLM
     ↓
Tool Call
     ↓
Shell Command
     ↓
Real File/System Operation
     ↓
Tool Result
     ↓
LLM
     ↓
Final Response
```

---

# 🪝 4. What Is Custom Middleware?

Built-in middleware handles generic requirements such as:

* Human-in-the-loop
* PII protection
* Tool-call limits
* Other common agent controls

But businesses often have application-specific rules.

For example:

```text
A customer cannot book more than two movies
```

```text
The agent must not mention competing cinema chains
```

```text
Every cancellation must be logged
```

```text
VIP tools should only be visible to VIP users
```

These rules are application-specific.

That is where **custom middleware** becomes useful.

---

# 🧩 5. Middleware Hooks

Middleware provides extension points where custom logic can intercept agent execution.

There are two major categories:

### Node-style hooks

Run sequentially at specific execution points.

### Wrap-style hooks

Wrap model or tool calls and provide direct control over execution.

---

## Six Major Hooks

| Hook              | Execution                  |
| ----------------- | -------------------------- |
| `before_agent`    | Before the agent starts    |
| `before_model`    | Before every model call    |
| `wrap_model_call` | Around every model call    |
| `after_model`     | After every model response |
| `wrap_tool_call`  | Around every tool call     |
| `after_agent`     | After the agent completes  |

---

# 🔄 6. Agent Execution Lifecycle

```text
User Request
     │
     ▼
before_agent
     │
     ▼
before_model
     │
     ▼
wrap_model_call
     │
     ▼
     Model
     │
     ▼
after_model
     │
     ▼
wrap_tool_call
     │
     ▼
     Tool
     │
     └──────────────┐
                    │
                    ▼
              before_model
                    │
                    ▼
              Agentic Loop
                    │
                    ▼
               after_agent
```

---

# 🟡 7. `before_agent`

Runs once at the beginning of an agent invocation.

Useful for:

* Initialization
* Database connections
* Loading resources
* Initial validation
* Setup logic

```python
from langchain.agents.middleware import before_agent
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from typing import Any

@before_agent
def connect_to_db(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    print("Connected to DB")

    return None
```

---

# 🔵 8. `after_agent`

Runs once after the agent finishes.

Useful for:

* Cleanup
* Closing connections
* Final logging
* Resource release

```python
from langchain.agents.middleware import after_agent

@after_agent
def disconnect_from_db(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    print("Disconnected from DB")

    return None
```

---

# 🟠 9. `before_model`

Runs before every model call.

Useful for:

* Logging
* Validation
* State inspection
* Preparing model context
* Security checks

```python
from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from typing import Any

@before_model
def log_before_model(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    print(
        f"About to call model with "
        f"{len(state['messages'])} messages"
    )

    return None
```

Returning:

```python
None
```

means:

```text
Observe the execution
but do not modify anything.
```

---

# 🔴 10. `after_model`

Runs after every model response.

Useful for:

* Logging responses
* Validation
* Output inspection
* State updates
* Safety checks

```python
from langchain.agents.middleware import after_model

@after_model
def log_response(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    print(
        f"Model returned: "
        f"{state['messages'][-1].content}"
    )

    return None
```

---

# 🟣 11. `wrap_model_call`

`wrap_model_call` provides direct control over the model request.

It can be used for:

* Dynamic model selection
* Retries
* Fallbacks
* Caching
* Prompt transformation
* Tool filtering
* Model configuration changes

```python
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from typing import Callable

@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:

    for attempt in range(3):

        try:
            return handler(request)

        except Exception as e:

            if attempt == 2:
                raise

            print(
                f"Retry {attempt + 1}/3 after error: {e}"
            )
```

---

# 🛠️ 12. `wrap_tool_call`

Wraps tool execution.

Useful for:

* Tool monitoring
* Logging
* Validation
* Error handling
* Permission checks
* Tool result transformation

```python
from collections.abc import Callable
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command

@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[
        [ToolCallRequest],
        ToolMessage | Command,
    ],
) -> ToolMessage | Command:

    print(
        f"Executing tool: "
        f"{request.tool_call['name']}"
    )

    print(
        f"Arguments: "
        f"{request.tool_call['args']}"
    )

    try:
        result = handler(request)

        print("Tool completed successfully")

        return result

    except Exception as e:
        print(f"Tool failed: {e}")
        raise
```

---

# ⚖️ 13. `before_model` vs `wrap_model_call`

This distinction is critical.

| Feature                 | `before_model`             | `wrap_model_call` |
| ----------------------- | -------------------------- | ----------------- |
| Access state            | Yes                        | Yes               |
| Access runtime          | Yes                        | Yes               |
| Access request          | No direct request object   | Yes               |
| Modify model            | Limited                    | Yes               |
| Modify tools            | No direct request override | Yes               |
| Modify messages         | Limited/state-based        | Yes               |
| Retry model call        | No                         | Yes               |
| Dynamic model selection | Not ideal                  | Yes               |
| Wrap execution          | No                         | Yes               |

Think of it as:

```text
before_model
    ↓
Observe / prepare
    ↓
wrap_model_call
    ↓
Control the actual model request
    ↓
Model
```

---

# 🎯 14. Dynamic Model Selection

A powerful real-world use case is choosing a model based on conversation complexity.

```python
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from typing import Callable

complex_model = init_chat_model(
    "claude-sonnet-4-6"
)

simple_model = init_chat_model(
    "claude-haiku-4-5-20251001"
)

@wrap_model_call
def dynamic_model(
    request: ModelRequest,
    handler: Callable[
        [ModelRequest],
        ModelResponse,
    ],
) -> ModelResponse:

    if len(request.messages) > 10:
        model = complex_model
    else:
        model = simple_model

    return handler(
        request.override(model=model)
    )
```

The idea:

```text
Short / Simple Conversation
          ↓
      Cheap Model

Long / Complex Conversation
          ↓
     Capable Model
```

This can improve:

* Cost efficiency
* Latency
* Scalability
* Model utilization

---

# 🔐 15. Dynamic Tool Selection

Tools can also be filtered dynamically.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from typing import Callable

@wrap_model_call
def select_tools(
    request: ModelRequest,
    handler: Callable[
        [ModelRequest],
        ModelResponse,
    ],
) -> ModelResponse:

    relevant_tools = select_relevant_tools(
        request.state,
        request.runtime,
    )

    return handler(
        request.override(
            tools=relevant_tools
        )
    )
```

Benefits:

```text
Fewer tools
    ↓
Smaller prompt
    ↓
Less confusion
    ↓
Better tool selection
    ↓
Better accuracy
```

It can also provide permission-based tool access.

---

# 🏷️ 16. VIP Tool Gating

Middleware can dynamically remove tools based on state.

```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def gate_vip_tools(request, handler):

    is_vip = request.state.get(
        "is_vip_member",
        False,
    )

    if not is_vip:

        allowed = [
            tool
            for tool in request.tools
            if tool.name != "book_vip_lounge"
        ]

        request = request.override(
            tools=allowed
        )

    return handler(request)
```

This allows the same agent to expose different capabilities to different users.

---

# 🏗️ 17. Decorator-Based Middleware

Decorator-based middleware is ideal for:

* One hook
* Simple logic
* Quick experimentation
* Prototyping

Example:

```python
from langchain.agents.middleware import before_model
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from typing import Any

@before_model
def log_model_call(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    print(
        f"Messages: {len(state['messages'])}"
    )

    return None
```

---

# 🏢 18. Class-Based Middleware

Class-based middleware is better when you need:

* Multiple hooks
* Internal state
* Configuration
* Reusability
* Sync and async implementations
* More complex business logic

```python
from langchain.agents.middleware import AgentMiddleware

class CallCounterMiddleware(AgentMiddleware):

    def __init__(self, warn_after: int = 3):

        super().__init__()

        self._num_calls = 0
        self.warn_after = warn_after

    def before_model(
        self,
        state,
        runtime,
    ):

        self._num_calls += 1

        if self._num_calls > self.warn_after:

            print(
                "High number of model calls."
            )

        return None
```

---

# 📊 19. Decorator vs Class

| Feature               | Decorator | Class     |
| --------------------- | --------- | --------- |
| Simple middleware     | Excellent | Good      |
| Single hook           | Excellent | Good      |
| Multiple hooks        | Limited   | Excellent |
| Internal state        | Limited   | Excellent |
| Configuration         | Limited   | Excellent |
| Reusability           | Moderate  | Excellent |
| Sync + async          | Limited   | Excellent |
| Production complexity | Moderate  | Excellent |

### Rule of thumb

```text
Simple hook
    ↓
Decorator

Complex / reusable middleware
    ↓
AgentMiddleware class
```

---

# 🧬 20. Extending Existing Middleware

Custom middleware can extend built-in middleware.

Example:

```python
class MyPIIMiddleware(PIIMiddleware):

    def wrap_model_call(
        self,
        request,
        handler,
    ):

        response = handler(request)

        return ExtendedModelResponse(
            model_response=response,
            command=Command(
                update={
                    "trace_layer": "outer",
                    "messages": [
                        SystemMessage(
                            content="[Outer ran]"
                        )
                    ],
                }
            ),
        )
```

Python inheritance allows you to:

* Reuse existing behavior
* Add new hooks
* Customize existing hooks
* Extend built-in middleware

Be careful when overriding a parent hook because replacing the method can remove the parent's behavior.

---

# 🧠 21. Custom State Schema

Middleware can extend the agent state.

```python
from langchain.agents.middleware import AgentState
from typing_extensions import NotRequired

class CustomState(AgentState):

    model_call_count: NotRequired[int]

    user_id: NotRequired[str]
```

This enables middleware to:

* Track counters
* Store flags
* Share information between hooks
* Maintain user context
* Implement rate limiting
* Track usage
* Perform audit logging
* Make conditional decisions

---

# 🔢 22. State Tracking Example

```python
from langchain.agents.middleware import (
    after_model,
    AgentState,
)
from langgraph.runtime import Runtime
from typing import Any
from typing_extensions import NotRequired

class TrackingState(AgentState):

    model_call_count: NotRequired[int]


@after_model(state_schema=TrackingState)
def increment_after_model(
    state: TrackingState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    return {
        "model_call_count":
            state.get("model_call_count", 0) + 1
    }
```

---

# 🔄 23. State Updates

### Node-style hooks

Return a dictionary:

```python
return {
    "model_call_count": 10
}
```

The dictionary is applied to the agent state through graph reducers.

### Wrap-style hooks

For model calls, use:

```python
ExtendedModelResponse
```

with:

```python
Command(update={...})
```

Example:

```python
from langgraph.types import Command
from langchain.agents.middleware import (
    ExtendedModelResponse,
)

return ExtendedModelResponse(
    model_response=response,
    command=Command(
        update={
            "last_model_call_tokens": 150
        }
    ),
)
```

---

# 🧩 24. Middleware Composition

Multiple middleware layers can compose state updates.

```text
Middleware 1
     ↓
Middleware 2
     ↓
Middleware 3
     ↓
Model
```

For state conflicts:

```text
Inner Middleware
       ↓
Outer Middleware
       ↓
Outer value wins
```

For additive message reducers:

```text
Inner message
+
Outer message
=
Both messages
```

---

# 🔄 25. Middleware Execution Order

Consider:

```python
agent = create_agent(
    model="gpt-5.5",
    middleware=[
        middleware1,
        middleware2,
        middleware3,
    ],
)
```

### Before hooks

```text
middleware1.before_agent()
        ↓
middleware2.before_agent()
        ↓
middleware3.before_agent()
```

### Before model

```text
middleware1.before_model()
        ↓
middleware2.before_model()
        ↓
middleware3.before_model()
```

### Wrap model

```text
middleware1.wrap_model_call()
        ↓
middleware2.wrap_model_call()
        ↓
middleware3.wrap_model_call()
        ↓
Model
```

### After model

```text
middleware3.after_model()
        ↓
middleware2.after_model()
        ↓
middleware1.after_model()
```

### After agent

```text
middleware3.after_agent()
        ↓
middleware2.after_agent()
        ↓
middleware1.after_agent()
```

### Core rule

```text
before_*  → First to Last

wrap_*    → Nested

after_*   → Last to First
```

---

# 🚦 26. Agent Jumps

Middleware can terminate or redirect execution using:

```python
jump_to
```

Available targets include:

```text
'end'
'tools'
'model'
```

Example:

```python
from langchain.agents.middleware import (
    after_model,
    hook_config,
    AgentState,
)
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

@after_model
@hook_config(can_jump_to=["end"])
def check_for_blocked(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:

    last_message = state["messages"][-1]

    if "BLOCKED" in last_message.content:

        return {
            "messages": [
                AIMessage(
                    "I cannot respond to that request."
                )
            ],
            "jump_to": "end",
        }

    return None
```

---

# 🔁 27. Retry Middleware

Wrap-style middleware is useful for retry logic.

```python
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from typing import Callable

@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[
        [ModelRequest],
        ModelResponse,
    ],
) -> ModelResponse:

    for attempt in range(3):

        try:

            return handler(request)

        except Exception as e:

            if attempt == 2:
                raise

            print(
                f"Retry {attempt + 1}/3 "
                f"after error: {e}"
            )
```

The handler can be called:

```text
0 times → short circuit

1 time → normal execution

Multiple times → retry/fallback behavior
```

---

# ✍️ 28. Dynamic Prompt Middleware

Middleware can modify the system prompt dynamically.

```python
from collections.abc import Callable

from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    wrap_model_call,
)
from langchain.messages import SystemMessage

@wrap_model_call
def add_context(
    request: ModelRequest,
    handler: Callable[
        [ModelRequest],
        ModelResponse,
    ],
) -> ModelResponse:

    new_content = (
        list(
            request.system_message.content_blocks
        )
        + [
            {
                "type": "text",
                "text": "Additional context.",
            }
        ]
    )

    new_system_message = SystemMessage(
        content=new_content
    )

    return handler(
        request.override(
            system_message=new_system_message
        )
    )
```

Important:

```python
request.system_message
```

is a `SystemMessage`.

Use:

```python
content_blocks
```

when modifying the system message so the existing structure is preserved.

---

# 📡 29. Custom Stream Transformers

Middleware can also register stream transformer factories.

This can be useful for:

* Counters
* Side-channel artifacts
* Partial outputs
* Wire-level redaction
* Tool activity
* Typed extension channels

Example:

```python
from langchain.agents.middleware import AgentMiddleware

class ToolActivityMiddleware(AgentMiddleware):

    transformers = (
        ToolActivityTransformer,
    )
```

Then:

```python
agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    middleware=[
        ToolActivityMiddleware()
    ],
)
```

This functionality requires:

```text
langchain >= 1.3.2
```

---

# 🔍 30. Middleware Tracing

Middleware hook spans can be traced.

A trace policy can control what gets recorded.

```python
from langchain.agents.middleware import (
    AgentMiddleware,
    TracePolicy,
    omit_payload,
)

class MyMiddleware(AgentMiddleware):

    trace_policy = TracePolicy(
        process_inputs=omit_payload
    )
```

Global configuration:

```python
from langchain.agents.middleware import (
    configure_trace_policy,
    TracePolicy,
    omit_payload,
)

configure_trace_policy(
    TracePolicy(
        process_inputs=omit_payload
    )
)
```

A middleware-level policy overrides the global default.

---

# 🛡️ 31. Security Considerations

Shell access is powerful and therefore requires strong isolation.

An agent with shell access may potentially:

```text
Create files
Modify files
Delete files
Execute programs
Access available resources
Interact with remote systems
```

Therefore:

```text
LLM
 +
Shell Access
 =
High Capability
```

but also:

```text
High Capability
 +
Weak Isolation
 =
High Risk
```

Prefer sandboxing for untrusted or production workloads.

---

# 🧠 32. PII Middleware Example

PII protection can require multiple hooks.

### Before model

Sensitive information can be masked before reaching the model:

```text
User Input
    ↓
before_model
    ↓
PII Redaction
    ↓
Model
```

### After model

Model-generated sensitive information can also be checked:

```text
Model
    ↓
after_model
    ↓
PII Validation
    ↓
User
```

This is why middleware often needs multiple lifecycle hooks rather than a single interception point.

---

# 🧱 33. Middleware Design Principles

Good middleware should follow these principles:

### Single responsibility

```text
One middleware
        ↓
One primary concern
```

Avoid combining unrelated business rules.

### Graceful error handling

A middleware bug should not unnecessarily crash the entire agent.

### Correct hook selection

Use:

```text
before_model
```

for observation, validation, and sequential logic.

Use:

```text
wrap_model_call
```

when the actual model request must be modified or controlled.

Use:

```text
wrap_tool_call
```

when tool execution needs control.

### Explicit state

Document custom state fields clearly.

### Independent testing

Test middleware independently before integrating it into a complete agent.

### Prefer built-in middleware

If LangChain already provides the required middleware, use it.

Create custom middleware only when there is a genuine application-specific requirement.

---

# 🏭 34. Production Use Cases

Custom middleware can support:

| Requirement            | Middleware Approach            |
| ---------------------- | ------------------------------ |
| Authentication context | Custom state                   |
| Authorization          | Dynamic tool selection         |
| PII protection         | `before_model` + `after_model` |
| Logging                | `before_model` / `after_model` |
| Cost optimization      | Dynamic model selection        |
| Retry logic            | `wrap_model_call`              |
| Fallback models        | `wrap_model_call`              |
| Tool monitoring        | `wrap_tool_call`               |
| Rate limiting          | Custom state + hooks           |
| Audit logging          | `after_model` / `after_agent`  |
| Prompt customization   | `wrap_model_call`              |
| Request filtering      | `before_model`                 |
| Early termination      | Agent jumps                    |
| Usage tracking         | Custom state                   |
| Resource management    | `before_agent` + `after_agent` |

---

# 💡 35. Important Q&A Insights

### Should login/session validation use an agent?

No.

Authentication and session validation are deterministic programming concerns.

Use normal application logic.

```text
Authentication
    ↓
Regular Code

Intelligent Decision
    ↓
Agent
```

---

### Is LangChain's agent graph a DAG?

No.

The agentic loop can cycle:

```text
Model
  ↓
Tool
  ↓
Model
  ↓
Tool
  ↓
Model
```

Therefore it is not a Directed Acyclic Graph.

---

### LangChain vs LangGraph?

```text
LangChain
    ↓
Higher-level agent development

LangGraph
    ↓
Lower-level graph/runtime control
```

LangGraph becomes especially useful when fine-grained graph control, custom state transitions, and complex orchestration are required.

---

### Does every agent step consume LLM tokens?

No.

LLM tokens are consumed when the model is actually called.

Regular Python execution does not consume LLM tokens.

```text
Python Logic
    ↓
No LLM tokens

LLM Call
    ↓
LLM tokens
```

---

### Should different agent frameworks be mixed in one project?

Generally, avoid unnecessary framework mixing.

Prefer:

```text
One framework
    ↓
Multiple agents
```

If independent systems need to communicate, use:

```text
API
```

or an agent-to-agent protocol such as:

```text
A2A
```

---

### Can shell middleware access a remote machine?

Yes, when the execution environment has legitimate access to that machine.

For example:

```text
Agent
  ↓
Local Shell
  ↓
SSH
  ↓
Remote Machine
```

The security boundary and credentials must be handled carefully.

---

### Can a browser-based web application directly access the user's terminal?

No.

Browsers intentionally sandbox access to the local machine.

Similar capabilities require a controlled access layer such as:

* Installed application
* IDE extension
* MCP
* Proper backend execution environment

---

# 🗺️ 36. Class Roadmap

```text
Class 14
   │
   ├── Shell Tools
   │
   ├── Built-in Middleware
   │
   ├── Custom Middleware
   │
   ├── Middleware Hooks
   │
   ├── State
   │
   ├── Dynamic Models
   │
   └── Dynamic Tools
          │
          ▼
         MCP
          │
          ▼
       LangGraph
          │
          ├── Runtime
          ├── Multi-Agent
          └── Memory
                │
                ▼
          Full Projects
```

---

# 📝 37. Practice Tasks

* [ ] Recreate the `ShellToolMiddleware` demo
* [ ] Create a file through the shell agent
* [ ] Execute a Python script through the agent
* [ ] Delete the generated file
* [ ] Inspect the agent message history
* [ ] Create a `before_agent` hook
* [ ] Create an `after_agent` hook
* [ ] Verify setup and teardown order
* [ ] Implement `before_model`
* [ ] Implement `after_model`
* [ ] Build dynamic model selection
* [ ] Create decorator-based middleware
* [ ] Convert it into class-based middleware
* [ ] Add internal middleware state
* [ ] Extend `PIIMiddleware`
* [ ] Implement middleware execution logging
* [ ] Test middleware execution order
* [ ] Implement a retry middleware
* [ ] Implement dynamic tool selection
* [ ] Experiment with agent jumps
* [ ] Explore custom state schemas
* [ ] Explore middleware tracing
* [ ] Prepare for MCP

---

# 📚 38. Quick Revision Cheat Sheet

```text
ShellToolMiddleware
    ↓
Give agent controlled shell access

before_agent
    ↓
Runs once before agent execution

before_model
    ↓
Runs before every model call

wrap_model_call
    ↓
Controls model request/execution

after_model
    ↓
Runs after every model response

wrap_tool_call
    ↓
Controls tool execution

after_agent
    ↓
Runs once after agent execution
```

---

## Middleware Selection

```text
Need simple logging?
        ↓
before_model / after_model

Need setup or cleanup?
        ↓
before_agent / after_agent

Need retry?
        ↓
wrap_model_call

Need dynamic model?
        ↓
wrap_model_call

Need dynamic tools?
        ↓
wrap_model_call

Need tool monitoring?
        ↓
wrap_tool_call

Need persistent custom state?
        ↓
AgentMiddleware class
```

---

## Execution Order

```text
BEFORE
1 → 2 → 3

WRAP
1 → 2 → 3 → MODEL → 3 → 2 → 1

AFTER
3 → 2 → 1
```

---

## Decorator vs Class

```text
Decorator
    ↓
Simple
Single Hook
Quick Prototype

Class
    ↓
Complex
Multiple Hooks
State
Configuration
Reusable
Production
```

---

# 🔗 Resources

### LangChain Custom Middleware Documentation

[https://docs.langchain.com/oss/python/langchain/middleware](https://docs.langchain.com/oss/python/langchain/middleware)

### LangChain Documentation Index

[https://docs.langchain.com/llms.txt](https://docs.langchain.com/llms.txt)

### Class 14 Colab Notebook

[https://colab.research.google.com/drive/1CpnGhWhGG4r8NCIoh0WEmcPEVb6KJ2TH?usp=sharing](https://colab.research.google.com/drive/1CpnGhWhGG4r8NCIoh0WEmcPEVb6KJ2TH?usp=sharing)

---

# 🚀 Key Takeaway

> **Middleware is the control layer between your agent's reasoning and its execution.**

The LLM provides intelligence.

Tools provide capabilities.

Middleware provides **control, safety, customization, observability, and business-specific behavior**.

A useful mental model is:

```text
                 ┌──────────────────┐
                 │       USER       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │      AGENT       │
                 └────────┬─────────┘
                          │
              ┌───────────▼───────────┐
              │      MIDDLEWARE       │
              │                       │
              │ Validation            │
              │ Security              │
              │ PII                   │
              │ Logging               │
              │ Model Routing         │
              │ Tool Selection        │
              │ Retry / Fallback      │
              │ State Management      │
              └───────────┬───────────┘
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       ┌───────────┐             ┌───────────┐
       │   MODEL   │             │   TOOLS   │
       └───────────┘             └───────────┘
             │                         │
             └────────────┬────────────┘
                          ▼
                   EXECUTION RESULT
```

---

## 🎯 Class 14 in One Sentence

**Shell tools give agents real-world execution capabilities, while custom middleware gives developers precise control over how those agents reason, call models, use tools, manage state, enforce policies, and behave in production.**
