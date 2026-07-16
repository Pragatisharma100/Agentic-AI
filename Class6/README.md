## Core Concepts

### Tools
**Tools** → API calls and external functions the agent can invoke.

---

## The Building Blocks

### 1. AI Model: A Brilliant Guesser with No Memory and No Hands

An AI model predicts the next best words to say, given everything said so far. There is no separate understanding mechanism — the feeling of being understood comes entirely from being extremely good at this one narrow job.

- **Ask it something it has memorized**: Answers beautifully
- **Ask it to check current state** (weather, exchange rates): Can only guess, confidently

**Analogy**: A brilliant person in a windowless room with extraordinary reading knowledge. They answer perfectly about what they've read, but can only guess about what's happening outside right now.


---

### 2. Chatbot: The Same Guesser, Now Handed a Transcript

A chatbot is the same model with one addition: a written record of the conversation re-shown in full on every turn. It isn't truly remembering — just reading the entire transcript fresh each time.

- Stops forgetting what you said messages ago
- Still cannot check anything real in the world
- Memory and access are two different problems

**Analogy**: Same person, same windowless room — except now someone hands them the entire written conversation before each answer. Better memory, same guesswork.

---

### 3. Agent: The Same Guesser, Now Handed a Phone

An agent is that same model, handed something genuinely new: the ability to call a real tool, get a real answer, and use it. The critical part is that **the model decides, on its own, when a question needs one**.

The word **"decides"** is what separates an agent from everything before it. A chatbot with a weather function is only an agent if the model decides to call it, not a human.

**Analogy**: Now someone hands the person a real phone. They don't guess about weather — they call someone who knows and relay the real answer back.



---

## Technical Implementation

### 4. Calling a Real Model: Turning the Idea into One Real Function Call

Underneath every chat interface sits one plain function call: send text in, servers do the prediction, text comes back. Everything elaborate — memory, tools, judgment — gets built as a layer wrapped around this basic call.

**Analogy**: The phone gets plugged into a working line for the first time. Before this, it was just a prop. Now dialing actually connects to someone.

---

### 5. Paid vs. Free Providers: Different Phone Companies, Identical Phone Call

Several companies offer model access — some free, some paid — and the shape of the call is mostly identical. Swapping providers is closer to changing a phone number than rewriting the call.

**Analogy**: Different phone companies, same phone call. Premium or free — you dial the same handset, ask the same question, only the billing company differs.

---

### 6. Failing Loudly: A Clear Error Beats a Confident Guess

When there's no working provider, **fail immediately and clearly** with the exact problem. A confidently wrong answer is far more dangerous than an obvious failure — nobody fixes what they don't notice needs fixing.

**Analogy**: "This isn't connected" is better than making up a fake conversation. One is an honest dead end, the other is a lie that costs you later.


---

### 7. Structured Output: Asking for a Form Instead of a Paragraph

Models naturally reply in sentences — "Tokyo" or buried in "sure, let me check on Tokyo for you!" Structured output asks the model to reply in a fixed JSON shape with exact field names, so code can read it reliably.

This habit lets a model's reply feed directly into real functions without human rework.

**Analogy**: Hand them a form to fill out instead of asking for a paragraph. Forms are something the next step can actually use.

---

### 8. Validation: The Bouncer That Checks the Form at the Door

Asking for a specific shape doesn't guarantee it arrives that way. Validation is a strict check applied instantly: does the reply match the promised shape? Reject immediately with a precise reason if not.

This turns "the model probably replied correctly" into "nothing proceeds unless provably correct."

**Analogy**: A bouncer holding the form spec, checking every single form. Empty boxes or wrong types get turned away immediately — not three rooms further in.

---

## Tools & Decisions

### 9. What Is a Tool: Just a Function, Nothing More Mysterious

A tool is an ordinary function — check weather, do arithmetic, look up exchange rates. It has no AI awareness; it just takes input and returns a result. The word "tool" sounds complicated but almost never is. **What makes it interesting is who decides to call it and when.**

**Analogy**: One specific number in the phone — a direct line to a weather service. Nothing complicated, just one single-purpose contact.

---

