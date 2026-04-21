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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# Multiple Reddit endpoints to try (fallback chain including proxy)
REDDIT_URLS = [
    "https://www.reddit.com/r/{sub}/{sort}.json?limit={limit}&raw_json=1",
    "https://old.reddit.com/r/{sub}/{sort}.json?limit={limit}",
    "https://api.reddit.com/r/{sub}/{sort}?limit={limit}",
    "https://www.reddit.com/r/{sub}/search.json?q=loan+emergency&restrict_sr=1&sort=new&limit={limit}&raw_json=1",
]

# Pullpush.io is a free Reddit archive API — works when Reddit blocks direct access
PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/?subreddit={sub}&size={limit}&sort=desc&sort_type=created_utc"


# ── Reddit (free JSON API with fallback) ────────────────────────

def scrape_reddit(subreddit: str, limit: int = 10, sort: str = "hot") -> list[dict]:
    """Fetch real posts from a subreddit. Tries multiple Reddit endpoints as fallback."""
    last_error = ""
    for url_template in REDDIT_URLS:
        url = url_template.format(sub=subreddit, sort=sort, limit=limit)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            if resp.status_code in (403, 429, 503):
                last_error = f"{resp.status_code} from {url.split('/r/')[0]}"
                continue
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
            if posts:
                return posts
        except Exception as e:
            last_error = str(e)
            continue
    # Fallback: try Pullpush.io (free Reddit archive API)
    try:
        pp_url = PULLPUSH_URL.format(sub=subreddit, limit=limit)
        resp = requests.get(pp_url, headers={"User-Agent": "AgentBlaze/1.0"}, timeout=15)
        if resp.ok:
            items = resp.json().get("data", [])
            posts = []
            for item in items[:limit]:
                posts.append({
                    "title": item.get("title", ""),
                    "body": (item.get("selftext", "") or "")[:500],
                    "author": item.get("author", ""),
                    "score": item.get("score", 0),
                    "num_comments": item.get("num_comments", 0),
                    "url": f"https://reddit.com/r/{subreddit}/comments/{item.get('id', '')}",
                    "created": datetime.fromtimestamp(item.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M"),
                    "subreddit": subreddit,
                    "source": "pullpush",
                })
            if posts:
                return posts
    except Exception:
        pass

    return [{"error": f"All Reddit endpoints blocked. Last error: {last_error}", "subreddit": subreddit}]


def search_reddit(query: str, subreddit: str = "", limit: int = 10) -> list[dict]:
    """Search Reddit for posts matching a query. Tries multiple endpoints."""
    sub_part = f"r/{subreddit}/" if subreddit else ""
    q = requests.utils.quote(query)
    urls = [
        f"https://old.reddit.com/{sub_part}search.json?q={q}&limit={limit}&sort=relevance&t=month",
        f"https://www.reddit.com/{sub_part}search.json?q={q}&limit={limit}&sort=relevance&t=month",
        f"https://api.reddit.com/{sub_part}search?q={q}&limit={limit}&sort=relevance&t=month",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            if resp.status_code in (403, 429, 503):
                continue
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
            if posts:
                return posts
        except Exception:
            continue
    return [{"error": "All Reddit endpoints blocked"}]


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

def _pullpush_search(query: str, subreddit: str = "", limit: int = 5) -> list[dict]:
    """Search Reddit via Pullpush.io (works when Reddit blocks direct access)."""
    try:
        params = f"q={requests.utils.quote(query)}&size={limit}&sort=desc&sort_type=created_utc"
        if subreddit:
            params += f"&subreddit={subreddit}"
        url = f"https://api.pullpush.io/reddit/search/submission/?{params}"
        resp = requests.get(url, headers={"User-Agent": "AgentBlaze/1.0"}, timeout=15)
        if resp.ok:
            items = resp.json().get("data", [])
            return [{
                "title": item.get("title", ""),
                "body": (item.get("selftext", "") or "")[:500],
                "author": item.get("author", ""),
                "score": item.get("score", 0),
                "num_comments": item.get("num_comments", 0),
                "subreddit": item.get("subreddit", subreddit),
                "url": f"https://reddit.com/r/{item.get('subreddit','')}/comments/{item.get('id','')}",
                "source": "pullpush",
            } for item in items]
    except Exception:
        pass
    return []


def research_live(topic: str = "personal loan India") -> dict:
    """Run a full live research sweep — Reddit (via Pullpush) + Google Trends."""
    results = {}

    # Reddit: search across finance subreddits using Pullpush (bypasses Reddit blocks)
    subreddits = ["personalfinanceindia", "IndiaInvestments", "india"]
    all_reddit_posts = []
    for sub in subreddits:
        # Try Pullpush first (reliable), then regular search as fallback
        posts = _pullpush_search(topic, subreddit=sub, limit=5)
        if not posts:
            posts = search_reddit(topic, subreddit=sub, limit=5)
        all_reddit_posts.extend([p for p in posts if "error" not in p])

    results["reddit"] = {
        "query": topic,
        "total_posts": len(all_reddit_posts),
        "posts": all_reddit_posts[:15],
    }

    # Hacker News — top stories related to fintech/India
    try:
        hn_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        if hn_resp.ok:
            story_ids = hn_resp.json()[:30]
            hn_posts = []
            for sid in story_ids[:30]:
                try:
                    s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
                    title = s.get("title", "").lower()
                    if any(kw in title for kw in ["fintech", "india", "loan", "credit", "gig", "payment", "upi", "lending", "banking", "salary"]):
                        hn_posts.append({
                            "title": s.get("title", ""),
                            "url": s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                            "score": s.get("score", 0),
                            "comments": s.get("descendants", 0),
                            "source": "hackernews",
                        })
                except Exception:
                    continue
            if hn_posts:
                results["hackernews"] = {"posts": hn_posts[:5], "total": len(hn_posts)}
    except Exception:
        pass

    # YouTube Trending — search for relevant finance content (no API key, scrape search)
    try:
        yt_query = requests.utils.quote(f"{topic} India")
        yt_resp = requests.get(
            f"https://www.youtube.com/results?search_query={yt_query}&sp=CAI%253D",
            headers=HEADERS, timeout=10
        )
        if yt_resp.ok:
            import re
            video_titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', yt_resp.text)
            video_ids = re.findall(r'"videoId":"([^"]+)"', yt_resp.text)
            yt_results = []
            seen = set()
            for title, vid in zip(video_titles, video_ids):
                if vid not in seen and len(yt_results) < 5:
                    seen.add(vid)
                    yt_results.append({"title": title, "video_id": vid, "url": f"https://youtube.com/watch?v={vid}", "source": "youtube"})
            if yt_results:
                results["youtube"] = {"videos": yt_results, "query": topic}
    except Exception:
        pass

    # Twitter/X Trends — scrape trending topics for India (no API needed)
    try:
        # Use an unofficial trends endpoint
        trends_resp = requests.get(
            "https://trends24.in/india/",
            headers=HEADERS, timeout=10
        )
        if trends_resp.ok:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(trends_resp.text, "html.parser")
            trend_cards = soup.select("li a.trend-link")
            x_trends = [{"topic": t.get_text(strip=True), "source": "x_trends"} for t in trend_cards[:10]]
            if x_trends:
                results["x_trends"] = {"trends": x_trends, "region": "India"}
    except Exception:
        pass

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
        posts = _pullpush_search(kw, limit=5)
        if not posts:
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
