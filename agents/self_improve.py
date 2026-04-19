"""
Recursive Self-Improvement Engine — inspired by Karpathy's autoresearch.

The autoresearch pattern applied to marketing content:
  1. Generate content (the "experiment")
  2. Evaluate quality (the "metric" — like val_bpb)
  3. If score improved → keep. If not → discard and try differently.
  4. Log every attempt in experiment_log.jsonl
  5. Learn: store winning patterns in memory for future generations

Like autoresearch, the agent is autonomous — it keeps iterating until
the content quality threshold is met or max iterations reached.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "output" / "experiments"


def evaluate_content(content: str, llm_fn) -> dict:
    """Score content on 5 dimensions. Returns scores + weaknesses."""
    eval_prompt = f"""Rate this marketing content strictly. Score each 1-10:

1. RELATABILITY — Would someone in tier 2/3 India think "this is my life"?
2. AUTHENTICITY — Does it sound like a real person or a brand?
3. EMOTIONAL IMPACT — Does it make you feel something?
4. SPECIFICITY — Real details (₹ amounts, times, places) or vague?
5. NON-PROMOTIONAL — Free of "apply now", feature lists, CTAs?

Content:
{content[:1000]}

Reply with ONLY: SCORES: R/A/E/S/N (five numbers) | WEAKNESSES: list | AVERAGE: number"""

    try:
        raw = llm_fn(
            "You are a strict content evaluator. Be harsh. Output only the requested format.",
            eval_prompt, 0.2, 300
        )
        # Parse scores
        import re
        avg_match = re.search(r'AVERAGE:\s*(\d+(?:\.\d+)?)', raw)
        avg = float(avg_match.group(1)) if avg_match else 5.0

        weakness_match = re.search(r'WEAKNESSES?:\s*(.+?)(?:\||$)', raw, re.DOTALL)
        weaknesses = weakness_match.group(1).strip() if weakness_match else ""

        return {"average": avg, "weaknesses": weaknesses, "raw": raw}
    except Exception as e:
        return {"average": 5.0, "weaknesses": str(e), "raw": ""}


def improve_content(content: str, evaluation: dict, system_prompt: str, llm_fn) -> str:
    """Rewrite content to fix identified weaknesses."""
    prompt = f"""This content scored {evaluation['average']}/10.

Weaknesses: {evaluation['weaknesses']}

Rewrite to fix ONLY the weaknesses. Keep what works. Make it more human, specific, emotional.
Remove any promotional language, CTAs, or feature dumps.

Original:
{content[:1500]}

Output ONLY the improved content:"""

    try:
        return llm_fn(system_prompt, prompt, 0.9, 3000)
    except Exception:
        return content


def autoresearch_loop(
    content: str,
    system_prompt: str,
    llm_fn,
    max_iterations: int = 3,
    threshold: float = 7.0,
    agent_name: str = "unknown",
) -> dict:
    """Run the autoresearch-style improvement loop.

    Like Karpathy's autoresearch:
    - Each iteration is an "experiment"
    - We measure val_bpb equivalent (content quality score)
    - Keep improvements, discard regressions
    - Log everything

    Returns the best content and experiment history.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    best_content = content
    best_score = 0.0
    history = []

    for iteration in range(max_iterations):
        # Evaluate (like running train.py and checking val_bpb)
        evaluation = evaluate_content(current if iteration > 0 else content, llm_fn)
        score = evaluation["average"]

        experiment = {
            "iteration": iteration + 1,
            "score": score,
            "status": "pending",
            "weaknesses": evaluation["weaknesses"],
            "content_preview": (current if iteration > 0 else content)[:150],
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
        }

        # Keep or discard (autoresearch pattern)
        if score > best_score:
            best_score = score
            best_content = current if iteration > 0 else content
            experiment["status"] = "keep"
        else:
            experiment["status"] = "discard"

        history.append(experiment)

        # Log experiment (like results.tsv in autoresearch)
        log_file = LOG_DIR / "experiment_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(experiment) + "\n")

        # If above threshold, stop (good enough)
        if score >= threshold:
            break

        # Below threshold — improve (like modifying train.py for next experiment)
        if iteration < max_iterations - 1:
            current = improve_content(
                best_content, evaluation, system_prompt, llm_fn
            )

    return {
        "best_content": best_content,
        "best_score": best_score,
        "iterations": len(history),
        "improved": best_score > (history[0]["score"] if history else 0),
        "history": history,
    }


def get_experiment_stats() -> dict:
    """Get stats from all experiments (like checking results.tsv)."""
    log_file = LOG_DIR / "experiment_log.jsonl"
    if not log_file.exists():
        return {"total": 0, "kept": 0, "discarded": 0, "avg_score": 0}

    experiments = []
    with open(log_file) as f:
        for line in f:
            try:
                experiments.append(json.loads(line))
            except Exception:
                pass

    if not experiments:
        return {"total": 0, "kept": 0, "discarded": 0, "avg_score": 0}

    return {
        "total": len(experiments),
        "kept": sum(1 for e in experiments if e.get("status") == "keep"),
        "discarded": sum(1 for e in experiments if e.get("status") == "discard"),
        "avg_score": sum(e.get("score", 0) for e in experiments) / len(experiments),
        "best_score": max(e.get("score", 0) for e in experiments),
        "by_agent": {
            agent: {
                "count": sum(1 for e in experiments if e.get("agent") == agent),
                "avg": sum(e.get("score", 0) for e in experiments if e.get("agent") == agent) / max(1, sum(1 for e in experiments if e.get("agent") == agent)),
            }
            for agent in set(e.get("agent", "unknown") for e in experiments)
        },
    }
