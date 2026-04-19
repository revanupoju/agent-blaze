"""
Browser Use Skill — Real-time community reading and trend research.

Uses browser-use (https://github.com/browser-use/browser-use) to give agents
the ability to browse the real web: read Reddit threads, Quora questions,
Twitter conversations, and Google Trends.

Requirements: Python 3.11+, browser-use package
Install: uv add browser-use

This skill connects to the Community Agent and Research Agent,
enabling them to find and read real conversations instead of
generating simulated ones.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "browser"


# ── Skill definitions (for the harness tool registry) ───────────

BROWSER_SKILLS = [
    {
        "name": "browse_reddit",
        "description": "Browse a subreddit and find recent posts matching keywords. Returns post titles, bodies, and comment counts.",
        "parameters": {
            "type": "object",
            "properties": {
                "subreddit": {"type": "string", "description": "Subreddit name (e.g., 'personalfinanceindia')"},
                "keywords": {"type": "string", "description": "Comma-separated keywords to search for"},
                "limit": {"type": "integer", "description": "Max posts to return", "default": 5},
            },
            "required": ["subreddit"],
        },
    },
    {
        "name": "browse_quora",
        "description": "Search Quora for questions matching a topic. Returns question titles and top answer previews.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for Quora"},
                "limit": {"type": "integer", "description": "Max questions to return", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "browse_twitter_search",
        "description": "Search Twitter/X for recent tweets matching keywords. Returns tweet text, author, and engagement counts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for Twitter"},
                "limit": {"type": "integer", "description": "Max tweets to return", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "browse_google_trends",
        "description": "Check Google Trends for a keyword in India. Returns trend data and related queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Keyword to check trends for"},
                "region": {"type": "string", "description": "Region code", "default": "IN"},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "browse_competitor_instagram",
        "description": "Browse a competitor's Instagram profile and analyze their recent posts, engagement, and content strategy.",
        "parameters": {
            "type": "object",
            "properties": {
                "handle": {"type": "string", "description": "Instagram handle (e.g., 'slicepayin')"},
                "post_count": {"type": "integer", "description": "Number of recent posts to analyze", "default": 5},
            },
            "required": ["handle"],
        },
    },
]


async def execute_browser_skill(skill_name: str, params: dict) -> str:
    """Execute a browser skill using browser-use.

    Requires Python 3.11+ and browser-use installed.
    Falls back to simulated results if browser-use is not available.
    """
    try:
        from browser_use import Agent, Browser
        from browser_use import ChatBrowserUse

        browser = Browser()

        if skill_name == "browse_reddit":
            task = f"""
            Go to https://www.reddit.com/r/{params['subreddit']}/
            Find the {params.get('limit', 5)} most recent posts that mention
            any of these keywords: {params.get('keywords', 'loan money emergency')}
            For each post, extract: title, body text (first 200 chars), comment count, upvotes
            Return the results as a JSON array.
            """
        elif skill_name == "browse_quora":
            task = f"""
            Go to https://www.quora.com/search?q={params['query'].replace(' ', '+')}
            Find the top {params.get('limit', 5)} questions.
            For each question, extract: question title, top answer preview (first 200 chars)
            Return the results as a JSON array.
            """
        elif skill_name == "browse_twitter_search":
            task = f"""
            Go to https://twitter.com/search?q={params['query'].replace(' ', '%20')}&f=live
            Find the {params.get('limit', 10)} most recent relevant tweets.
            For each tweet, extract: author handle, tweet text, likes, retweets
            Return the results as a JSON array.
            """
        elif skill_name == "browse_google_trends":
            task = f"""
            Go to https://trends.google.com/trends/explore?q={params['keyword'].replace(' ', '%20')}&geo={params.get('region', 'IN')}
            Extract: interest over time trend, related queries, related topics
            Return as a JSON object.
            """
        elif skill_name == "browse_competitor_instagram":
            task = f"""
            Go to https://www.instagram.com/{params['handle']}/
            Analyze their {params.get('post_count', 5)} most recent posts.
            For each post, extract: caption preview, likes count, comments count, post type (photo/video/carousel)
            Return as a JSON array.
            """
        else:
            return json.dumps({"error": f"Unknown skill: {skill_name}"})

        agent = Agent(task=task, llm=ChatBrowserUse())
        result = await agent.run()

        # Save results
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = OUTPUT_DIR / f"{skill_name}_{timestamp}.json"
        with open(filepath, "w") as f:
            json.dump({"skill": skill_name, "params": params, "result": result, "timestamp": timestamp}, f, indent=2)

        return json.dumps({"status": "success", "result": result, "file": str(filepath)})

    except ImportError:
        return json.dumps({
            "status": "fallback",
            "message": "browser-use not available (requires Python 3.11+). Using simulated results.",
            "skill": skill_name,
            "params": params,
        })
