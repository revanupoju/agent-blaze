"""Unified LLM client — Cerebras (default), Ollama, Anthropic, or OpenAI."""

from __future__ import annotations

import os
import json
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
    return response.choices[0].message.content


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
    return response.choices[0].message.content


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
    return response.choices[0].message.content


def generate(system_prompt: str, user_prompt: str, temperature: float = 0.9, max_tokens: int = 4096) -> str:
    """Call the configured LLM provider and return the raw text response."""
    if PROVIDER == "cerebras":
        return _call_cerebras(system_prompt, user_prompt, temperature, max_tokens)
    if PROVIDER == "ollama":
        return _call_ollama(system_prompt, user_prompt, temperature, max_tokens)
    if PROVIDER == "openai":
        return _call_openai(system_prompt, user_prompt, temperature, max_tokens)
    if PROVIDER == "anthropic":
        return _call_anthropic(system_prompt, user_prompt, temperature, max_tokens)
    return _call_cerebras(system_prompt, user_prompt, temperature, max_tokens)


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
