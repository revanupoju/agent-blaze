"""
Layer 3 — Context & Memory Layer (powered by Mem0)

Semantic vector memory for all agents. Replaces flat JSON with
Mem0's auto-extraction, vector search, and cross-agent recall.
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Any

try:
    from mem0 import MemoryClient
    MEM0_KEY = os.environ.get("MEM0_API_KEY", "m0-CoQ1cXICObbl2S0YKLeqanooIrCi9SRqZmbb6Dd5")
    _client = MemoryClient(api_key=MEM0_KEY) if MEM0_KEY else None
    print("[MEMORY] Mem0 connected")
except Exception as e:
    _client = None
    print(f"[MEMORY] Mem0 not available: {e}")


class MemoryStore:
    """Semantic memory store powered by Mem0.

    Each agent has its own user_id namespace. Memories are:
    - Auto-extracted from conversations
    - Semantically searchable (not keyword-based)
    - Shared across sessions (persistent)
    - Cross-agent accessible via org_id
    """

    ORG_ID = "agent-blaze"

    def __init__(self):
        self._fallback: dict[str, Any] = {}  # In-memory fallback if Mem0 is down

    # ── Store memories ─────────────────────────────────────────

    def remember(self, key: str, value: Any, category: str = "session") -> None:
        """Store in memory (backward compat)."""
        self._fallback[key] = {"value": value, "category": category}

    def recall(self, key: str) -> Any | None:
        """Recall by key (backward compat)."""
        entry = self._fallback.get(key)
        return entry["value"] if entry else None

    def persist(self, key: str, value: Any, category: str = "strategy") -> None:
        """Persist a memory to Mem0."""
        if _client:
            try:
                text = f"[{category}] {key}: {json.dumps(value, ensure_ascii=False)}" if not isinstance(value, str) else f"[{category}] {key}: {value}"
                _client.add(text, user_id=self.ORG_ID, metadata={"category": category, "key": key})
            except Exception as e:
                print(f"[MEMORY] Persist error: {e}")
        self._fallback[key] = {"value": value, "category": category, "timestamp": datetime.now().isoformat()}

    # ── Agent-specific memory ──────────────────────────────────

    def add_agent_memory(self, agent: str, messages: list[dict], content: str = "") -> None:
        """Store conversation + generated content as agent memory.

        Mem0 auto-extracts relevant facts from the conversation.
        """
        if not _client:
            return
        try:
            _client.add(messages, user_id=f"agent-{agent}", metadata={"agent": agent})
            if content and len(content) > 100:
                # Store the generated content as a separate memory
                _client.add(
                    f"Generated content ({agent}): {content[:500]}",
                    user_id=f"agent-{agent}",
                    metadata={"type": "generated_content", "agent": agent}
                )
        except Exception as e:
            print(f"[MEMORY] Add error for {agent}: {e}")

    def get_agent_context(self, agent: str, query: str) -> str:
        """Retrieve relevant memories for an agent based on the query.

        Returns a context string to inject into the LLM prompt.
        """
        if not _client:
            return ""
        try:
            results = _client.search(query, user_id=f"agent-{agent}", limit=5)
            if not results or not results.get("results"):
                return ""
            memories = results["results"]
            lines = ["## Agent Memory (from past conversations)\n"]
            for m in memories:
                lines.append(f"- {m.get('memory', '')}")
            return "\n".join(lines)
        except Exception as e:
            print(f"[MEMORY] Search error for {agent}: {e}")
            return ""

    # ── Cross-agent memory ─────────────────────────────────────

    def search_all_agents(self, query: str) -> str:
        """Search memories across ALL agents."""
        if not _client:
            return ""
        try:
            results = _client.search(query, user_id=self.ORG_ID, limit=5)
            if not results or not results.get("results"):
                return ""
            lines = ["## Cross-Agent Memory\n"]
            for m in results["results"]:
                lines.append(f"- {m.get('memory', '')}")
            return "\n".join(lines)
        except Exception as e:
            return ""

    # ── Engagement tracking ────────────────────────────────────

    def log_engagement(self, content_id: str, metrics: dict) -> None:
        """Log engagement metrics for a piece of content."""
        if _client:
            try:
                text = f"Content {content_id} engagement: {json.dumps(metrics)}"
                _client.add(text, user_id=self.ORG_ID, metadata={"type": "engagement", "content_id": content_id})
            except Exception:
                pass
        self._fallback[f"engagement:{content_id}"] = metrics

    def get_top_performing(self, category: str = "engagement", limit: int = 5) -> list:
        """Get top-performing content."""
        if _client:
            try:
                results = _client.search("top performing content highest engagement", user_id=self.ORG_ID, limit=limit)
                return [m.get("memory", "") for m in results.get("results", [])]
            except Exception:
                pass
        return []

    # ── Context builder ────────────────────────────────────────

    def build_context(self) -> str:
        """Build context string from recent memories."""
        if _client:
            try:
                results = _client.get_all(user_id=self.ORG_ID, limit=10)
                if results and results.get("results"):
                    lines = ["## Agent Memory\n"]
                    for m in results["results"]:
                        lines.append(f"- {m.get('memory', '')}")
                    return "\n".join(lines)
            except Exception:
                pass
        return "No prior context available."

    # ── Utilities ──────────────────────────────────────────────

    def clear_session(self) -> None:
        """Clear short-term fallback memory."""
        self._fallback.clear()

    def all_memories(self) -> dict:
        """Return all memories for debugging / dashboard."""
        mem0_memories = []
        if _client:
            try:
                results = _client.get_all(user_id=self.ORG_ID, limit=50)
                mem0_memories = [{"memory": m.get("memory", ""), "id": m.get("id", "")} for m in results.get("results", [])]
            except Exception:
                pass
        return {
            "mem0": mem0_memories,
            "fallback": {k: v for k, v in self._fallback.items()},
            "provider": "mem0" if _client else "fallback",
        }
