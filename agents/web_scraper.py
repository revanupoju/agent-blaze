"""
Real web scraping for Agent Blaze — no API keys needed.

Reddit JSON API + pytrends + requests/BeautifulSoup
All free, all open source.
"""

from __future__ import annotations

import json
import requests
from datetime import datetime
from typing import Any

HEADERS = {
    "User-Agent": "AgentBlaze/1.0 (Marketing Research Bot; contact: demo@apollofinvest.com)"
}


# ── Reddit (free JSON API) ──────────────────────────────────────

def scrape_reddit(subreddit: str, limit: int = 10, sort: str = "hot") -> list[dict]:
    """Fetch real posts from a subreddit using Reddit's JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "body": (post.get("selftext", "") or "")[:500],
                "author": post.get("author", ""),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "created": datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M"),
                "subreddit": subreddit,
            })
        return posts
    except Exception as e:
        return [{"error": str(e), "subreddit": subreddit}]


def search_reddit(query: str, subreddit: str = "", limit: int = 10) -> list[dict]:
    """Search Reddit for posts matching a query."""
    sub_part = f"r/{subreddit}/" if subreddit else ""
    url = f"https://www.reddit.com/{sub_part}search.json?q={requests.utils.quote(query)}&limit={limit}&sort=relevance&t=month"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "body": (post.get("selftext", "") or "")[:500],
                "author": post.get("author", ""),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "subreddit": post.get("subreddit", ""),
                "url": f"https://reddit.com{post.get('permalink', '')}",
            })
        return posts
    except Exception as e:
        return [{"error": str(e)}]


# ── Google Trends (pytrends — no API key) ───────────────────────

def get_google_trends(keywords: list[str], region: str = "IN") -> dict:
    """Get Google Trends data for keywords in India."""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload(keywords[:5], cat=0, timeframe="now 7-d", geo=region)

        # Interest over time
        interest = pytrends.interest_over_time()
        trend_data = {}
        if not interest.empty:
            for kw in keywords[:5]:
                if kw in interest.columns:
                    values = interest[kw].tolist()[-7:]
                    trend_data[kw] = {
                        "current": values[-1] if values else 0,
                        "trend": "rising" if len(values) >= 2 and values[-1] > values[0] else "declining",
                        "last_7_values": values,
                    }

        # Related queries
        related = {}
        try:
            related_queries = pytrends.related_queries()
            for kw in keywords[:5]:
                if kw in related_queries:
                    top = related_queries[kw].get("top")
                    rising = related_queries[kw].get("rising")
                    related[kw] = {
                        "top_queries": top["query"].tolist()[:5] if top is not None and not top.empty else [],
                        "rising_queries": rising["query"].tolist()[:5] if rising is not None and not rising.empty else [],
                    }
        except Exception:
            pass

        return {
            "region": region,
            "keywords": keywords,
            "trends": trend_data,
            "related_queries": related,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "keywords": keywords}


# ── General web scraping (requests + BeautifulSoup) ─────────────

def scrape_page(url: str) -> dict:
    """Scrape a web page and extract text content."""
    try:
        from bs4 import BeautifulSoup
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        title = soup.title.string if soup.title else ""
        text = soup.get_text(separator="\n", strip=True)
        # Truncate
        text = text[:3000]

        return {"url": url, "title": title, "text": text, "status": "success"}
    except Exception as e:
        return {"url": url, "error": str(e), "status": "error"}


# ── Combined research function (what Freq uses) ────────────────

def research_live(topic: str = "personal loan India") -> dict:
    """Run a full live research sweep — Reddit + Google Trends."""
    results = {}

    # Reddit: search across finance subreddits
    subreddits = ["personalfinanceindia", "IndiaInvestments", "india"]
    all_reddit_posts = []
    for sub in subreddits:
        posts = search_reddit(topic, subreddit=sub, limit=5)
        all_reddit_posts.extend([p for p in posts if "error" not in p])

    results["reddit"] = {
        "query": topic,
        "total_posts": len(all_reddit_posts),
        "posts": all_reddit_posts[:15],
    }

    # Google Trends
    keywords = [topic]
    if "loan" in topic.lower():
        keywords.extend(["instant loan app", "personal loan", "loan without CIBIL"])
    elif "gig" in topic.lower():
        keywords.extend(["gig worker salary", "delivery partner income"])
    else:
        keywords.extend(["personal finance India", "money problems India"])

    results["google_trends"] = get_google_trends(keywords[:5])

    results["timestamp"] = datetime.now().isoformat()
    results["source"] = "live_web_scraping"

    return results


# ── Community thread discovery (what Rally uses) ────────────────

def discover_threads(keywords: list[str] | None = None) -> dict:
    """Find real threads across Reddit about money/loan problems."""
    if keywords is None:
        keywords = [
            "need money urgently",
            "salary delayed",
            "emergency loan",
            "personal loan app",
            "medical emergency money",
            "bike repair cost",
        ]

    all_threads = []
    for kw in keywords[:4]:
        posts = search_reddit(kw, limit=5)
        for p in posts:
            if "error" not in p and p.get("title"):
                p["search_keyword"] = kw
                p["relevance"] = "high" if p.get("num_comments", 0) > 5 else "medium"
                all_threads.append(p)

    # Deduplicate by title
    seen = set()
    unique = []
    for t in all_threads:
        if t["title"] not in seen:
            seen.add(t["title"])
            unique.append(t)

    return {
        "discovered": len(unique),
        "threads": unique[:20],
        "keywords_searched": keywords[:4],
        "timestamp": datetime.now().isoformat(),
        "source": "reddit_live",
    }
