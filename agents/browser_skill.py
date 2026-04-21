"""
Browser Skill — Real web browsing via Browserbase (cloud Chrome).

Uses Playwright + Browserbase to browse JS-heavy pages that JSON APIs can't reach.
No local Chrome needed — runs in the cloud.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "browser"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY", "")

_available = False
try:
    from playwright.async_api import async_playwright
    _available = True
    print("[BROWSER] Playwright available")
except ImportError:
    print("[BROWSER] Playwright not installed")


async def _get_browser():
    """Connect to Browserbase cloud Chrome or local Playwright."""
    p = await async_playwright().start()
    if BROWSERBASE_API_KEY:
        # Browserbase: create session via API, then connect via CDP
        import requests as http_req
        try:
            resp = http_req.post(
                "https://api.browserbase.com/v1/sessions",
                headers={"x-bb-api-key": BROWSERBASE_API_KEY, "Content-Type": "application/json"},
                json={
                    "browserSettings": {
                        "blockAds": True,
                        "solveCaptchas": True,
                    },
                    "proxies": True,
                },
                timeout=15
            )
            if resp.ok:
                session = resp.json()
                connect_url = f"wss://connect.browserbase.com?apiKey={BROWSERBASE_API_KEY}&sessionId={session['id']}"
                browser = await p.chromium.connect_over_cdp(connect_url)
                print(f"[BROWSER] Browserbase session: {session['id']}")
                return p, browser
        except Exception as e:
            print(f"[BROWSER] Browserbase error: {e}")

    # Fallback to local
    browser = await p.chromium.launch(headless=True)
    print("[BROWSER] Using local Chromium")
    return p, browser


async def browse(url: str, extract: str = "main content") -> dict:
    """Browse a URL and extract content using Playwright."""
    if not _available:
        return {"status": "unavailable", "message": "Playwright not installed"}

    try:
        p, browser = await _get_browser()
        page = await browser.new_page()
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)  # Wait for JS rendering

        # Extract page content
        title = await page.title()
        content = await page.evaluate("() => document.body.innerText.substring(0, 5000)")

        await browser.close()
        await p.stop()

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = OUTPUT_DIR / f"browse_{timestamp}.json"
        with open(filepath, "w") as f:
            json.dump({"url": url, "title": title, "content": content[:3000], "timestamp": timestamp}, f, indent=2)

        return {"status": "success", "title": title, "content": content[:3000], "file": str(filepath)}

    except Exception as e:
        return {"status": "error", "message": str(e)[:500]}


async def browse_reddit(subreddit: str, limit: int = 5) -> list[dict]:
    """Browse Reddit and extract post titles, scores, comments."""
    if not _available:
        return [{"error": "Playwright not available"}]

    try:
        p, browser = await _get_browser()
        page = await browser.new_page()
        await page.goto(f"https://old.reddit.com/r/{subreddit}/", timeout=30000)
        await page.wait_for_timeout(2000)

        # Extract posts using old.reddit.com structure (simpler HTML)
        posts = await page.evaluate(f"""() => {{
            const entries = document.querySelectorAll('.thing.link');
            const results = [];
            for (let i = 0; i < Math.min(entries.length, {limit}); i++) {{
                const e = entries[i];
                const title = e.querySelector('a.title')?.innerText || '';
                const score = e.querySelector('.score.unvoted')?.innerText || '0';
                const comments = e.querySelector('.comments')?.innerText || '0';
                const author = e.querySelector('.author')?.innerText || '';
                const href = e.querySelector('a.title')?.href || '';
                results.push({{ title, score, comments: comments.split(' ')[0], author, url: href }});
            }}
            return results;
        }}""")

        await browser.close()
        await p.stop()
        return posts

    except Exception as e:
        return [{"error": str(e)[:300]}]


async def browse_instagram(handle: str, limit: int = 5) -> list[dict]:
    """Browse a public Instagram profile and extract recent posts."""
    if not _available:
        return [{"error": "Playwright not available"}]

    try:
        p, browser = await _get_browser()
        page = await browser.new_page()
        await page.goto(f"https://www.instagram.com/{handle}/", timeout=30000)
        await page.wait_for_timeout(3000)

        # Extract post data from the page
        posts = await page.evaluate(f"""() => {{
            const imgs = document.querySelectorAll('article img');
            const results = [];
            for (let i = 0; i < Math.min(imgs.length, {limit}); i++) {{
                results.push({{
                    alt: imgs[i].alt || '',
                    src: imgs[i].src || '',
                    type: 'photo'
                }});
            }}
            return results;
        }}""")

        await browser.close()
        await p.stop()
        return posts

    except Exception as e:
        return [{"error": str(e)[:300]}]


async def browse_quora(query: str, limit: int = 5) -> list[dict]:
    """Search Quora and extract questions + answer previews."""
    if not _available:
        return [{"error": "Playwright not available"}]

    try:
        p, browser = await _get_browser()
        page = await browser.new_page()
        await page.goto(f"https://www.quora.com/search?q={query.replace(' ', '+')}", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.evaluate("() => document.body.innerText.substring(0, 5000)")

        await browser.close()
        await p.stop()
        return [{"query": query, "content": content[:2000], "source": "quora"}]

    except Exception as e:
        return [{"error": str(e)[:300]}]
