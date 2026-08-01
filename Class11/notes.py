"""Class 11 Notes — Detailed Handwritten-Style Version

Source files:
- Assignment_LangChain_Fundamentals_Landscape_to_Tools.ipynb
- Student_Reference_Structured_Output_and_Tools.ipynb

This note is written in a more detailed, revision-friendly style so it feels close to
classroom handwritten notes.

========================================
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

========================================
2. LangChain, LangGraph, LangSmith, Deep Agents
========================================
LangChain:
- Main framework for building LLM-based applications and agents.
- Helps connect prompts, models, tools, memory, and structured output.

LangGraph:
- Used for stateful workflows and multi-step agent behavior.
- Good for graphs, checkpoints, and long-running flows.

LangSmith:
- Used for debugging, tracing, and monitoring.
- Helps inspect how an agent behaves.

Deep Agents:
- A more advanced type of agent system.
- Different in kind because it focuses on more autonomous, layered reasoning and actions.

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

A dictionary-based message list is useful when the data is represented as a JSON-like structure.

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
Because the chunks carry incremental structure and metadata, not just raw text fragments.

This means streaming is not just "split text". It is structured information arriving piece by piece.

========================================
6. Structured Output — The Main Concept
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

This is very useful in real systems because customers often use ambiguous language.

========================================
12. Validation and Self-Correction
========================================
Structured output also gives us validation.
If a model gives an invalid value, the system can catch it.

Example:
If the field says the quantity must be between 1 and 10,
and the model says 15,
then the system can retry and correct the value.

This is powerful because the agent can self-correct without us manually writing a lot of logic.

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

The docstring is very important because it acts like the tool's pitch to the model.
If the description is weak, the model may not know when to use the tool.

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
15. args_schema — More Structured Tool Inputs
========================================
Sometimes a tool needs more complex input.
Instead of relying only on simple type hints, we can define a Pydantic schema.

Example:
class OrderInput(BaseModel):
    dish_name: str
    quantity: int
    delivery_or_pickup: Literal["delivery", "pickup"]

Then the tool uses this schema as its input definition.

This is helpful because it gives the model richer guidance and better validation.

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
ToolRuntime allows a tool to access information that the model does not directly see.
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
Sometimes the tool's output should be returned verbatim, without the model rephrasing it.
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
If the tool is removed from the visible toolset, the model cannot use it at all.

========================================
21. Checkpointing and Short-Term Memory
========================================
Agents can also remember the conversation within a thread.
This is done with a checkpointer and a thread_id.

Example idea:
- first message: "My name is Mayank"
- later message: "Who am I?"

A stateful agent can answer based on the conversation history.

This is important because a stateless agent forgets everything after each call.

========================================
22. Real-World Examples from the Notebook
========================================
The notebook uses a running example called CineBot.
The class shows how an assistant can:
- understand a booking request,
- structure it,
- call tools,
- and produce an answer.

The same pattern applies to restaurant assistants, trip planners, and customer support agents.

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
24. Final One-Line Summary
========================================
Class 11 teaches that the real power of AI agents comes from combining
structured output, tools, memory, and control flow into one working system.
"""
