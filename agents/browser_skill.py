"""
Browser Use Skill — Real web browsing for agents.

Uses browser-use (https://github.com/browser-use/browser-use) with Playwright
to give agents the ability to browse the real web: read Reddit threads, Quora
answers, competitor Instagram, and any JS-heavy page.

Runs headless Chromium via Playwright on Railway.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "browser"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_browser_available = False

try:
    from browser_use import Agent as BrowserAgent
    from langchain_openai import ChatOpenAI
    _browser_available = True
    print("[BROWSER-USE] Available")
except ImportError:
    print("[BROWSER-USE] Not installed — using fallback scraping")


def _get_llm():
    """Get LLM for browser-use agent. Uses Cerebras via OpenAI-compatible API."""
    api_key = os.environ.get("CEREBRAS_API_KEY", "")
    return ChatOpenAI(
        model="qwen-3-235b-a22b-instruct-2507",
        base_url="https://api.cerebras.ai/v1",
        api_key=api_key,
        temperature=0.3,
    )


async def browse(task: str, url: str = "") -> dict:
    """Run a browser-use agent to complete a web task.

    Args:
        task: Natural language description of what to do
        url: Optional starting URL

    Returns:
        dict with status, result, and optional file path
    """
    if not _browser_available:
        return {"status": "unavailable", "message": "browser-use not installed"}

    try:
        full_task = task
        if url:
            full_task = f"Go to {url}. Then: {task}"

        agent = BrowserAgent(
            task=full_task,
            llm=_get_llm(),
        )
        result = await agent.run()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = OUTPUT_DIR / f"browse_{timestamp}.json"
        with open(filepath, "w") as f:
            json.dump({
                "task": task,
                "url": url,
                "result": str(result),
                "timestamp": timestamp,
            }, f, indent=2)

        return {"status": "success", "result": str(result), "file": str(filepath)}

    except Exception as e:
        return {"status": "error", "message": str(e)[:500]}


async def browse_reddit(subreddit: str, keywords: str = "loan emergency salary", limit: int = 5) -> list[dict]:
    """Browse a subreddit using a real browser and extract posts."""
    if not _browser_available:
        return [{"error": "browser-use not available"}]

    task = f"""
    Go to https://www.reddit.com/r/{subreddit}/
    Find the {limit} most recent posts that mention any of these keywords: {keywords}
    For each post, extract:
    - title (exact text)
    - body text (first 200 characters)
    - number of comments
    - number of upvotes
    - author username
    Return ONLY a JSON array with these fields: title, body, num_comments, score, author
    """
    result = await browse(task)
    if result.get("status") == "success":
        try:
            return json.loads(result["result"])
        except (json.JSONDecodeError, TypeError):
            return [{"title": "Browser result", "body": result["result"][:500], "source": "browser-use"}]
    return [{"error": result.get("message", "Unknown error")}]


async def browse_quora(query: str, limit: int = 5) -> list[dict]:
    """Browse Quora and extract question + answer pairs."""
    if not _browser_available:
        return [{"error": "browser-use not available"}]

    task = f"""
    Go to https://www.quora.com/search?q={query.replace(' ', '+')}
    Find the top {limit} questions related to "{query}".
    For each question, extract:
    - question title
    - top answer preview (first 200 characters)
    - number of answers
    Return ONLY a JSON array with fields: question, answer_preview, num_answers
    """
    result = await browse(task)
    if result.get("status") == "success":
        try:
            return json.loads(result["result"])
        except (json.JSONDecodeError, TypeError):
            return [{"question": query, "answer_preview": result["result"][:500], "source": "browser-use"}]
    return [{"error": result.get("message", "Unknown error")}]


async def browse_instagram(handle: str, post_count: int = 5) -> list[dict]:
    """Browse a public Instagram profile and analyze recent posts."""
    if not _browser_available:
        return [{"error": "browser-use not available"}]

    task = f"""
    Go to https://www.instagram.com/{handle}/
    Look at their {post_count} most recent posts.
    For each post, extract:
    - caption text (first 150 characters)
    - number of likes (approximate)
    - number of comments
    - post type (photo, video, or carousel)
    Return ONLY a JSON array with fields: caption, likes, comments, type
    """
    result = await browse(task)
    if result.get("status") == "success":
        try:
            return json.loads(result["result"])
        except (json.JSONDecodeError, TypeError):
            return [{"caption": result["result"][:500], "source": "browser-use"}]
    return [{"error": result.get("message", "Unknown error")}]


async def browse_page(url: str, extract: str = "main content") -> dict:
    """Browse any URL and extract specified content."""
    if not _browser_available:
        return {"error": "browser-use not available"}

    task = f"Go to {url}. Extract: {extract}. Return the extracted text."
    return await browse(task, url)
