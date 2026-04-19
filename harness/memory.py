"""
Layer 3 — Context & Memory Layer

Short-term state, long-term memory, context compression, skills.
What enters the model's context window.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

MEMORY_DIR = Path(__file__).parent.parent / "data" / "memory"


@dataclass
class MemoryEntry:
    """A single memory record."""
    key: str
    value: Any
    category: str  # "engagement", "content", "strategy", "session"
    timestamp: str = ""
    ttl: str = "permanent"  # "session" | "day" | "week" | "permanent"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MemoryStore:
    """Persistent + in-session memory for the agent harness.

    Short-term: lives in memory for the current session (context window).
    Long-term: persisted to disk as JSON, loaded on startup.
    """

    def __init__(self):
        self._short_term: dict[str, MemoryEntry] = {}
        self._long_term: dict[str, MemoryEntry] = {}
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._load_long_term()

    # ── Short-term (session) ────────────────────────────────────

    def remember(self, key: str, value: Any, category: str = "session") -> None:
        """Store in short-term memory (current session only)."""
        self._short_term[key] = MemoryEntry(key=key, value=value, category=category)

    def recall(self, key: str) -> Any | None:
        """Recall from short-term, falling back to long-term."""
        entry = self._short_term.get(key) or self._long_term.get(key)
        return entry.value if entry else None

    # ── Long-term (persisted) ───────────────────────────────────

    def persist(self, key: str, value: Any, category: str = "strategy") -> None:
        """Store in long-term memory (survives across sessions)."""
        entry = MemoryEntry(key=key, value=value, category=category, ttl="permanent")
        self._long_term[key] = entry
        self._save_long_term()

    def _load_long_term(self) -> None:
        """Load long-term memory from disk."""
        path = MEMORY_DIR / "long_term.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, entry_data in data.items():
                self._long_term[key] = MemoryEntry(**entry_data)

    def _save_long_term(self) -> None:
        """Persist long-term memory to disk."""
        data = {}
        for key, entry in self._long_term.items():
            data[key] = {
                "key": entry.key,
                "value": entry.value,
                "category": entry.category,
                "timestamp": entry.timestamp,
                "ttl": entry.ttl,
            }
        path = MEMORY_DIR / "long_term.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Engagement tracking ─────────────────────────────────────

    def log_engagement(self, content_id: str, metrics: dict) -> None:
        """Log engagement metrics for a piece of content."""
        key = f"engagement:{content_id}"
        existing = self.recall(key) or []
        existing.append({**metrics, "timestamp": datetime.now().isoformat()})
        self.persist(key, existing, category="engagement")

    def get_top_performing(self, category: str = "engagement", limit: int = 5) -> list:
        """Get top-performing content based on logged engagement."""
        entries = []
        for key, entry in self._long_term.items():
            if entry.category == category:
                entries.append(entry)
        # Sort by most recent
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return [e.value for e in entries[:limit]]

    # ── Context builder ─────────────────────────────────────────

    def build_context(self) -> str:
        """Build a context string for the LLM from relevant memories.

        This is what gets injected into the model's context window.
        """
        sections = []

        # Session state
        session_items = [e for e in self._short_term.values() if e.category == "session"]
        if session_items:
            sections.append("## Current Session State")
            for item in session_items:
                sections.append(f"- {item.key}: {json.dumps(item.value, ensure_ascii=False)}")

        # Strategy memories
        strategy_items = [e for e in self._long_term.values() if e.category == "strategy"]
        if strategy_items:
            sections.append("\n## Learned Strategy")
            for item in strategy_items[-10:]:  # last 10
                sections.append(f"- {item.key}: {json.dumps(item.value, ensure_ascii=False)}")

        # Recent engagement data
        engagement_items = [e for e in self._long_term.values() if e.category == "engagement"]
        if engagement_items:
            sections.append("\n## Recent Engagement Data")
            for item in engagement_items[-5:]:
                sections.append(f"- {item.key}: {json.dumps(item.value, ensure_ascii=False)}")

        # Content generation history
        content_items = [e for e in self._long_term.values() if e.category == "content"]
        if content_items:
            sections.append("\n## Content History (avoid repetition)")
            for item in content_items[-10:]:
                sections.append(f"- {item.key}")

        return "\n".join(sections) if sections else "No prior context available."

    # ── Utilities ───────────────────────────────────────────────

    def clear_session(self) -> None:
        """Clear short-term memory."""
        self._short_term.clear()

    def all_memories(self) -> dict:
        """Return all memories for debugging / dashboard."""
        return {
            "short_term": {k: {"value": v.value, "category": v.category} for k, v in self._short_term.items()},
            "long_term": {k: {"value": v.value, "category": v.category, "timestamp": v.timestamp} for k, v in self._long_term.items()},
        }
