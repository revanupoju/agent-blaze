"""
Layer 4 — Tool Layer

APIs, file system, content generation, web search.
The agent's "hands." Connects reasoning to real-world actions.
Each tool is a callable with a JSON-schema description so the LLM
can decide when and how to invoke it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# Local agent imports (the actual work happens here)
from agents.social_media_agent import (
    generate_posts,
    generate_content_variations,
    generate_weekly_calendar,
    save_posts,
)
from agents.seo_agent import (
    generate_article,
    generate_keyword_analysis,
    save_article,
    ARTICLE_BRIEFS,
)
from agents.community_agent import (
    generate_responses,
    generate_thread_discovery,
    save_responses,
    THREAD_SCENARIOS,
)
from agents.research_agent import (
    research_trending_topics,
    research_audience_sentiment,
    analyze_engagement_and_adapt,
    save_research,
)
from config.settings import AUDIENCE_SEGMENTS, SEO_KEYWORDS, COMMUNITY_TARGETS


@dataclass
class ToolDefinition:
    """A tool the agent can call."""
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., str]


# ── Tool Implementations ───────────────────────────────────────

def _generate_social_posts(
    count: int = 5,
    audience_segment: str = "gig_workers",
    formats: str = "instagram_carousel,reel_script,facebook_post,meme",
    themes: str = "salary delay,bike repair,festival season,medical emergency",
) -> str:
    """Generate social media posts."""
    fmt_list = [f.strip() for f in formats.split(",")]
    theme_list = [t.strip() for t in themes.split(",")]
    posts = generate_posts(
        count=count,
        formats=fmt_list,
        audience_segment=audience_segment,
        themes=theme_list,
    )
    filepath = save_posts(posts)
    return json.dumps({
        "status": "success",
        "count": len(posts),
        "file": filepath,
        "preview": posts[:2] if len(posts) > 2 else posts,
    }, indent=2, ensure_ascii=False)


def _generate_variations(scenario: str = "", num_variations: int = 3) -> str:
    """Generate content variations of a single scenario."""
    variations = generate_content_variations(scenario, num_variations)
    return json.dumps({
        "status": "success",
        "scenario": scenario,
        "variations": variations,
    }, indent=2, ensure_ascii=False)


def _generate_calendar() -> str:
    """Generate a weekly content calendar."""
    calendar = generate_weekly_calendar()
    output_dir = Path("output/social_media")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "weekly_calendar.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)
    return json.dumps({
        "status": "success",
        "file": str(path),
        "week_start": calendar.get("week_start"),
        "total_posts": calendar.get("total_posts"),
    }, indent=2, ensure_ascii=False)


def _generate_seo_article(
    keyword: str = "",
    language: str = "hinglish",
    audience_segment: str = "ntc_youth",
    article_type: str = "educational",
) -> str:
    """Generate an SEO blog article."""
    brief = {
        "keyword": keyword,
        "secondary_keywords": [],
        "language": language,
        "audience_segment": audience_segment,
        "article_type": article_type,
    }
    # Try to find a matching pre-built brief
    for b in ARTICLE_BRIEFS:
        if b["keyword"].lower() == keyword.lower():
            brief = b
            break

    article = generate_article(brief)
    json_path, md_path = save_article(article)
    return json.dumps({
        "status": "success",
        "keyword": keyword,
        "title": article.get("meta_title", ""),
        "word_count": article.get("word_count", 0),
        "json_path": json_path,
        "md_path": md_path,
    }, indent=2, ensure_ascii=False)


def _keyword_analysis() -> str:
    """Run keyword analysis and prioritization."""
    analysis = generate_keyword_analysis()
    output_dir = Path("output/articles")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "keyword_analysis.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    return json.dumps({
        "status": "success",
        "file": str(path),
        "top_5": analysis.get("top_5_priorities", []),
        "quick_wins": analysis.get("quick_wins", []),
    }, indent=2, ensure_ascii=False)


def _generate_community_responses(
    count: int = 5,
    platforms: str = "reddit,quora,twitter,facebook_group",
) -> str:
    """Generate community responses to simulated threads."""
    platform_list = [p.strip() for p in platforms.split(",")]
    responses = generate_responses(count=count, platforms=platform_list)
    filepath = save_responses(responses)
    mentions = sum(1 for r in responses if r.get("response", {}).get("mentions_apollo_cash", False))
    return json.dumps({
        "status": "success",
        "count": len(responses),
        "file": filepath,
        "apollo_mentions": mentions,
        "preview": responses[:2] if len(responses) > 2 else responses,
    }, indent=2, ensure_ascii=False)


def _discover_threads() -> str:
    """Run thread discovery across target communities."""
    discovery = generate_thread_discovery()
    output_dir = Path("output/community")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "thread_discovery.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(discovery, f, indent=2, ensure_ascii=False)
    return json.dumps({
        "status": "success",
        "file": str(path),
        "total_discovered": discovery.get("total_discovered", 0),
        "actionable": discovery.get("daily_stats", {}).get("actionable", 0),
    }, indent=2, ensure_ascii=False)


def _list_audience_segments() -> str:
    """List all target audience segments and their details."""
    return json.dumps(AUDIENCE_SEGMENTS, indent=2, ensure_ascii=False)


def _list_seo_keywords() -> str:
    """List all target SEO keywords by category."""
    return json.dumps(SEO_KEYWORDS, indent=2, ensure_ascii=False)


def _list_communities() -> str:
    """List all target communities for distribution."""
    return json.dumps(COMMUNITY_TARGETS, indent=2, ensure_ascii=False)


def _research_trends() -> str:
    """Research trending topics and content opportunities."""
    trends = research_trending_topics()
    filepath = save_research(trends, "trending_topics")
    return json.dumps({
        "status": "success",
        "file": filepath,
        "top_5_ideas": trends.get("top_5_content_ideas", []),
        "trending_hashtags": trends.get("trending_hashtags", []),
    }, indent=2, ensure_ascii=False)


def _research_sentiment(audience_segment: str = "gig_workers") -> str:
    """Research audience sentiment for a specific segment."""
    sentiment = research_audience_sentiment(audience_segment)
    filepath = save_research(sentiment, f"sentiment_{audience_segment}")
    return json.dumps({
        "status": "success",
        "segment": audience_segment,
        "file": filepath,
        "content_recommendations": sentiment.get("content_recommendations", []),
        "trust_factors": sentiment.get("trust_factors", []),
    }, indent=2, ensure_ascii=False)


def _adapt_strategy(engagement_summary: str = "") -> str:
    """Analyze engagement and recommend strategy adjustments."""
    try:
        engagement_data = json.loads(engagement_summary) if engagement_summary else {}
    except json.JSONDecodeError:
        engagement_data = {"raw_input": engagement_summary}
    adaptation = analyze_engagement_and_adapt(engagement_data)
    filepath = save_research(adaptation, "engagement_adaptation")
    return json.dumps({
        "status": "success",
        "file": filepath,
        "do_more": adaptation.get("do_more", []),
        "stop_doing": adaptation.get("stop_doing", []),
        "next_week_strategy": adaptation.get("next_week_strategy", ""),
    }, indent=2, ensure_ascii=False)


def _read_output_file(filepath: str = "") -> str:
    """Read a generated output file."""
    path = Path(filepath)
    if not path.exists():
        return json.dumps({"error": f"File not found: {filepath}"})
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Truncate if too long
    if len(content) > 8000:
        content = content[:8000] + "\n\n... [truncated]"
    return content


# ── Tool Registry ──────────────────────────────────────────────

TOOL_REGISTRY: list[ToolDefinition] = [
    ToolDefinition(
        name="generate_social_posts",
        description="Generate social media posts for Apollo Cash. Creates Hinglish content across formats (carousels, reels, memes, etc.) for different audience segments.",
        parameters={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of posts to generate (1-10)", "default": 5},
                "audience_segment": {
                    "type": "string",
                    "enum": ["gig_workers", "salaried_tier2", "self_employed", "ntc_youth"],
                    "description": "Target audience segment",
                    "default": "gig_workers",
                },
                "formats": {
                    "type": "string",
                    "description": "Comma-separated content formats: instagram_carousel, reel_script, facebook_post, whatsapp_broadcast, twitter_thread, meme, youtube_short_script",
                    "default": "instagram_carousel,reel_script,facebook_post,meme",
                },
                "themes": {
                    "type": "string",
                    "description": "Comma-separated content themes/scenarios",
                    "default": "salary delay,bike repair,festival season,medical emergency",
                },
            },
            "required": [],
        },
        handler=_generate_social_posts,
    ),
    ToolDefinition(
        name="generate_content_variations",
        description="Generate multiple content variations of the same scenario across different formats and angles. Useful for A/B testing and content diversity.",
        parameters={
            "type": "object",
            "properties": {
                "scenario": {"type": "string", "description": "The base scenario to create variations of"},
                "num_variations": {"type": "integer", "description": "Number of variations (2-5)", "default": 3},
            },
            "required": ["scenario"],
        },
        handler=_generate_variations,
    ),
    ToolDefinition(
        name="generate_weekly_calendar",
        description="Generate a complete 7-day content calendar with posts scheduled for optimal times across all platforms and audience segments.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_generate_calendar,
    ),
    ToolDefinition(
        name="generate_seo_article",
        description="Generate a full SEO-optimized blog article targeting a specific keyword. Includes meta tags, proper heading structure, FAQs, and CTAs.",
        parameters={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Primary SEO keyword to target"},
                "language": {"type": "string", "enum": ["english", "hinglish"], "default": "hinglish"},
                "audience_segment": {
                    "type": "string",
                    "enum": ["gig_workers", "salaried_tier2", "self_employed", "ntc_youth"],
                    "default": "ntc_youth",
                },
                "article_type": {
                    "type": "string",
                    "enum": ["educational", "problem_solving", "myth_busting", "comparison", "audience_specific", "use_case_landing"],
                    "default": "educational",
                },
            },
            "required": ["keyword"],
        },
        handler=_generate_seo_article,
    ),
    ToolDefinition(
        name="keyword_analysis",
        description="Analyze and prioritize all SEO keywords for Apollo Cash content strategy. Returns priority scores, competition levels, and content recommendations.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_keyword_analysis,
    ),
    ToolDefinition(
        name="generate_community_responses",
        description="Generate authentic community responses for simulated threads across Reddit, Quora, Twitter, and Facebook groups. Responses are helpful-first, not promotional.",
        parameters={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of responses (1-12)", "default": 5},
                "platforms": {
                    "type": "string",
                    "description": "Comma-separated platforms: reddit, quora, twitter, facebook_group",
                    "default": "reddit,quora,twitter,facebook_group",
                },
            },
            "required": [],
        },
        handler=_generate_community_responses,
    ),
    ToolDefinition(
        name="discover_threads",
        description="Run daily thread discovery across target communities. Finds relevant conversations about loans, money problems, and financial stress.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_discover_threads,
    ),
    ToolDefinition(
        name="list_audience_segments",
        description="List all target audience segments with their demographics, pain points, and platform preferences.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_list_audience_segments,
    ),
    ToolDefinition(
        name="list_seo_keywords",
        description="List all target SEO keywords organized by category (high-intent, informational, long-tail).",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_list_seo_keywords,
    ),
    ToolDefinition(
        name="list_communities",
        description="List all target communities for distribution with their keywords and monitoring criteria.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_list_communities,
    ),
    ToolDefinition(
        name="research_trends",
        description="Research trending topics, viral formats, competitor strategies, and content opportunities for Apollo Cash's target audience. Use this before generating content to ensure relevance.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=_research_trends,
    ),
    ToolDefinition(
        name="research_audience_sentiment",
        description="Deep-dive into what a specific audience segment is talking about online — their language, fears, trust factors, and shareable content types.",
        parameters={
            "type": "object",
            "properties": {
                "audience_segment": {
                    "type": "string",
                    "enum": ["gig_workers", "salaried_tier2", "self_employed", "ntc_youth"],
                    "description": "Which audience segment to research",
                    "default": "gig_workers",
                },
            },
            "required": [],
        },
        handler=_research_sentiment,
    ),
    ToolDefinition(
        name="adapt_strategy",
        description="Analyze engagement metrics and recommend content strategy adjustments. Tell the agent what to do more/less of based on performance data.",
        parameters={
            "type": "object",
            "properties": {
                "engagement_summary": {
                    "type": "string",
                    "description": "JSON string of engagement metrics to analyze",
                    "default": "",
                },
            },
            "required": [],
        },
        handler=_adapt_strategy,
    ),
    ToolDefinition(
        name="read_output",
        description="Read a previously generated output file (JSON or Markdown).",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the output file to read"},
            },
            "required": ["filepath"],
        },
        handler=_read_output_file,
    ),
]


def get_tool_schemas() -> list[dict]:
    """Return JSON schemas for all tools (for LLM function calling)."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
        }
        for t in TOOL_REGISTRY
    ]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool by name with given arguments."""
    for tool in TOOL_REGISTRY:
        if tool.name == name:
            try:
                return tool.handler(**arguments)
            except Exception as e:
                return json.dumps({"error": str(e), "tool": name})
    return json.dumps({"error": f"Unknown tool: {name}"})
