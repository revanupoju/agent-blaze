"""
Auto-Publishing Pipeline for Agent Blaze

Handles scheduling and publishing content to social platforms.
Currently supports: simulated posting (logs what would be posted).
Ready for real API integration with:
- Meta Graph API (Instagram/Facebook)
- Twitter API v2
- YouTube Data API
- WhatsApp Business API

Each platform handler follows the same interface:
  publish(content, platform, scheduled_time) → PostResult
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

LOG_DIR = Path(__file__).parent.parent / "output" / "published"


@dataclass
class PostResult:
    platform: str
    status: str  # "published" | "scheduled" | "failed" | "simulated"
    post_id: str
    url: str
    timestamp: str
    content_preview: str


# ── Platform Handlers ───────────────────────────────────────────

def publish_instagram(content: dict) -> PostResult:
    """Publish to Instagram via Meta Graph API.
    Requires: META_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID env vars.
    """
    import os
    token = os.getenv("META_ACCESS_TOKEN")
    ig_id = os.getenv("INSTAGRAM_BUSINESS_ID")

    if token and ig_id:
        # Real Instagram publishing via Meta Graph API
        import requests
        # Step 1: Create media container
        caption = content.get("caption", content.get("text", ""))
        # For carousels, this would be multi-step
        resp = requests.post(
            f"https://graph.facebook.com/v18.0/{ig_id}/media",
            data={"caption": caption, "access_token": token}
        )
        if resp.ok:
            media_id = resp.json().get("id")
            # Step 2: Publish
            pub = requests.post(
                f"https://graph.facebook.com/v18.0/{ig_id}/media_publish",
                data={"creation_id": media_id, "access_token": token}
            )
            return PostResult(
                platform="instagram", status="published",
                post_id=pub.json().get("id", ""), url=f"https://instagram.com/p/{pub.json().get('id','')}",
                timestamp=datetime.now().isoformat(), content_preview=caption[:100]
            )

    # Simulated mode
    return _simulate("instagram", content)


def publish_facebook(content: dict) -> PostResult:
    """Publish to Facebook Page via Graph API."""
    import os
    token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if token and page_id:
        import requests
        text = content.get("text", content.get("caption", ""))
        resp = requests.post(
            f"https://graph.facebook.com/v18.0/{page_id}/feed",
            data={"message": text, "access_token": token}
        )
        if resp.ok:
            return PostResult(
                platform="facebook", status="published",
                post_id=resp.json().get("id", ""), url=f"https://facebook.com/{resp.json().get('id','')}",
                timestamp=datetime.now().isoformat(), content_preview=text[:100]
            )

    return _simulate("facebook", content)


def publish_twitter(content: dict) -> PostResult:
    """Publish to Twitter/X via API v2."""
    import os
    bearer = os.getenv("TWITTER_BEARER_TOKEN")

    if bearer:
        import requests
        text = content.get("text", content.get("caption", ""))[:280]
        resp = requests.post(
            "https://api.twitter.com/2/tweets",
            headers={"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"},
            json={"text": text}
        )
        if resp.ok:
            tweet_id = resp.json().get("data", {}).get("id", "")
            return PostResult(
                platform="twitter", status="published",
                post_id=tweet_id, url=f"https://twitter.com/i/status/{tweet_id}",
                timestamp=datetime.now().isoformat(), content_preview=text[:100]
            )

    return _simulate("twitter", content)


def publish_reddit(content: dict, subreddit: str = "test") -> PostResult:
    """Post to Reddit via API."""
    return _simulate("reddit", content)


def _simulate(platform: str, content: dict) -> PostResult:
    """Log what would be posted (simulation mode)."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    text = content.get("text", content.get("caption", content.get("message", str(content)[:200])))

    result = PostResult(
        platform=platform,
        status="simulated",
        post_id=f"sim_{datetime.now().strftime('%H%M%S')}",
        url=f"https://{platform}.com/simulated",
        timestamp=datetime.now().isoformat(),
        content_preview=text[:100] if isinstance(text, str) else str(text)[:100],
    )

    # Log the simulated post
    log_file = LOG_DIR / "publish_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps({
            "platform": result.platform,
            "status": result.status,
            "post_id": result.post_id,
            "timestamp": result.timestamp,
            "content": text[:500] if isinstance(text, str) else str(text)[:500],
        }) + "\n")

    return result


# ── Batch Publisher ─────────────────────────────────────────────

PLATFORM_HANDLERS = {
    "instagram": publish_instagram,
    "facebook": publish_facebook,
    "twitter": publish_twitter,
    "reddit": publish_reddit,
}


def publish_batch(posts: list[dict]) -> list[PostResult]:
    """Publish a batch of posts to their target platforms."""
    results = []
    for post in posts:
        platform = post.get("platform", "instagram")
        handler = PLATFORM_HANDLERS.get(platform, _simulate)
        content = post.get("content", post)
        result = handler(content)
        results.append(result)
    return results


def get_publish_log() -> list[dict]:
    """Get the publish log."""
    log_file = LOG_DIR / "publish_log.jsonl"
    if not log_file.exists():
        return []
    entries = []
    with open(log_file) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries
