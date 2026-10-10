# Multi-Agent Patterns in LangChain v1 -- CineBot Edition (VS Code + uv)

One notebook, all five official LangChain v1 multi-agent patterns, every cell genuinely executed:

- **`LangChain_MultiAgent_Patterns_VSCode.ipynb`** -- Subagents, Handoffs (both approaches),
  Skills, Router, and Custom Workflow. 54 cells: diagrams, comparison tables, copyable
  takeaways for your second screen, and real, runnable code for every pattern -- not
  markdown-fenced snippets.

## One-time setup

1. Install `uv` if you don't already have it:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
   # or: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
   ```

2. In the Python environment used by VS Code, install the Groq chat-model integration:

   ```bash
   python -m pip install langchain-groq
   ```

   Keep the existing LangChain, LangGraph, and Jupyter dependencies installed in that environment.

3. Copy `.env.example` to `.env` and fill in your key:

   ```bash
   cp .env.example .env
   # then edit .env: set GROQ_API_KEY=your-groq-api-key
   ```

   The key is **optional**. Every pattern in the notebook runs for real without it (see below)
   -- it's only needed for the "production wiring" cells that call a live `openai/gpt-oss-120b`, and
   those are all wrapped in `try/except` so the notebook still completes cleanly without a key.

4. Open this folder in VS Code, open the notebook, and when VS Code asks which kernel to use,
   pick the one at `.venv/bin/python` (VS Code's Jupyter extension detects `uv`-created
   virtualenvs automatically; if it doesn't show up, run **"Python: Select Interpreter"** from
   the command palette and point it at `.venv/bin/python`, then
   **"Notebook: Select Notebook Kernel"**).

5. Run All.

## How this notebook runs every pattern for real without an API key

The honest problem with teaching multi-agent orchestration is that the interesting part --
the graph wiring, the state transitions, the tool dispatch, the handoff mechanics -- has
nothing to do with what a real LLM decides to say. But a notebook that only *describes* the
wiring in markdown doesn't prove it works, and a notebook that needs a live key to run at all
is a bad fit for a classroom where not everyone has one handy.

This notebook uses a small test double, **`ScriptedToolModel`**, defined once near the top and
reused throughout:

```python
class ScriptedToolModel(FakeMessagesListChatModel):
    """Plays back a scripted list of AIMessages, in order, on each call.
    Overriding bind_tools() to return self is what makes FakeMessagesListChatModel
    usable with create_agent -- the base class raises NotImplementedError otherwise."""
    def bind_tools(self, tools, **kwargs):
        return self
```

Give it a list of `AIMessage`s -- some plain, some with `tool_calls` -- and it feeds them to
`create_agent` one at a time, in order, as if a real model produced them. Everything
downstream is **completely real**: `create_agent` really runs its loop, tools really execute,
`Command` objects really update real graph state, `StateGraph.invoke()` really traverses real
nodes, and `InMemorySaver` really persists real checkpoints across turns. The only thing that
isn't live is which words the model chooses -- the graph mechanics around that choice are
exercised exactly as they would be in production.

The same idea shows up once more in the Custom Workflow / RAG section:
**`DeterministicFakeEmbedding`** (from `langchain_core.embeddings`) stands in for
`OpenAIEmbeddings` so the vector store can be built and queried with zero network calls. The
embedding *values* are deterministic stand-ins, but `InMemoryVectorStore` still does real
vector math and real nearest-neighbor search over them -- so the retrieval step is genuinely
verified, not mocked away. Swapping back to `OpenAIEmbeddings()` in production is a one-line
change.

Every "production wiring" cell (`model="groq:openai/gpt-oss-120b"`) is left in alongside the scripted
version, wrapped in `try/except`, so the moment you add your own `GROQ_API_KEY` those cells
start calling a real model live -- nothing else about the notebook changes.

## A real bug this notebook found (and fixed) along the way

While verifying the Router pattern's parallel fan-out (`Send`-based dispatch to multiple
agents at once), the notebook hit a genuine LangGraph error:

```
InvalidUpdateError: At key 'sub_answers': Can receive only one value per step.
Use an Annotated key to handle multiple values.
```

The cause: `sub_answers: list[str]` had no reducer, so when two `Send`-dispatched nodes both
wrote to it in the same step, LangGraph couldn't merge the two writes. The fix -- the same
pattern LangGraph's own `messages` key uses internally:

```python
import operator
from typing import Annotated

class RouterState(TypedDict, total=False):
    sub_answers: Annotated[list[str], operator.add]
```

This is called out as a 🐛 note directly in the notebook's Router section, right where it
happened -- it's a real, teachable gotcha for anyone building parallel fan-out graphs, caught
precisely because the whole notebook was run end-to-end rather than each cell checked in
isolation.

## Re-running the verification yourself

```bash
uv run jupyter nbconvert --to notebook --execute --allow-errors \
    --output executed_check.ipynb LangChain_MultiAgent_Patterns_VSCode.ipynb
```

Then check `executed_check.ipynb` for any cell with `"output_type": "error"` -- there should be
none. Every pattern's core mechanics run with zero error cells and no API key; only the
optional "production wiring" cells change behavior once you add `GROQ_API_KEY` to `.env`
(from a graceful printed fallback to a real live call).
