"""
Unified LLM client with robust failover chain.

Chain: Cerebras Qwen 235B → Cerebras Llama 3.1 8B → Ollama → error message
Every call retries with backoff on 429. Empty responses trigger next provider.
"""

from __future__ import annotations

import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "cerebras").lower()


def _call_cerebras(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    from cerebras.cloud.sdk import Cerebras
    client = Cerebras()
    response = client.chat.completions.create(
        model=os.getenv("CEREBRAS_MODEL", "llama3.1-8b"),
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _call_cerebras_model(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, model: str) -> str:
    """Call Cerebras with a specific model."""
    from cerebras.cloud.sdk import Cerebras
    client = Cerebras()
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _call_ollama(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    from openai import OpenAI
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )
    response = client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _call_anthropic(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_openai(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


# ── Robust failover chain ───────────────────────────────────────

def generate_with_failover(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    """Call LLM with full failover chain. Never returns empty.

    Chain:
    1. Preferred model (from env CEREBRAS_MODEL, e.g. qwen-3-235b)
    2. Cerebras Llama 3.1 8B (fast fallback)
    3. Ollama local (if running)
    4. Error message (last resort)

    Each step retries 2x with backoff on 429/rate limits.
    Empty responses trigger next provider.
    """
    preferred_model = os.getenv("CEREBRAS_MODEL", "llama3.1-8b")

    # Build chain based on preferred model
    chain = []
    if preferred_model != "llama3.1-8b":
        chain.append(("cerebras/" + preferred_model, lambda s, u, t, m: _call_cerebras_model(s, u, t, m, preferred_model)))
    chain.append(("cerebras/llama3.1-8b", lambda s, u, t, m: _call_cerebras_model(s, u, t, m, "llama3.1-8b")))
    chain.append(("ollama", _call_ollama))

    last_error = ""
    for provider_name, fn in chain:
        for attempt in range(2):
            try:
                result = fn(system_prompt, user_prompt, temperature, max_tokens)
                if result and len(result.strip()) > 10:
                    return result
                last_error = f"Empty response from {provider_name}"
            except Exception as e:
                last_error = f"{provider_name}: {str(e)[:100]}"
                if "429" in str(e) or "rate" in str(e).lower() or "queue" in str(e).lower():
                    time.sleep(1.5 * (attempt + 1))
                else:
                    break  # Non-rate-limit error, try next provider

    return f"All LLM providers unavailable. Last error: {last_error}. Please try again in a moment."


def generate(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    """Call the configured LLM provider with failover."""
    return generate_with_failover(system_prompt, user_prompt, temperature, max_tokens)


def generate_json(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 4096):
    """Call the LLM and parse the response as JSON."""
    raw = generate(system_prompt, user_prompt, temperature, max_tokens)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    return json.loads(cleaned, strict=False)