### 10. Manual Tool Calling: We Dial the Number for It, Still

It's entirely possible to give the model access to a tool while you decide to call it — reading the reply yourself, pulling what you need, and calling by hand. This works, but **the model still isn't deciding anything. We are.**

This stage matters because the next concept changes exactly one thing — and that one change is the entire idea of an agent.

**Analogy**: The weather hotline is saved. But we still pick up the receiver, dial it ourselves, and relay the answer. The person has a phone but isn't using it.

---

### 11. The Tool Schema: A Menu, Not the Kitchen

A tool schema is a plain-language description — name, purpose, required information — in a format the model can read. **The model never sees actual function code, only this description.** The wording carries all the weight.

A precise description ("use this whenever someone asks about current weather in a specific place") lets the model recognize correctly when this tool is right.

**Analogy**: A small card taped next to the phone listing every number they can call and when each is useful. Describes each number, doesn't explain how the phone company routes it.

---

### 12. The Model Chooses: The Instant It Stops Being Us

Hand the model a question and the tool card together in the same call, and something changes: instead of plain text, it responds with exactly which tool it wants and what arguments — **before any code runs**. The model has simply made a decision.

**This is the precise moment a system stops being "a chatbot with a function attached" and becomes an agent.**

**Analogy**: The person reads the card themselves and tells you which number to dial and why — without your suggestion. They decided on their own reading of the card.

---

## Agent Architecture

### 13. The Agent Loop: Decide, Act, Observe, Repeat

Real questions often need several decisions in a row: check one thing, look at the result, decide if more is needed, possibly check something else, then answer. The agent loop is exactly that repeating cycle: reason → act → observe → repeat.

This loop separates a genuine agent from fixed, hand-coded sequences. Fixed sequences always run the same steps in the same order. A loop decides steps fresh every time based on the actual question.

**Analogy**: The person might make multiple calls before answering — check weather, work out a conversion, then respond. Each time they hang up, they decide if one more call is needed.

---

### 14. Memory: Nothing More Mysterious Than a Growing List

Memory is nothing exotic — just a running list: every message, every tool result, appended in order, and the entire list re-sent on every call. The model reads the whole list fresh each time and answers based on everything.

This is exactly what lets the agent loop work — each decision sees everything gathered earlier in the conversation.

**Analogy**: One notepad on the desk. Every question, phone call, answer — written on the same notepad in order. The whole notepad gets glanced at again before every decision.

---

### 15. The Complete Agent: Every Piece in One Place, No Framework

Put every piece together and the full picture appears:
- A model reachable reliably
- Asked to reply in a trustworthy shape
- Handed a card describing available tools
- Left to run its own loop — deciding, acting, observing

Every part was built from plain code, one concept at a time. **None of it required a specialized framework.** A framework is simply a way of writing this loop with less repetition.

**Analogy**: The room now has everything: a working phone, a card listing useful numbers, a growing notepad, and someone genuinely capable of deciding when to reach for any of it.

---




---

### 16. Why No Framework First: Knowing What's Inside the Box Before You Buy One

Frameworks that build agents are genuinely useful — they save repetition once the underlying idea is understood. The risk is building something that works while understanding almost none of why, which becomes a real problem when it breaks.

Building the loop by hand once means every later framework reads as a shortcut for something already understood, not an unexplained black box.

**Analogy**: You could hire a company to furnish the room completely. Nothing wrong with that, later. But furnish it yourself once first — so when something eventually breaks, you recognize what failed instead of staring at a room you've never truly seen inside.

---

## Frameworks

### 17. LangChain: Agent = Model + Harness

**LangChain vs. LangGraph vs. Deep Agents:**

- **Deep Agents**: "Batteries-included" agent with automatic context compression, virtual filesystem, subagent-spawning. Built on LangChain agents.
- **LangChain** (`create_agent`): Highly customizable harness, easily tailored to your use case and data.
- **LangGraph**: Low-level orchestration framework for advanced needs combining deterministic and agentic workflows.
- **LangSmith**: Trace, debug, and evaluate agents built with any framework. Set up LangSmith Engine to monitor traces, detect issues, and propose fixes.