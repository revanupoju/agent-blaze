"""
Layer 5 — LLM Core

The model (Claude, GPT-4o, Gemini, Llama, Mistral).
Swappable — the harness is model-agnostic. Every upper layer talks to
this interface, never to a provider SDK directly.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# ── Data types shared across the harness ────────────────────────

@dataclass
class ToolCall:
    """An LLM's request to invoke a tool."""
    tool_name: str
    arguments: dict[str, Any]
    call_id: str = ""


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""
    name: str = ""


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"  # "end_turn" | "tool_use" | "max_tokens"
    raw: Any = None  # provider-specific raw response for debugging


# ── Abstract base ───────────────────────────────────────────────

class LLMProvider(ABC):
    """Interface every model provider must implement."""

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...

    @abstractmethod
    def name(self) -> str:
        ...


# ── Anthropic Claude ────────────────────────────────────────────

class ClaudeProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model

    def name(self) -> str:
        return f"claude/{self.model}"

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Separate system message
        system_text = ""
        api_messages = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            elif m.role == "tool":
                api_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m.tool_call_id,
                            "content": m.content,
                        }
                    ],
                })
            elif m.role == "assistant" and m.tool_calls:
                content_blocks: list[dict] = []
                if m.content:
                    content_blocks.append({"type": "text", "text": m.content})
                for tc in m.tool_calls:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc.call_id,
                        "name": tc.tool_name,
                        "input": tc.arguments,
                    })
                api_messages.append({"role": "assistant", "content": content_blocks})
            else:
                api_messages.append({"role": m.role, "content": m.content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if system_text:
            kwargs["system"] = system_text
        if tools:
            kwargs["tools"] = [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": t["parameters"],
                }
                for t in tools
            ]

        resp = self.client.messages.create(**kwargs)

        # Parse response
        text_parts = []
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        tool_name=block.name,
                        arguments=block.input,
                        call_id=block.id,
                    )
                )

        stop = "tool_use" if tool_calls else "end_turn"
        return LLMResponse(
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            stop_reason=stop,
            raw=resp,
        )


# ── OpenAI GPT ──────────────────────────────────────────────────

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def name(self) -> str:
        return f"openai/{self.model}"

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        api_messages = []
        for m in messages:
            if m.role == "tool":
                api_messages.append({
                    "role": "tool",
                    "content": m.content,
                    "tool_call_id": m.tool_call_id,
                })
            elif m.role == "assistant" and m.tool_calls:
                oai_tool_calls = []
                for tc in m.tool_calls:
                    oai_tool_calls.append({
                        "id": tc.call_id,
                        "type": "function",
                        "function": {
                            "name": tc.tool_name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    })
                msg_dict: dict[str, Any] = {"role": "assistant", "tool_calls": oai_tool_calls}
                if m.content:
                    msg_dict["content"] = m.content
                api_messages.append(msg_dict)
            else:
                api_messages.append({"role": m.role, "content": m.content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
                for t in tools
            ]

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        text = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        tool_name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                        call_id=tc.id,
                    )
                )

        stop = "tool_use" if tool_calls else "end_turn"
        return LLMResponse(content=text, tool_calls=tool_calls, stop_reason=stop, raw=resp)


# ── Cerebras (open-source models, ultra-fast inference) ─────────

class CerebrasProvider(LLMProvider):
    def __init__(self, model: str = "llama3.1-8b"):
        from cerebras.cloud.sdk import Cerebras
        self.client = Cerebras()
        self.model = model

    def name(self) -> str:
        return f"cerebras/{self.model}"

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        api_messages = []
        for m in messages:
            if m.role == "tool":
                api_messages.append({
                    "role": "tool",
                    "content": m.content,
                    "tool_call_id": m.tool_call_id,
                })
            elif m.role == "assistant" and m.tool_calls:
                oai_tool_calls = []
                for tc in m.tool_calls:
                    oai_tool_calls.append({
                        "id": tc.call_id,
                        "type": "function",
                        "function": {
                            "name": tc.tool_name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    })
                msg_dict: dict[str, Any] = {"role": "assistant", "tool_calls": oai_tool_calls}
                if m.content:
                    msg_dict["content"] = m.content
                api_messages.append(msg_dict)
            else:
                api_messages.append({"role": m.role, "content": m.content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
                for t in tools
            ]

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        text = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        tool_name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                        call_id=tc.id,
                    )
                )

        stop = "tool_use" if tool_calls else "end_turn"
        return LLMResponse(content=text, tool_calls=tool_calls, stop_reason=stop, raw=resp)


# ── Ollama (local, free, fully offline) ─────────────────────────

class OllamaProvider(LLMProvider):
    """Uses Ollama's OpenAI-compatible API running locally."""

    def __init__(self, model: str = "llama3.1"):
        from openai import OpenAI
        self.client = OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",  # Ollama doesn't need a real key
        )
        self.model = model

    def name(self) -> str:
        return f"ollama/{self.model}"

    def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        api_messages = []
        for m in messages:
            if m.role == "tool":
                api_messages.append({
                    "role": "tool",
                    "content": m.content,
                    "tool_call_id": m.tool_call_id,
                })
            elif m.role == "assistant" and m.tool_calls:
                oai_tool_calls = []
                for tc in m.tool_calls:
                    oai_tool_calls.append({
                        "id": tc.call_id,
                        "type": "function",
                        "function": {
                            "name": tc.tool_name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    })
                msg_dict: dict[str, Any] = {"role": "assistant", "tool_calls": oai_tool_calls}
                if m.content:
                    msg_dict["content"] = m.content
                api_messages.append(msg_dict)
            else:
                api_messages.append({"role": m.role, "content": m.content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
                for t in tools
            ]

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        text = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        tool_name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                        call_id=tc.id,
                    )
                )

        stop = "tool_use" if tool_calls else "end_turn"
        return LLMResponse(content=text, tool_calls=tool_calls, stop_reason=stop, raw=resp)


# ── Factory ─────────────────────────────────────────────────────

def get_provider(provider: str | None = None, model: str | None = None) -> LLMProvider:
    """Create an LLM provider from environment or explicit args."""
    provider = provider or os.getenv("LLM_PROVIDER", "cerebras")
    if provider == "cerebras":
        return CerebrasProvider(model=model or os.getenv("CEREBRAS_MODEL", "llama3.1-8b"))
    if provider == "ollama":
        return OllamaProvider(model=model or os.getenv("OLLAMA_MODEL", "llama3.1"))
    if provider == "openai":
        return OpenAIProvider(model=model or "gpt-4o")
    if provider == "anthropic":
        return ClaudeProvider(model=model or "claude-sonnet-4-20250514")
    return CerebrasProvider(model=model or "llama3.1-8b")
