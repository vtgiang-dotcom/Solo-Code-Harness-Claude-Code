---
name: claude-api
description: "Build, debug, and optimize Anthropic SDK / Claude API apps. Covers model strings, prompt caching, thinking params, streaming, tool use, token counting, and model migration. TRIGGER when: code imports `anthropic`/`@anthropic-ai/sdk`; user asks about Claude API, Anthropic SDK, or model pricing; user adds/modifies Claude features (caching, thinking, tool use, batch, files, citations, memory); user asks about model selection (Opus/Sonnet/Haiku). SKIP: file imports `openai` or uses other provider SDKs."
license: MIT
allowed-tools: "Read, WebFetch, Grep, Glob"
---

# Claude API & Anthropic SDK

Build LLM-powered applications with the Anthropic SDK. Covers Python (`anthropic`) and TypeScript (`@anthropic-ai/sdk`).

## Before Writing Code

1. **Verify the SDK is installed** — check `pip show anthropic` or `npm list @anthropic-ai/sdk`
2. **Check SDK version** — APIs differ between versions. The current stable is `anthropic>=0.39.0`.
3. **Never guess API signatures** — if unsure, WebFetch the official docs: `https://docs.anthropic.com/en/api`

## Model Selection

| Model | String | Use Case |
|-------|--------|----------|
| Opus 4.8 | `claude-opus-4-8` | Complex reasoning, architecture, debugging |
| Sonnet 4.6 | `claude-sonnet-4-6` | Daily coding, PR review, refactoring |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast tasks, search, read-only |

**Defaults:** Use Opus 4.8 for complex work. Use adaptive thinking: `thinking: {type: "adaptive"}`. Use streaming for long inputs/outputs.

## Core Patterns

### Basic Message (Python)

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello"}],
    thinking={"type": "adaptive"},
)
print(message.content[0].text)
```

### Streaming (Python)

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Explain quantum computing"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()
```

### Prompt Caching (Python)

```python
# Cache system prompt + repeated content to reduce costs by 90%
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": "<long system prompt>",
            "cache_control": {"type": "ephemeral"},  # Caches this block
        }
    ],
    messages=[...],
)
# Check cache hit: print(message.usage.cache_read_input_tokens)
```

### Tool Use (Python)

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"],
        },
    }
]

message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)

# Handle tool use response
for block in message.content:
    if block.type == "tool_use":
        print(f"Tool call: {block.name}({block.input})")
```

### Token Counting

```python
# Count tokens before sending
count = client.messages.count_tokens(
    model="claude-opus-4-8",
    system="You are helpful.",
    messages=[{"role": "user", "content": "Hello"}],
)
print(f"Input tokens: {count.input_tokens}")
```

## Anti-Hallucination Rules (DeepSeek-Specific)

When generating Claude API code:

1. **Verify model strings** — never invent model names. Use the exact strings in the table above.
2. **Verify SDK method signatures** — `client.messages.create()`, not `client.completions.create()` or `client.chat()`.
3. **Verify parameter names** — `max_tokens` not `max_tokens_to_sample`, `system` not `system_prompt`.
4. **Never guess pricing** — WebFetch current pricing from `https://www.anthropic.com/pricing`.

## Model Migration

### Upgrading Model Versions

1. Update the `model` string to the new version
2. Check for deprecated parameters (beta headers, `max_tokens_to_sample` → `max_tokens`)
3. Verify thinking params: `{"type": "adaptive"}` is the current default
4. Run tests — model behavior changes between versions
5. Check cost implications — newer models may have different pricing

## Resources

- Official docs: `https://docs.anthropic.com/en/api`
- SDK repo (Python): `https://github.com/anthropics/anthropic-sdk-python`
- SDK repo (TypeScript): `https://github.com/anthropics/anthropic-sdk-typescript`
- Pricing: `https://www.anthropic.com/pricing`
