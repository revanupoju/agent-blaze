"""
Content Research & Trend Analysis Skill

Researches trending topics, competitor content, audience sentiment,
and viral formats relevant to Apollo Cash's target audience.
Feeds insights into the content generation agents.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from agents.llm_client import generate_json
from config.settings import AUDIENCE_SEGMENTS, BRAND

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "research"

RESEARCH_SYSTEM = """You are a market research analyst specializing in Indian fintech,
personal lending, and tier 2/3 digital consumers. You analyze trends, competitor
strategies, and audience behavior to inform Apollo Cash's content strategy.

Apollo Cash is a personal loan app targeting gig workers, salaried individuals in
tier 2/3 cities, self-employed workers, and NTC (New To Credit) youth in India.
Loans from ₹5,000 to ₹2,00,000, disbursed in 15 minutes.

Your research should be:
- Data-informed (use realistic estimates for Indian market)
- Actionable (every insight should map to a content opportunity)
- Audience-specific (different segments have different triggers)
- Culturally aware (Indian festivals, salary cycles, regional nuances)
"""


def research_trending_topics() -> dict:
    """Research what's trending for the target audience right now."""
    prompt = f"""
Research current trending topics and content opportunities for Apollo Cash.
Today's date: {datetime.now().strftime('%B %Y')}

Analyze:
1. **Seasonal triggers** — What financial events are happening now?
   (festivals, tax season, school fees, wedding season, monsoon repairs)
2. **Viral content formats** — What content formats are performing well
   on Instagram Reels, YouTube Shorts, and Facebook in India right now?
3. **Competitor content analysis** — What are Slice, Fi Money, KreditBee,
   Fibe doing on social media? What's working for them?
4. **Audience pain points right now** — Based on the season/month,
   what money problems are people facing?
5. **Hashtag trends** — Which hashtags are active in the personal
   finance / gig worker / tier 2 India space?
6. **Meme formats** — What meme templates are viral in India right now
   that could be adapted for financial content?

Return a JSON object:
{{
  "research_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "seasonal_triggers": [
    {{"trigger": "...", "relevance": "high/medium/low", "content_opportunity": "..."}}
  ],
  "viral_formats": [
    {{"format": "...", "platform": "...", "why_it_works": "...", "apollo_adaptation": "..."}}
  ],
  "competitor_insights": [
    {{"brand": "...", "what_works": "...", "gap_for_apollo": "..."}}
  ],
  "current_pain_points": [
    {{"pain_point": "...", "audience_segment": "...", "content_angle": "..."}}
  ],
  "trending_hashtags": ["#tag1", "#tag2"],
  "meme_templates": [
    {{"template": "...", "how_to_adapt": "..."}}
  ],
  "top_5_content_ideas": [
    {{"idea": "...", "format": "...", "platform": "...", "audience": "...", "why_now": "..."}}
  ]
}}

Return ONLY the JSON object.
"""
    return generate_json(RESEARCH_SYSTEM, prompt)


def research_audience_sentiment(segment: str = "gig_workers") -> dict:
    """Deep-dive into what a specific audience segment is talking about online."""
    seg = AUDIENCE_SEGMENTS.get(segment, AUDIENCE_SEGMENTS["gig_workers"])
    prompt = f"""
Research the online sentiment and conversations of this audience segment:

Segment: {seg['label']} — {seg['description']}
Pain points: {', '.join(seg['pain_points'])}
Platforms they use: {', '.join(seg['platforms'])}

Analyze:
1. What are they posting about on social media?
2. What questions are they asking on Reddit / Quora?
3. What language/slang do they use when talking about money?
4. What are their biggest fears about borrowing?
5. What would make them trust a loan app?
6. What content would they share with friends?

Return a JSON object:
{{
  "segment": "{segment}",
  "online_conversations": [
    {{"topic": "...", "platform": "...", "sample_post": "...", "sentiment": "..."}}
  ],
  "common_questions": ["...", "..."],
  "language_patterns": {{
    "slang_terms": ["..."],
    "common_phrases": ["..."],
    "emoji_usage": "...",
    "tone": "..."
  }},
  "trust_factors": ["...", "..."],
  "fear_factors": ["...", "..."],
  "shareable_content_types": ["...", "..."],
  "content_recommendations": [
    {{"type": "...", "topic": "...", "format": "...", "hook": "..."}}
  ]
}}

Return ONLY the JSON object.
"""
    return generate_json(RESEARCH_SYSTEM, prompt)


def analyze_engagement_and_adapt(engagement_data: dict) -> dict:
    """Analyze engagement metrics and recommend content strategy adjustments.

    This is the adaptation skill — it takes what's working and suggests
    what to do more/less of.
    """
    prompt = f"""
Analyze this engagement data and recommend content strategy adjustments
for Apollo Cash:

{json.dumps(engagement_data, indent=2, ensure_ascii=False)}

Provide:
1. What content types/themes are performing best?
2. What should we do MORE of?
3. What should we STOP doing?
4. What new angles should we try?
5. Optimal posting times based on engagement patterns
6. Audience segment adjustments

Return a JSON object:
{{
  "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "top_performers": [
    {{"content_type": "...", "theme": "...", "why_it_worked": "..."}}
  ],
  "do_more": [
    {{"action": "...", "expected_impact": "...", "priority": "high/medium/low"}}
  ],
  "stop_doing": [
    {{"action": "...", "reason": "..."}}
  ],
  "new_experiments": [
    {{"experiment": "...", "hypothesis": "...", "format": "..."}}
  ],
  "optimal_schedule": {{
    "best_days": ["..."],
    "best_times": ["..."],
    "worst_times": ["..."]
  }},
  "segment_adjustments": [
    {{"segment": "...", "adjustment": "..."}}
  ],
  "next_week_strategy": "one paragraph summary of recommended strategy"
}}

Return ONLY the JSON object.
"""
    return generate_json(RESEARCH_SYSTEM, prompt)


def save_research(data: dict, name: str) -> str:
    """Save research output to file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"{name}_{timestamp}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(filepath)


def run_full_research() -> dict:
    """Run complete research pipeline."""
    results = {}

    # Trending topics
    trends = research_trending_topics()
    results["trends"] = trends
    save_research(trends, "trending_topics")

    # Audience sentiment for each segment
    for segment in AUDIENCE_SEGMENTS:
        sentiment = research_audience_sentiment(segment)
        results[f"sentiment_{segment}"] = sentiment
        save_research(sentiment, f"sentiment_{segment}")

    # Mock engagement data for adaptation demo
    mock_engagement = {
        "period": "last_7_days",
        "posts": [
            {"format": "reel", "theme": "salary delay", "likes": 2400, "shares": 180, "comments": 95},
            {"format": "carousel", "theme": "bike repair", "likes": 1800, "shares": 120, "comments": 60},
            {"format": "meme", "theme": "month end", "likes": 3200, "shares": 450, "comments": 200},
            {"format": "facebook_post", "theme": "medical emergency", "likes": 900, "shares": 45, "comments": 30},
            {"format": "carousel", "theme": "festival season", "likes": 2100, "shares": 210, "comments": 85},
            {"format": "reel", "theme": "first loan experience", "likes": 3800, "shares": 520, "comments": 310},
        ],
        "top_performing_segment": "ntc_youth",
        "top_platform": "instagram",
    }
    adaptation = analyze_engagement_and_adapt(mock_engagement)
    results["adaptation"] = adaptation
    save_research(adaptation, "engagement_adaptation")

    return results
