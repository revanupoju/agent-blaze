"""
Layer 2 — Orchestration Layer

Planning loop, routing, sub-agent management.
Decides what happens next. Runs the ReAct / tool-calling loop.

The harness loop:
  User Goal → Intent Capture → Load Memory → LLM Reasoning
  → Tool Execution → Verify + Persist → Done or Loop ↻
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from harness.llm_core import LLMProvider, Message, LLMResponse, ToolCall, get_provider
from harness.memory import MemoryStore
from harness.tools import get_tool_schemas, execute_tool


# Maximum iterations to prevent runaway loops
MAX_ITERATIONS = 15

# ── Orchestrator system prompt ──────────────────────────────────

ORCHESTRATOR_SYSTEM = """You are the Apollo Cash AI Marketing Orchestrator.

You manage three sub-agents for Apollo Cash marketing:
1. **Social Media Content Engine** — generates Hinglish social posts, carousels, reels, memes
2. **SEO + Article Agent** — generates blog articles targeting high-intent keywords
3. **Community Distribution Agent** — generates authentic community responses

You have tools to invoke each agent's capabilities. When the user gives you a goal,
you should:
1. Break it into sub-tasks
2. Decide which tools to call
3. Execute them step by step
4. Verify the output quality
5. Report results

IMPORTANT RULES:
- Always generate content in Hinglish (Hindi+English) unless explicitly asked for English
- Content must feel human and relatable, never corporate
- When generating social posts, cover multiple audience segments
- When generating articles, ensure proper SEO structure
- When generating community responses, ~70% should mention Apollo Cash, ~30% should be pure advice
- After generating content, briefly verify it meets quality standards
- Track what you've generated to avoid repetition

