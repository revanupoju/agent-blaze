"""Agent 3: Community Distribution Agent for Apollo Cash."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from agents.llm_client import generate_json
from agents.prompts import COMMUNITY_SYSTEM, COMMUNITY_USER_TEMPLATE
from config.settings import COMMUNITY_TARGETS

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "community"

# Realistic thread scenarios that the agent should respond to
THREAD_SCENARIOS = [
    {
        "platform": "reddit",
        "subreddit": "r/personalfinanceindia",
        "scenario": "Someone urgently needs ₹20K for mother's medical bills, salary comes next week",
    },
    {
        "platform": "reddit",
        "subreddit": "r/india",
        "scenario": "Gig worker asking how to manage irregular income and sudden expenses",
    },
    {
        "platform": "reddit",
        "subreddit": "r/IndianStreetBets",
        "scenario": "Young person asking if instant loan apps are safe or all scams",
    },
    {
        "platform": "quora",
        "subreddit": "Personal Finance in India",
        "scenario": "First-time borrower asking how to get a loan without CIBIL score",
    },
    {
        "platform": "quora",
        "subreddit": "Loans in India",
        "scenario": "Auto driver asking which loan app works without salary slip",
    },
    {
        "platform": "twitter",
        "subreddit": "Twitter/X",
        "scenario": "Someone tweeting about salary being delayed for the 3rd month in a row",
    },
    {
        "platform": "twitter",
        "subreddit": "Twitter/X",
        "scenario": "Person ranting about predatory loan apps that harass contacts",
    },
    {
        "platform": "facebook_group",
        "subreddit": "Delivery Partners India (Facebook Group)",
        "scenario": "Delivery boy asking how others handle bike repair costs when they have no savings",
    },
    {
        "platform": "reddit",
        "subreddit": "r/IndiaInvestments",
        "scenario": "Thread discussing the best short-term borrowing options for emergencies",
    },
    {
        "platform": "facebook_group",
        "subreddit": "Small Business Owners India",
        "scenario": "Kirana shop owner needs to restock inventory but cash flow is tight",
    },
    {
        "platform": "quora",
        "subreddit": "Financial Planning for Young Indians",
        "scenario": "College graduate in first job asking about managing finances with ₹18K salary",
    },
    {
        "platform": "reddit",
        "subreddit": "r/india",
        "scenario": "Someone comparing borrowing from family vs using a loan app - which is less stressful",
    },
]


def generate_responses(
    count: int = 10,
    platforms: list[str] | None = None,
    scenarios: list[dict] | None = None,
) -> list[dict]:
    """Generate community responses for simulated threads."""
    if platforms is None:
        platforms = ["reddit", "quora", "twitter", "facebook_group"]
    if scenarios is None:
        scenarios = THREAD_SCENARIOS[:count]

    scenario_descriptions = []
    for s in scenarios:
        scenario_descriptions.append(
            f"[{s['platform'].upper()} — {s.get('subreddit', '')}] {s['scenario']}"
        )

    prompt = COMMUNITY_USER_TEMPLATE.format(
        count=count,
        platforms=", ".join(platforms),
        scenarios="\n".join(f"  {i+1}. {s}" for i, s in enumerate(scenario_descriptions)),
    )

    responses = generate_json(COMMUNITY_SYSTEM, prompt, max_tokens=6000)
    return responses


def generate_thread_discovery() -> dict:
    """Simulate daily thread discovery across platforms."""
    discovery_prompt = f"""
Simulate a daily thread discovery report for Apollo Cash's community agent.

Based on these target communities and keywords:
{json.dumps(COMMUNITY_TARGETS, indent=2)}

Generate a realistic report of threads/posts discovered today that the agent could
respond to. Include a mix of:
- High-relevance (directly asking about loans/money problems)
- Medium-relevance (discussing financial stress generally)
- Low-relevance (tangentially related, should probably skip)

Return a JSON object:
{{
  "discovery_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "total_discovered": number,
  "high_relevance": [
    {{
      "platform": "...",
      "community": "...",
      "title": "thread title",
      "snippet": "first 100 chars of the post",
      "relevance_score": 0.0-1.0,
      "recommended_action": "respond" | "monitor" | "skip",
      "response_priority": "high" | "medium" | "low",
      "suggested_tone": "empathetic" | "helpful" | "educational"
    }}
  ],
  "medium_relevance": [...],
  "low_relevance": [...],
  "daily_stats": {{
    "total_scanned": number,
    "actionable": number,
    "responded": 0,
    "skipped": number
  }}
}}

Return ONLY the JSON object.
"""
    return generate_json(COMMUNITY_SYSTEM, discovery_prompt)


def save_responses(responses: list[dict], filename: str | None = None) -> str:
    """Save generated responses to a JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"responses_{timestamp}.json"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    return str(filepath)


def run_full_pipeline(num_responses: int = 12) -> dict:
    """Run the complete community distribution pipeline."""
    # Generate responses
    responses = generate_responses(count=num_responses)
    filepath = save_responses(responses, "all_responses.json")

    # Generate thread discovery report
    discovery = generate_thread_discovery()
    discovery_path = OUTPUT_DIR / "thread_discovery.json"
    with open(discovery_path, "w", encoding="utf-8") as f:
        json.dump(discovery, f, indent=2, ensure_ascii=False)

    # Calculate stats
    mentions_apollo = sum(1 for r in responses if r.get("response", {}).get("mentions_apollo_cash", False))

    return {
        "total_responses": len(responses),
        "responses_file": filepath,
        "discovery_file": str(discovery_path),
        "apollo_cash_mentions": mentions_apollo,
        "no_mention_responses": len(responses) - mentions_apollo,
        "mention_ratio": f"{mentions_apollo}/{len(responses)}",
        "responses": responses,
        "discovery": discovery,
    }
