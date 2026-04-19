"""Agent 1: Social Media Content Engine for Apollo Cash."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from agents.llm_client import generate_json
from agents.prompts import SOCIAL_MEDIA_SYSTEM, SOCIAL_MEDIA_USER_TEMPLATE
from config.settings import AUDIENCE_SEGMENTS, CONTENT_FORMATS, POSTING_SCHEDULE

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "social_media"


def generate_posts(
    count: int = 5,
    formats: list[str] | None = None,
    audience_segment: str = "gig_workers",
    themes: list[str] | None = None,
    language: str = "english",
) -> list[dict]:
    """Generate a batch of social media posts."""
    if formats is None:
        formats = ["instagram_carousel", "reel_script", "facebook_post", "meme", "twitter_thread"]
    if themes is None:
        themes = [
            "salary delay emergency",
            "bike/phone repair",
            "festival season cash crunch",
            "medical emergency",
            "month-end struggle",
            "first time loan experience",
            "small shop restocking",
        ]

    segment_info = AUDIENCE_SEGMENTS.get(audience_segment, AUDIENCE_SEGMENTS["gig_workers"])
    prompt = SOCIAL_MEDIA_USER_TEMPLATE.format(
        count=count,
        language=language,
        formats=", ".join(formats),
        audience_segment=f"{segment_info['label']} — {segment_info['description']}",
        themes=", ".join(themes),
    )

    posts = generate_json(SOCIAL_MEDIA_SYSTEM, prompt)
    return posts


def generate_content_variations(base_scenario: str, num_variations: int = 3) -> list[dict]:
    """Generate multiple content variations of the same scenario across formats."""
    variation_prompt = f"""
Take this scenario and create {num_variations} completely different content pieces,
each in a different format and with a different angle/voice:

Scenario: {base_scenario}

Formats to use: instagram_carousel, reel_script, meme

Return a JSON array where each item has:
{{
  "format": "the format used",
  "platform": "target platform",
  "angle": "the unique angle/perspective",
  "content": {{format-specific content structure}},
  "hashtags": ["#tag1", "#tag2"],
  "why_this_works": "brief explanation of the creative choice"
}}

Return ONLY the JSON array.
"""
    return generate_json(SOCIAL_MEDIA_SYSTEM, variation_prompt)


def generate_weekly_calendar(week_start: str | None = None) -> dict:
    """Generate a full week's content calendar with posts for each slot."""
    if week_start is None:
        today = datetime.now()
        # Start from next Monday
        days_ahead = 7 - today.weekday()
        if days_ahead == 7:
            days_ahead = 0
        monday = today + timedelta(days=days_ahead)
        week_start = monday.strftime("%Y-%m-%d")

    calendar_prompt = f"""
Generate a complete 7-day content calendar for Apollo Cash starting {week_start}.

For each day, generate 2 content pieces following this schedule structure:
{json.dumps(POSTING_SCHEDULE, indent=2)}

Rotate through ALL audience segments across the week:
- Monday/Tuesday: Gig Workers focus
- Wednesday/Thursday: Salaried Tier 2/3 focus
- Friday/Saturday: Self-Employed focus
- Sunday: NTC Youth focus

Return a JSON object:
{{
  "week_start": "{week_start}",
  "week_end": "calculated end date",
  "total_posts": number,
  "calendar": {{
    "monday": [{{post objects with full content}}],
    "tuesday": [...],
    ...
  }},
  "weekly_themes": ["theme 1", "theme 2", "theme 3"],
  "audience_rotation": {{"monday": "segment", ...}}
}}

Each post in the calendar should have:
{{
  "scheduled_time": "HH:MM",
  "platform": "...",
  "format": "...",
  "audience_segment": "...",
  "theme": "...",
  "content": {{format-specific content}},
  "hashtags": [...],
  "engagement_hook": "..."
}}

Return ONLY the JSON object.
"""
    return generate_json(SOCIAL_MEDIA_SYSTEM, calendar_prompt, max_tokens=8000)


def save_posts(posts: list[dict], filename: str | None = None) -> str:
    """Save generated posts to a JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"posts_{timestamp}.json"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    return str(filepath)


def run_full_pipeline(total_posts: int = 18) -> dict:
    """Run the complete social media content generation pipeline."""
    all_posts = []
    segments = list(AUDIENCE_SEGMENTS.keys())
    posts_per_segment = max(1, total_posts // len(segments))

    for segment in segments:
        posts = generate_posts(
            count=posts_per_segment,
            audience_segment=segment,
        )
        all_posts.extend(posts)

    # Save all posts
    filepath = save_posts(all_posts, "all_posts.json")

    # Generate weekly calendar
    calendar = generate_weekly_calendar()
    cal_path = OUTPUT_DIR / "weekly_calendar.json"
    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)

    return {
        "total_posts": len(all_posts),
        "posts_file": filepath,
        "calendar_file": str(cal_path),
        "segments_covered": segments,
        "posts": all_posts,
        "calendar": calendar,
    }
