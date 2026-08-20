"""Class 11 Notes
Agents, Middleware & Memory — Giving CineBot a Mind
Agentic AI 3.0 Specialization | Krish Naik Academy
Mentor: Mayank Aggarwal | Session: Day 11 (1 August 2026)

1. What is an Agent?
========================================
An agent is not just a chatbot.
It is a system where a language model can:
- understand the user,
- decide what to do,
- use tools if needed,
- and keep going until the task is complete.

In simple words:
Model + Tools + Loop = Agent

The agent loop usually works like this:
1. The user gives a request.
2. The model thinks about what is needed.
3. It may call a tool.
4. It may get more information.
5. It produces the final answer.

Important difference:
- A normal model answers questions.
- An agent can act.

The harness means everything around the loop:
- model
- prompts
- tools
- memory
- runtime state
- control flow

Key framing from class:
An agent is a model plus a harness. Around the model, you can add tools,
context, sub-agents, memory, skills, middleware -- anything that helps you
take the best advantage of the model.

Everything covered so far in the course (models, messages, structured output,
tools) was never separate from "agents" -- these are literally the components
an agent is built from. What has changed over the last 4-5 years is really
just the "artificial brain" (the LLM) -- everything else around it is the
same idea as before. The core question becomes: how do we best harness this
model?

========================================
2. LangChain, LangGraph, LangSmith, Deep Agents
========================================
LangChain:
- Main framework for building LLM-based applications and agents.
- Helps connect prompts, models, tools, memory, and structured output.

LangGraph:
- Used for stateful workflows and multi-step agent behavior.
- Good for graphs, checkpoints, and long-running flows.
- State, in much more depth, is covered here (upcoming classes).

LangSmith:
- Used for debugging, tracing, and monitoring.
- Helps inspect how an agent behaves.

Deep Agents:
- A more advanced type of agent system.
- Different in kind because it focuses on more autonomous, layered reasoning
  and actions.

Note: Interview questions shared for this class intentionally reflect
LangChain's latest version (v1.0+), not the older "Classic" version most
companies/tutorials still use -- the course stays on the newer version since
that's the direction the field is moving.

========================================
3. Why .env Files Matter
========================================
A .env file stores secret values such as API keys.
It is better than putting keys directly into the notebook code.

Why?
- Keeps secrets safe.
- Makes code cleaner.
- Easier to reuse across environments.

If you hardcode the API key directly into notebook cells:
- it is risky,
- it can be exposed accidentally,
- and it is harder to maintain.

Typical setup:
- load_dotenv()
- read OPENAI_API_KEY from the environment
- initialize the model only after the key is available

========================================
4. Plain Prompts vs Messages vs Message Lists
========================================
A plain prompt is just a single string.
Example:
- "Explain this concept"

A message-object list is more structured.
It allows the model to understand role-based messages like:
- system
- user
- assistant
- tool

A dictionary-based message list is useful when the data is represented as a
JSON-like structure.

Why this matters:
- Models can respond better when messages are clearly separated by role.
- Chat history and tool interactions become easier to manage.

========================================
5. AIMessage, AIMessageChunk, and Message Types
========================================
AIMessage contains more than just .content.
It can include:
- tool calls
- metadata
- finish reasons
- usage information

Streaming returns AIMessageChunk instead of plain text.
Why?
Because the chunks carry incremental structure and metadata, not just raw
text fragments.

This means streaming is not just "split text". It is structured information
arriving piece by piece.

========================================
6. Structured Output -- The Main Concept
========================================
Structured output means the model returns data in a specific format.
Instead of giving a free paragraph, it gives an object with known fields.

This is very useful in:
- booking systems
- extraction tasks
- forms
- APIs
- automation pipelines

Example idea:
If the user says "Book 2 tickets for Dune",
we want the model to return something like:
- customer_name
- movie_title
- action
- ticket_count

This is much easier for code to use than raw text.

========================================
7. Pydantic and BaseModel
========================================
Pydantic is used to define the expected shape of output.
BaseModel is the main class.

Example:
from pydantic import BaseModel, Field
from typing import Literal

class BookingRequest(BaseModel):
    customer_name: str
    movie_title: str
    action: Literal["book", "cancel"]
    ticket_count: int = Field(default=1)

Why this matters:
- The schema gives the model a strict form.
- The data can be validated automatically.
- The output becomes reliable for code.

Field is used to add descriptions and constraints.
Literal is used when a field must be one of a small list of values.

========================================
8. with_structured_output() at the Model Level
========================================
with_structured_output() is the raw model-level method.
It tells the model to return data in the desired schema.

Example:
structured_model = model.with_structured_output(BookingRequest)
result = structured_model.invoke("Extract a booking request from this message")

This works well when you just need a parsed object.

But it has a limitation:
- it is not designed to manage a full tool-using loop.
- it only returns the structured object.

That is why the agent-level version is more important in real agent systems.

========================================
9. Why Agent-Level Structured Output Is Better
========================================
When we build an agent, we want the system to:
- understand the request,
- maybe call tools,
- then return a structured answer.

That is why we use:
create_agent(..., response_format=...)

This allows the agent to work with tools and still produce structured output.

In other words:
- model-level structured output = good for parsing
- agent-level structured output = good for real agents

This is the most important practical lesson from the class.

========================================
10. ProviderStrategy vs ToolStrategy
========================================
There are two general ways to enforce structured output.

ProviderStrategy:
- Uses the provider's native structured-output support.
- Usually fast and clean.
- Works when the provider supports it.

ToolStrategy:
- Uses a synthetic tool-call style mechanism.
- More broadly compatible.
- Often used when the model/provider support is weaker.

In short:
- ProviderStrategy uses native support.
- ToolStrategy uses a compatibility layer.

========================================
11. Union Schemas for Multiple Intents
========================================
Sometimes one message can mean multiple things.
Example:
- "Book a reservation"
- "Cancel my booking"
- "Modify my trip"

In such cases, one single schema may not be enough.
We can define multiple schemas and use Union.

Example:
class NewBooking(BaseModel): ...
class CancelBooking(BaseModel): ...

Then the agent can choose which schema fits the request.

This is very useful in real systems because customers often use ambiguous
language.

========================================
12. Validation and Self-Correction
========================================
Structured output also gives us validation.
If a model gives an invalid value, the system can catch it.

Example:
If the field says the quantity must be between 1 and 10,
and the model says 15,
then the system can retry and correct the value.

This is powerful because the agent can self-correct without us manually
writing a lot of logic.

The agent loop is what makes this possible.

========================================
13. What is a Tool?
========================================
A tool is a function that the model can call to do something real.
Examples:
- check showtimes
- book seats
- search the web
- access a database
- read memory

The tool is usually defined with:
- @tool
- type hints
- a clear docstring

The docstring is very important because it acts like the tool's pitch to
the model. If the description is weak, the model may not know when to use
the tool.

========================================
14. How a Tool is Built
========================================
Example:
from langchain_core.tools import tool

@tool
def check_showtimes(movie_title: str) -> str:
    """Check available showtimes for a movie."""
    return "7:00 PM and 10:15 PM"

This tool can now be given to the model.

Important rule:
- bind_tools() makes tools visible to the model.
- It does not run them by itself.

The actual execution happens inside the agent loop.

========================================
15. args_schema -- More Structured Tool Inputs
========================================
Sometimes a tool needs more complex input.
Instead of relying only on simple type hints, we can define a Pydantic
schema.

Example:
class OrderInput(BaseModel):
    dish_name: str
    quantity: int
    delivery_or_pickup: Literal["delivery", "pickup"]

Then the tool uses this schema as its input definition.

This is helpful because it gives the model richer guidance and better
validation.

========================================
16. Reserved Tool Parameters
========================================
Two names are special and should not be used as tool parameters:
- config
- runtime

Why?
Because LangChain reserves them for its own internal behavior.
Using them accidentally can cause confusing errors.

This is one of the easiest mistakes to make in practice.

========================================
17. ToolRuntime and Hidden Context
========================================
ToolRuntime allows a tool to access information that the model does not
directly see.
This includes:
- runtime.state
- runtime.context
- runtime.store

The model only sees the declared tool inputs.
It does not see the hidden runtime information.

This is useful when a tool needs access to:
- the current conversation state,
- per-run context,
- or persistent memory.

========================================
18. Memory with runtime.store
========================================
A tool can save long-term information in runtime.store.
Example use cases:
- remember a customer's favorite genre,
- remember dietary preferences,
- remember trip preferences across sessions.

This makes the agent more personal and more useful over time.

Key idea:
- state is for this conversation,
- store is for longer-term memory.

========================================
19. return_direct=True
========================================
Sometimes the tool's output should be returned verbatim, without the model
rephrasing it.
This is useful when the output is a policy, rule, or exact message.

Example:
@tool(return_direct=True)
def get_exact_refund_policy() -> str:
    return "Tickets are refundable up to 2 hours before showtime."

This is useful when exact wording matters.

========================================
20. Dynamic Tool Gating
========================================
Some tools should be available only in certain situations.
For example:
- VIP-only tools
- premium-member tools
- tools allowed only at certain times

This is done using middleware such as wrap_model_call.
The tool can be hidden from the model entirely for some users.

This is stronger than just telling the model not to use the tool.
If the tool is removed from the visible toolset, the model cannot use it
at all.

========================================
21. Checkpointing and Short-Term Memory
========================================
Agents can also remember the conversation within a thread.
This is done with a checkpointer and a thread_id.

Example idea:
- first message: "My name is Mayank"
- later message: "Who am I?"

A stateful agent can answer based on the conversation history.

This is important because a stateless agent forgets everything after each
call.

========================================
22. Real-World Examples from the Notebook
========================================
The notebook uses a running example called CineBot.
The class shows how an assistant can:
- understand a booking request,
- structure it,
- call tools,
- and produce an answer.

The same pattern applies to restaurant assistants, trip planners, and
customer support agents.

========================================
23. Important Revision Points
========================================
Be ready to explain:
- what an agent is,
- how tools differ from plain prompts,
- why structured output matters,
- how agent-level structured output works with tools,
- how Pydantic schemas help enforce structure,
- why ToolRuntime and runtime.store are useful,
- and how dynamic gating improves safety and control.

========================================
24. The Agentic Loop, Restated
========================================
At the core of an agent is the Agentic Loop:
1. Receive a message.
2. Model decides: is a tool needed?
3. If yes -> execute tool.
4. Append the tool result to messages.
5. Go back to the model with the updated messages.
6. Repeat until no more tool calls are needed.
7. Return the final answer.

This used to be called the "ReAct pattern" -- "Agentic Loop" is the more
accurate/modern term.

Important confirmed detail:
A tool's result ALWAYS goes back to the model first, never straight to the
user. The user only ever sees the model's final response after it has
processed that tool result.

========================================
25. The Real Problem: Not Every Tool Belongs to Every User
========================================
CineBot scenario: a booking agent has a standard tool, a VIP lounge tool,
and an admin tool. A regular, non-paying user asks for a VIP seat.

Two tempting (but wrong) fixes:
1. Ask the user if they're a VIP -- pointless, since a user will always
   just say yes.
2. Permanently remove the VIP tool -- breaks things for actual VIP users.

The Menu Analogy:
Think of it like a menu that reprints itself before you sit down. A VIP
member sees the full menu; a regular guest sees a shorter menu -- not
because they were told "don't order the VIP item," but because those items
simply aren't printed on their menu at all.

Real-world proof -- ChatGPT connectors:
- Each connector (Gmail, Slack, etc.) is really just a collection of tools
  (e.g. Gmail has write/delete tools, Slack has ~11 tools).
- On a free-tier account, ChatGPT still loads/pays the token cost for tools
  a user can never use -- a real, ongoing cost companies lose money on.
- Live example of a bad tool call: asking "who won the FIFA World Cup"
  triggered an unnecessary web search that returned the wrong year's result.

========================================
26. Dynamic Tool Loading
========================================
With dynamic tool loading, the set of tools available to the agent is
modified AT RUNTIME, rather than being fixed upfront.

Two approaches, depending on whether tools are known ahead of time:
- Filtering pre-registered tools: register every possible tool at
  agent-creation time, then dynamically filter which are exposed based on
  state, permissions, and context.
- Registering tools dynamically: for cases where the full toolset isn't
  known upfront (e.g. tools arriving via MCP).

Why not just use plain Python if/else to hand the agent one of two
pre-built tool lists?
- Plain Python code outside the agent CANNOT read the agent's live state
  (e.g. it can't see the store, or that a message count increased). That
  visibility only exists inside the agent's execution -- which is exactly
  what middleware provides.

========================================
27. Middleware: Cutting Into the Loop
========================================
Middleware lets you "cut into" the agent loop at specific points:
- before calling the model
- after calling the model
- before calling the tool
- after calling the tool
- after observing the result

This is a universal concept across frameworks (parallels exist in Java's
Spring ecosystem too) -- not a LangChain-only idea.

Live code -- State-based filtering:

def only_public_tools_if_unauthenticated(request):
    if not request.state.get("authenticated"):
        request.tools = [t for t in request.tools if t.name.startswith("public_")]
    return request

Idea: read from state whether the user is authenticated; if not, only
expose tools whose name starts with "public_".

Live code -- Store/context-based filtering:
A second example used request.runtime.context instead of state -- checking
a user ID and feature flags to decide which tools to load.
Key production point: if you have 1,000 tools registered "publicly," they
should NOT all load for every authenticated user -- that itself is a sign
of poor tool design.

The VIP Booking Demo (including a live bug):

def vip_gate_middleware(request):
    is_vip = request.state.get("is_vip_member", False)
    if not is_vip:
        request.tools = [t for t in request.tools if t.name != "vip_lounge_booking"]
    return request

Result with a regular user: the agent genuinely has no idea the VIP tool
exists (it's not in its tool list at all) -- stronger than just telling the
model "don't use it."

Live bug: passing is_vip_member=True directly into invoke() did NOT work --
the middleware kept reading it as False.

The fix: define a CUSTOM STATE SCHEMA that explicitly tells the agent to
track is_vip_member alongside its built-in fields (like the running message
list). Once that schema was added, the middleware correctly read the flag
and exposed the VIP tool.

Big-picture takeaway: based on the user, AT RUNTIME (not just at agent
creation), you can change which tools the agent has access to.

========================================
28. Headless Tools
========================================
Some actions can only happen on the USER's device, not on the server:
- accessing the clipboard
- getting device location
- completing a payment

Three categories of tools:
- Server-side tools: run on the AI provider's own servers (e.g. web search,
  code interpreter).
- Regular tools: your own functions, run wherever your agent runs.
- Headless tools: run on the USER's device (clipboard, location, payment).

How headless tools work:
Tool definitions (name, description, argument schema) are registered on the
server with your agent, but the IMPLEMENTATION is registered only on the
client, and executed after a short interrupt-or-resume handshake.

This isn't an AI-specific idea -- it parallels everyday browser APIs
(geolocation, clipboard, IndexedDB). The agent just needs to trigger these
client-side capabilities when appropriate.
Example: if Amazon needs your location, it runs in your browser and sends
the location back to Amazon -- Amazon's US server has no way to get it
directly.

========================================
29. Real Tools: The TripMate Project
========================================
A second, fuller project introduced alongside CineBot (which is kept purely
for explaining concepts): TripMate, a travel-planning agent, built with
REAL tools instead of mocked/hard-coded ones.

Real Weather Tool:
- Built live using Open-Meteo -- a free, open-source, keyless weather API.

Real Search Tool:
- Uses Tavily for genuine travel research.
- Reminder: Tavily is a third-party service, not a LangChain method --
  LangChain just makes it easier to integrate because it's used so often.

Real Persistent Database:
- SQLite used live to set up a `trips` table, with tools to save and
  retrieve a trip by user ID.
- The DB choice itself doesn't matter (could be ChromaDB, Postgres, NoSQL,
  Mongo, etc.) -- SQLite is just an easy local mock-up.
- Confirmed: if the application restarts, the data does NOT disconnect,
  because it's stored outside the app, in the SQL DB.

Result: four real tools -- save trip, get saved trip, web search, real
weather -- giving TripMate a genuinely working toolset, not placeholders.

========================================
30. The Forgetting Problem
========================================
Demo: tell CineBot "my name is Mayank," then in the NEXT message ask "who
am I?" -- the agent does not remember, by default.

This connects back to an earlier course lesson: an agent should be able to
remember us, but by default, it does not.

The Fix -- Checkpointing:

from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent_with_memory = create_agent(
    model=model,
    tools=[...],
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "mayank-session-1"}}
agent_with_memory.invoke({"messages": [...]}, config=config)

This is the official, documented way an agent remembers you (not a custom
approach).

thread_id explained:
- Just a unique ID so the checkpointer can locate a particular chat.
- The USER does not enter this -- the application controls it.
- New session -> new/different thread_id.

InMemorySaver:
- Keeps everything in RAM only as long as the process runs.
- A persistent option (e.g. Postgres) follows the exact same pattern for
  anything that needs to survive a restart.

========================================
31. Memory Saver vs Memory Store vs Caching vs Database
========================================
No single "right" answer -- it depends on the use case as a developer.
Example: Swiggy/Amazon customer chatbots close a chat if you don't reply in
~10 minutes -- there's no benefit to keeping that chat in memory forever.

Comparison:

| Concept        | What it's for                                                        | Typical lifetime                              |
|----------------|-----------------------------------------------------------------------|------------------------------------------------|
| Memory saver   | Saving ONE conversation's history so an agent can resume it, tied to  | As long as that thread needs -- minutes to     |
| (checkpointer) | a thread_id.                                                           | persistent, depending on backend.              |
| Memory store   | Saving information ABOUT A USER -- preferences, facts -- usable       | Persistent by design.                          |
|                | across many separate conversations.                                   |                                                 |
| Caching        | Avoiding repeated expensive calls for near-identical requests.        | Short and tunable -- an hour, a day, etc.      |
| Database       | General persistent storage for anything the app needs to keep.        | Persistent, application-defined.               |

Rule of thumb examples:
- "I like Python as a language" -> belongs in the memory STORE (usable
  across different chats = long-term memory), not just a memory saver.
- "What's the weather in Delhi" asked a million times an hour -> CACHE the
  result rather than hitting the API every time (API calls at scale are
  not cheap).

========================================
32. What's Next
========================================
- LangGraph: state, checkpointing in full depth (worth spending
  1-1.5 months understanding properly -- once understood deeply, every
  other framework becomes much simpler).
- Memory, RAG, and MCP: upcoming modules.

========================================
33. Live Q&A Highlights
========================================
Q: Why can't a plain Python if/else decide which tools to send instead of
   middleware?
A: Plain code outside the agent can't read the agent's own live state --
   that visibility only exists inside the agent's execution, which is
   exactly what middleware provides.

Q: Is thread_id a reserved keyword?
A: No -- it's just the identifier the checkpointer looks for in the config.
   The application controls how IDs are generated and assigned.

Q: Can I inspect what's actually stored in memory for a thread?
A: Yes, via the checkpointer's API -- but the full mechanics of
   state-as-checkpoints belong to LangGraph, covered there in depth.

Q: Does InMemorySaver have a time limit?
A: No -- it lasts exactly as long as the Python process runs. A persistent
   store (e.g. Postgres) removes that limit entirely.

Q: What happens if a tool fails or times out?
A: Recoverable failures are typically retried as part of the harness; a
   fatal error (e.g. no internet) causes the agent to fail outright --
   exactly why defining that harness matters.

Q: Can an agent discover brand-new tools at runtime, not just from a fixed
   list?
A: Yes -- this is where MCP and middleware intersect; tools arriving
   dynamically can still be registered and made available mid-run.

Q: Does running a tool cost money the same way a model call does?
A: No -- only model calls consume tokens and cost money. A tool running on
   its own, with no model call involved, doesn't.

Q: Will this course cover training or building a model from scratch?
A: No -- the focus is entirely on using and harnessing existing models,
   not training them.

Q: Is Agentic AI 2.0's content still relevant, given it used an older
   LangChain version?
A: The concepts carry over, but the code reflects LangChain Classic; this
   course deliberately stays on the latest version, since that's where the
   industry is shifting.

Q: How do I decide between memory store, memory saver, caching, and a
   database?
A: No universal answer -- short-lived conversational context -> memory
   saver; cross-session preferences -> memory store; repeated identical
   expensive calls -> caching; everything else persistent -> a database.

========================================
34. Action Items After Class 11
========================================
- Recreate the VIP booking middleware example, and deliberately trigger the
  "state field not tracked" bug before fixing it with a custom state
  schema.
- Write a piece of middleware from scratch that filters tools based on
  request.state.
- Build one genuinely real tool (a free public API, no key required)
  instead of a hard-coded placeholder.
- Set up InMemorySaver with a thread_id, confirm an agent remembers a name
  across two invoke() calls, then swap the thread_id and confirm it forgets
  again.
- Walk through the TripMate build yourself: real weather, real search, real
  SQLite persistence.
- Revise memory saver vs. memory store vs. caching vs. database until the
  distinctions are automatic.
- Come back ready for deeper state, checkpointing, and LangGraph coverage
  in upcoming classes.

"""