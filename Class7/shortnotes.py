"""Class8 short notes on models, memory, streaming, batching, and tool interactions.

Groq
-----
- Groq is an OpenRouter model designed for high-performance routing capabilities.
- It is optimized for low latency and high throughput.
- Suitable for applications that require fast and efficient data processing.
- Groq's architecture handles complex routing tasks with minimal overhead.

Parameters
----------
- model
- api_key (optional)
- temperature (controls randomness)
- max_tokens
- timeout
- max_retries

Short-term memory
-----------------
- system message
- AI message
- human message
- tool message

Streaming
---------
- Streaming delivers partial results as they arrive.
- Defines chunks and a full message.
- No installation is required when using streaming in supported SDKs.

Batching
--------
- Batching is the collection of messages sent in one request.
- Helps reduce request overhead and improve throughput.

Tools and messages
------------------
- Tools:
  - response(name, args, id, type)
- Model:
  - tools calling
  - structured output
- Message:
  - message(role, content, name, id, type)

Roles
-----
- system
- ai
- user
- tool
"""
