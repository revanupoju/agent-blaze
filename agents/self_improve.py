"""
Recursive Self-Improvement Engine for Agent Blaze
Inspired by Karpathy's autoresearch — agents evaluate their own output,
score it, and iterate until quality improves.

The loop:
  1. Generate content
  2. Self-evaluate (score 1-10 on relatability, authenticity, emotional impact)
  3. If score < threshold, identify weaknesses and regenerate
  4. Keep the best version
  5. Learn: store what worked in memory for future generations
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from agents.llm_client import generate

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "improvements"


EVALUATOR_PROMPT = """You are a strict content quality evaluator for Apollo Cash marketing.

Score the content on these 5 dimensions (1-10 each):

1. **Relatability** — Would a gig worker / salaried person in tier 2/3 India think "this is my life"?
2. **Authenticity** — Does it sound like a real person, not a brand? No corporate speak?
3. **Emotional Impact** — Does it make you feel something (shame, relief, humor, hope)?
4. **Specificity** — Does it use specific details (₹7,500, Wednesday 11 PM) not vague generalities?
5. **Non-Promotional** — Does it avoid sounding like an ad? No "Apply now", no hard CTAs?

SCORING RULES:
- 1-3: Bad. Corporate, generic, salesy.
- 4-5: Mediocre. Somewhat relatable but forgettable.
- 6-7: Good. Would stop someone scrolling.
- 8-9: Great. Would get shared.
- 10: Perfect. Indistinguishable from a real person's post.

Respond ONLY in this JSON format:
{
  "scores": {
    "relatability": X,
    "authenticity": X,
    "emotional_impact": X,
    "specificity": X,
    "non_promotional": X
  },
  "average": X.X,
  "weaknesses": ["specific weakness 1", "specific weakness 2"],
  "strengths": ["specific strength 1"],
  "improvement_suggestions": ["do this to make it better", "change this"]
}
"""

IMPROVER_PROMPT = """You are a content improvement agent. You take content that scored poorly
and rewrite it to be better based on specific feedback.

RULES:
- Fix ONLY the weaknesses identified — don't change what's already working
- Make it more specific (add real amounts, times, scenarios)
- Make it more emotional (show the feeling, not just the situation)
- Remove any corporate/promotional language
- Keep it the same format and length
- The rewritten version should feel like a real person wrote it
"""


def evaluate_content(content: str) -> dict:
    """Self-evaluate content quality. Returns scores and improvement suggestions."""
    try:
        raw = generate(EVALUATOR_PROMPT, f"Evaluate this content:\n\n{content}", temperature=0.3, max_tokens=500)
        # Parse JSON from response
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)
    except Exception as e:
        return {"average": 5.0, "error": str(e), "weaknesses": [], "improvement_suggestions": []}


def improve_content(content: str, evaluation: dict) -> str:
    """Rewrite content based on evaluation feedback."""
    weaknesses = "\n".join(f"- {w}" for w in evaluation.get("weaknesses", []))
    suggestions = "\n".join(f"- {s}" for s in evaluation.get("improvement_suggestions", []))

    prompt = f"""Original content:
{content}

Evaluation score: {evaluation.get('average', 5)}/10

Weaknesses:
{weaknesses}

Improvement suggestions:
{suggestions}

Rewrite the content to fix these issues. Output ONLY the improved content, nothing else."""

    return generate(IMPROVER_PROMPT, prompt, temperature=0.9, max_tokens=2000)


def self_improve_loop(content: str, max_iterations: int = 3, threshold: float = 7.0) -> dict:
    """Run the recursive self-improvement loop.

    1. Evaluate content
    2. If below threshold, improve and re-evaluate
    3. Keep best version
    4. Return improvement history
    """
    history = []
    best_content = content
    best_score = 0.0
    current = content

    for iteration in range(max_iterations):
        # Evaluate
        evaluation = evaluate_content(current)
        score = evaluation.get("average", 5.0)

        history.append({
            "iteration": iteration + 1,
            "score": score,
            "content_preview": current[:200],
            "weaknesses": evaluation.get("weaknesses", []),
            "strengths": evaluation.get("strengths", []),
        })

        # Track best
        if score > best_score:
            best_score = score
            best_content = current

        # If above threshold, we're done
        if score >= threshold:
            break

        # Below threshold — improve
        if iteration < max_iterations - 1:
            current = improve_content(current, evaluation)

    return {
        "original": content[:200],
        "final": best_content,
        "final_score": best_score,
        "iterations": len(history),
        "history": history,
        "improved": best_score > history[0]["score"] if history else False,
        "timestamp": datetime.now().isoformat(),
    }


def batch_improve(contents: list[str], threshold: float = 7.0) -> list[dict]:
    """Improve a batch of content pieces."""
    results = []
    for content in contents:
        result = self_improve_loop(content, threshold=threshold)
        results.append(result)
    return results