You can call tools to execute actions. Plan your approach, then act.
"""


@dataclass
class HarnessStep:
    """One iteration of the harness loop."""
    step_number: int
    phase: str  # "intent" | "memory" | "reasoning" | "tool_execution" | "verify" | "done"
    description: str
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    llm_output: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class HarnessRun:
    """A complete run of the harness loop for one user goal."""
    run_id: str
    goal: str
    steps: list[HarnessStep] = field(default_factory=list)
    status: str = "running"  # "running" | "completed" | "error"
    final_output: str = ""
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.run_id:
            self.run_id = str(uuid.uuid4())[:8]
        if not self.started_at:
            self.started_at = datetime.now().isoformat()


class Orchestrator:
    """The ReAct-style orchestration loop.

    Implements the harness flow:
      User Goal → Intent Capture → Load Memory → LLM Reasoning
      → Tool Execution → Verify + Persist → Done or Loop ↻
    """

    def __init__(
        self,
        llm: LLMProvider | None = None,
        memory: MemoryStore | None = None,
    ):
        self.llm = llm or get_provider()
        self.memory = memory or MemoryStore()
        self.runs: list[HarnessRun] = []
        self._step_callbacks: list = []

    def on_step(self, callback) -> None:
        """Register a callback that fires after each harness step.
        Signature: callback(run: HarnessRun, step: HarnessStep)
        """
        self._step_callbacks.append(callback)

    def _emit_step(self, run: HarnessRun, step: HarnessStep) -> None:
        for cb in self._step_callbacks:
            cb(run, step)

    # ── The main loop ───────────────────────────────────────────

    def run(self, goal: str) -> HarnessRun:
        """Execute the full harness loop for a user goal."""
        harness_run = HarnessRun(run_id="", goal=goal)
        self.runs.append(harness_run)

        try:
            # Phase 1: Intent Capture
            intent_step = HarnessStep(
                step_number=1,
                phase="intent",
                description=f"Captured user goal: {goal}",
            )
            harness_run.steps.append(intent_step)
            self._emit_step(harness_run, intent_step)

            # Phase 2: Load Memory
            context = self.memory.build_context()
            memory_step = HarnessStep(
                step_number=2,
                phase="memory",
                description=f"Loaded context ({len(context)} chars)",
            )
            harness_run.steps.append(memory_step)
            self._emit_step(harness_run, memory_step)

            # Build initial messages
            system_msg = ORCHESTRATOR_SYSTEM
            if context and context != "No prior context available.":
                system_msg += f"\n\n## Context from Memory\n{context}"

            messages: list[Message] = [
                Message(role="system", content=system_msg),
                Message(role="user", content=goal),
            ]

            # Phase 3-N: ReAct Loop (Reasoning → Tool Execution → Verify → Loop)
            iteration = 0
            while iteration < MAX_ITERATIONS:
                iteration += 1

                # LLM Reasoning
                response = self.llm.chat(
                    messages=messages,
                    tools=get_tool_schemas(),
                    temperature=0.7,
                    max_tokens=4096,
                )

                reasoning_step = HarnessStep(
                    step_number=len(harness_run.steps) + 1,
                    phase="reasoning",
                    description=f"LLM reasoning (iteration {iteration})",
                    llm_output=response.content,
                )

                if not response.tool_calls:
                    # No tool calls — model is done
                    reasoning_step.phase = "done"
                    reasoning_step.description = "LLM completed — no more tool calls"
                    harness_run.steps.append(reasoning_step)
                    self._emit_step(harness_run, reasoning_step)
                    harness_run.final_output = response.content
                    break

                # Record tool calls in the step
                reasoning_step.tool_calls = [
                    {"tool": tc.tool_name, "args": tc.arguments, "id": tc.call_id}
                    for tc in response.tool_calls
                ]
                harness_run.steps.append(reasoning_step)
                self._emit_step(harness_run, reasoning_step)

                # Add assistant message to conversation
                messages.append(Message(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                ))

                # Tool Execution
                for tc in response.tool_calls:
                    exec_step = HarnessStep(
                        step_number=len(harness_run.steps) + 1,
                        phase="tool_execution",
                        description=f"Executing tool: {tc.tool_name}",
                        tool_calls=[{"tool": tc.tool_name, "args": tc.arguments}],
                    )

                    result = execute_tool(tc.tool_name, tc.arguments)

                    exec_step.tool_results = [{"tool": tc.tool_name, "result_preview": result[:500]}]
                    harness_run.steps.append(exec_step)
                    self._emit_step(harness_run, exec_step)

                    # Add tool result to conversation
                    messages.append(Message(
                        role="tool",
                        content=result,
                        tool_call_id=tc.call_id,
                        name=tc.tool_name,
                    ))

                # Verify + Persist
                verify_step = HarnessStep(
                    step_number=len(harness_run.steps) + 1,
                    phase="verify",
                    description=f"Verify & persist after iteration {iteration}",
                )
                # Save what was generated to memory
                for tc in response.tool_calls:
                    self.memory.persist(
                        key=f"generated:{tc.tool_name}:{datetime.now().strftime('%H%M%S')}",
                        value={"tool": tc.tool_name, "args": tc.arguments},
                        category="content",
                    )
                harness_run.steps.append(verify_step)
                self._emit_step(harness_run, verify_step)

            else:
                harness_run.final_output = "Reached maximum iterations."

            harness_run.status = "completed"
            harness_run.completed_at = datetime.now().isoformat()

        except Exception as e:
            harness_run.status = "error"
            harness_run.final_output = f"Error: {str(e)}"
            harness_run.completed_at = datetime.now().isoformat()
            error_step = HarnessStep(
                step_number=len(harness_run.steps) + 1,
                phase="error",
                description=str(e),
            )
            harness_run.steps.append(error_step)
            self._emit_step(harness_run, error_step)

        # Persist run summary
        self.memory.persist(
            key=f"run:{harness_run.run_id}",
            value={
                "goal": harness_run.goal,
                "status": harness_run.status,
                "steps": len(harness_run.steps),
                "completed_at": harness_run.completed_at,
            },
            category="session",
        )

        return harness_run

    def get_run_summary(self, run: HarnessRun) -> dict:
        """Get a structured summary of a harness run."""
        return {
            "run_id": run.run_id,
            "goal": run.goal,
            "status": run.status,
            "total_steps": len(run.steps),
            "phases": [s.phase for s in run.steps],
            "tools_called": [
                tc["tool"]
                for s in run.steps
                for tc in s.tool_calls
            ],
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "final_output": run.final_output[:500] if run.final_output else "",
            "steps": [
                {
                    "step": s.step_number,
                    "phase": s.phase,
                    "description": s.description,
                    "tool_calls": s.tool_calls,
                    "llm_output": s.llm_output[:200] if s.llm_output else "",
                }
                for s in run.steps
            ],
        }
