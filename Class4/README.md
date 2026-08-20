# Project Zero

| File | Contents |
|---|---|
| `_01_ai_model_vs_chatbot_vs_agent.py` | Structural comparison of the three, no API calls |
| `_02_calling_the_ai_paid_and_free.py` | Real API calls: OpenAI, Anthropic, Groq, OpenRouter |
| `_03_structuring_with_pydantic.py` | Structured JSON extraction, validated with Pydantic |
| `_04_giving_it_a_tool.py` | A weather tool, called manually |
| `_05_teaching_it_to_choose.py` | Tool schema + the model choosing and calling the tool itself |
| `_06_project_zero_agent.py` | The full loop, terminal chat, one tool |
| `_07_streamlit_app.py` | The full loop with a Streamlit front end, three tools (weather, calculator, currency) |

Each file is independent and can be run on its own. All files require a real API key --
there is no offline stand-in.

## Setup

```bash
uv sync
cp .env.example .env
# fill in at least one key -- GROQ_API_KEY is free and fastest to get
```

## Run

```bash
uv run _01_ai_model_vs_chatbot_vs_agent.py
uv run streamlit run _07_streamlit_app.py
```



## Key Concepts

### Provider Notes
- **Groq** is stateless — the system message is generated every time because it cannot recall previous interactions. Every time it sends the system message.

### Knowledge Cutoff
The AI has a knowledge cutoff date, indicating the date up to which the AI was trained.

### Core Components of an Agent
An agent consists of 3 main components:
1. **Memory** — Stores conversation history
2. **AI Model** — Generates responses
3. **Tools** — External functions the AI can invoke

### Pydantic & Structured Responses
Pydantic helps with a structured approach to getting answers from the AI in a validated format.

### AI Decision Making
- **Normal Responses**: For straightforward questions, the AI provides a direct reply.
- **Tool Usage**: When a question requires a tool the AI has access to, it can decide to call that tool with the appropriate parameters.
- **Schema-Based Approach**: Passing a schema is better than passing individual parameters.

### Component Definitions

**Agent** — Wraps `ai_model()` with history AND a set of tools it can choose to use. The `decide_tool()` function here uses simple keyword matching, which is only good enough to illustrate the concept. In reality (as shown in File 5), a real model makes that choice based on meaning, not string matching.

**Chatbot** — Wraps `ai_model()` with conversation history. Each call to `ask()` appends both the question and answer to `self.history`, so the next call can see everything said before. It has no ability to check the real world—only to talk with better memory of the chat.

**AI Model** — A single one-shot prediction. Takes a question, returns an answer, and remembers nothing about previous or future calls. This is the base capability of a raw model with no wrapping.

    