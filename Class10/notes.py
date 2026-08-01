"""Class 10 Notes - LangChain, Tools, Structured Output, and Agents

Files in this folder:
- Langchain_Continue.ipynb
- Langchain 1.pdf
- Langchain-2.pdf
- notes.py

This class focuses on moving from simple LLM calls to agent-like systems that can:
- produce structured output,
- call tools,
- use memory/state,
- and make decisions with clear schemas.

========================================
1. Class Overview
========================================
The main idea of this class is: build an AI assistant that does more than chat.
It should understand user intent, extract structured information, and act using tools.

Core flow:
1. Understand the user message.
2. Convert it into a structured request.
3. Decide whether a tool is needed.
4. Call the tool if required.
5. Return a clean answer.

========================================
2. Setup and Environment
========================================
We typically begin by loading the API key and installing the required libraries.

Example:
```python
import os
from dotenv import load_dotenv
load_dotenv()
```

Useful packages used in this class:
- langchain
- langchain-openai
- langchain-community
- langgraph
- python-dotenv
- langchain-mcp-adapters
- langchain-chroma
- chromadb
- pypdf

Example installation:
```python
!pip install langchain langchain-openai langchain-community langgraph python-dotenv langchain-mcp-adapters langchain-chroma chromadb pypdf
```

========================================
3. Structured Output with Pydantic
========================================
Structured output means the model returns data in a known format instead of free text.
This is very useful for booking systems, forms, extraction, and APIs.

Why it is important:
- It gives consistent results.
- It is easier to validate.
- It allows downstream code to work with objects.

Example schema:
```python
from pydantic import BaseModel, Field
from typing import Literal

class BookingRequest(BaseModel):
    customer_name: str = Field(description="The customer's name")
    movie_title: str = Field(description="The movie they want to see")
    action: Literal["book", "cancel"] = Field(description="Whether this is a new booking or a cancellation")
    ticket_count: int = Field(description="How many tickets, default 1 if not mentioned", default=1)
```

Using it with a model:
```python
structured_model = model.with_structured_output(BookingRequest)
result = structured_model.invoke("Extract a booking request from: I want 2 tickets for Dune")
```

Key takeaway:
Structured output makes the model behave like a parser and formatter.

========================================
4. Provider Strategy vs Tool Strategy
========================================
There are two common ways to get structured output.

A. ProviderStrategy
- Uses the model provider's native structured-output support.
- Usually fast and clean.
- Works only where provider supports it.

B. ToolStrategy
- Uses a synthetic tool call to force structured response.
- Works more broadly.
- Slightly slower but more compatible.

Example:
```python
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
```

This is important because in real projects, you may need compatibility across models.

========================================
5. Agents and Tool Calling
========================================
An agent combines:
- a language model,
- tools,
- and sometimes memory/state.

The agent can decide when to use a tool.

Example tool:
```python
from langchain_core.tools import tool

@tool
def peek_showtimes(movie_title: str) -> str:
    """Check showtimes for a movie."""
    return "7:00 PM and 10:15 PM"
```

When you bind tools to a model:
```python
incomplete_model = model.bind_tools([peek_showtimes]).with_structured_output(BookingRequest)
```

Then you can create an actual agent:
```python
from langchain.agents import create_agent

booking_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=[peek_showtimes],
    response_format=BookingRequest,
)
```

This is the basic blueprint for a real assistant.

========================================
6. What Makes a Tool?
========================================
A tool is basically a function with:
- clear input parameters,
- a clear description,
- and a return value.

Important rules:
- Use type hints.
- Write a good docstring.
- Make the tool purpose obvious.
- Avoid using runtime/config as tool parameters unless you really know why.

Example:
```python
@tool
def check_showtimes(movie_title: str) -> str:
    """Check available showtimes for a movie at the cinema."""
    return "Show is available"
```

A tool is not just a prompt trick; it is an action interface.

========================================
7. Multi-Format Structured Output
========================================
Sometimes the model needs to choose between different response forms.
For example: book vs cancel.

We can define multiple Pydantic models and use Union.

Example:
```python
from typing import Union

class NewBooking(BaseModel):
    customer_name: str
    movie_title: str
    ticket_count: int

class CancelBooking(BaseModel):
    customer_name: str
    movie_title: str

union_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=[],
    response_format=ToolStrategy(Union[NewBooking, CancelBooking]),
)
```

This helps when a request could match multiple intents.

========================================
8. Validation and Error Handling
========================================
Structured output can also help constrain the model.
You can enforce rules with field constraints.

Example:
```python
from pydantic import BaseModel, Field

class SeatBooking(BaseModel):
    customer_name: str
    ticket_count: int = Field(description="Number of tickets, must be between 1 and 10", ge=1, le=10)
```

This means if the model tries to return an invalid value, the system can reject or correct it.

The notebook also demonstrates that invalid requests can be handled with custom error behavior.

========================================
9. Runtime in Tools
========================================
A tool can access runtime information such as:
- execution info,
- messages/history,
- store,
- and other context.

This is very useful in real applications.

Example concept:
```python
from langchain.tools import ToolRuntime

@tool
def get_last_movie_mentioned(movie: str, runtime: ToolRuntime) -> str:
    """Get the last movie mentioned in the chat history."""
    pass
```

This allows tools to access the broader agent runtime rather than just simple inputs.

========================================
10. Memory and Persistent State
========================================
Agents can remember user preferences using a memory store.

Example idea:
- save a customer's favorite genre,
- recall it later,
- personalize future responses.

Example:
```python
from langgraph.store.memory import InMemoryStore

loyalty_store = InMemoryStore()
```

Then tools can use the store to save and recall data:
```python
@tool
def save_favourite_genres(customer_id: str, genre: str, runtime: ToolRuntime) -> str:
    runtime.store.put((customer_id, "preferences"), "favourite_genre", {"value": genre})
    return f"Got it -- I will remember you like {genre} movies"
```

This shows how an agent moves from being stateless to stateful.

========================================
11. Return Direct
========================================
Some tools can bypass the model's final polishing and return an exact output directly.

Example:
```python
@tool(return_direct=True)
def get_exact_refund_policy() -> str:
    return "Tickets are refundable up to 2 hours before showtime. No refunds after that."
```

This is helpful when you want the tool output to be used verbatim.

========================================
12. Dynamic Tool Loading
========================================
In advanced systems, tools can be loaded dynamically based on the situation.
This means the agent does not always use the same tool set.

The idea is:
- check the user request,
- decide which tools are relevant,
- gate the tool selection.

Example concept:
```python
@tool
def standard_booking(movie_title: str) -> str:
    return f"Standard seat booked for {movie_title}."

@tool
def vip_lounge_booking(movie_title: str) -> str:
    return f"VIP lounge seat booked for {movie_title}."
```

This is the foundation of role-based or permission-based tool access.

========================================
13. Important Takeaways
========================================
- LLMs are much more powerful when they can use structured output.
- Tools turn the model into an action-taking assistant.
- Agents combine reasoning + tools + memory.
- Pydantic is the bridge between natural language and reliable data.
- In production, agents should be designed with clear schemas and controlled tool behavior.

========================================
14. Short Summary for Revision
========================================
Class 10 teaches the transition from:
- a simple chatbot

to
- a structured, tool-enabled agent.

The main building blocks are:
1. model + schema
2. tool definitions
3. agent creation
4. structured response handling
5. memory/runtime/context
6. controlled tool usage

========================================
15. Practical Example Flow
========================================
A booking assistant might follow this flow:
1. User says: "Book 2 tickets for Interstellar."
2. Model extracts booking info into a BookingRequest object.
3. Agent chooses a booking tool.
4. Tool reserves the seats.
5. Agent returns a final answer.

This is the same pattern used in many real-world AI applications.
"""
