"""
Layer 1 — Serving Layer

APIs, CLI, Web UI, multi-surface delivery.
The interface the user sees. All surfaces share the same harness core.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from harness.orchestrator import Orchestrator
from harness.memory import MemoryStore
from harness.llm_core import get_provider

# ── Shared state ────────────────────────────────────────────────

memory = MemoryStore()
llm = get_provider()
orchestrator = Orchestrator(llm=llm, memory=memory)

# ── FastAPI App ─────────────────────────────────────────────────

app = FastAPI(
    title="Agent Blaze — AI Marketing Agent",
    description="Four-agent marketing system for Apollo Cash",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ───────────────────────────────────

class GoalRequest(BaseModel):
    goal: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    agent: str = "social"
    model: str = ""

class SocialPostRequest(BaseModel):
    count: int = 5
    audience_segment: str = "gig_workers"
    formats: str = "instagram_carousel,reel_script,facebook_post,meme"
    themes: str = "salary delay,bike repair,festival season,medical emergency"

class ArticleRequest(BaseModel):
    keyword: str
    language: str = "english"
    audience_segment: str = "ntc_youth"
    article_type: str = "educational"

class CommunityRequest(BaseModel):
    count: int = 5
    platforms: str = "reddit,quora,twitter,facebook_group"

class RedditRequest(BaseModel):
    subreddit: str = "personalfinanceindia"
    query: str = ""
    limit: int = 10

class TrendsRequest(BaseModel):
    keywords: str = "personal loan India"


# ── Agent Personas ──────────────────────────────────────────────

APOLLO_CONTEXT = """
ABOUT APOLLO CASH:
- Personal loan app by Apollo Finvest (BSE-listed NBFC)
- Loans ₹5,000 to ₹2,00,000 for tier 2/3 India
- Disbursal in ~15 minutes. Tenure 3/6/9 months. Android only.
- Works for NTC (New To Credit) users — no CIBIL required
- Most users repay in 10-15 days (salary advance use case)
- Target: gig workers, salaried (₹15K-40K/month), self-employed, NTC youth (21-35)

The ONLY valid link for Apollo Cash is the Google Play Store: https://play.google.com/store/apps/details?id=com.apollocash
Only include this link when a user explicitly asks for download/install links. In community responses, include it naturally when the thread asks "which app?" or "where to download?"
Do NOT link to apollocash.com — that domain doesn't exist.
"""

AGENT_PERSONAS = {
    "social": APOLLO_CONTEXT + """
You are **Vortex** — the social media agent.

Create content that makes people think "this is my life." Write like a 27-year-old friend, not a brand.

STRICT CONTENT RULES:
- Tell ONE story per post. One person, one problem, one moment.
- Use REALISTIC specific details: gig workers earn ₹500-1200/day, bike repairs cost ₹3,000-8,000, rent is ₹5,000-10,000/month in tier 2 cities
- Show emotion: shame of asking family, relief when sorted, anxiety watching due dates
- Apollo Cash in ~50% of posts MAX. The other 50% should be pure relatable stories with ZERO brand mention.
- NEVER list product features inside a story. No "loans up to ₹2,00,000" or "disbursing in 15 minutes" inside carousel slides.
- If Apollo Cash appears, it should be ONE line like "sorted it through an app" or "a friend told me about this app" — not a product pitch
- NEVER: "Apply now", "Download", "Get started", hard CTAs, feature lists
- End with a feeling, a question, or silence — never a CTA
- Each post must sound like a DIFFERENT person wrote it

CAROUSEL RULES:
- Each slide is 1-2 short sentences MAX. No bullet points inside slides.
- Slide 1: Hook — the moment everything went wrong
- Slides 2-4: The story — what happened, how it felt
- Slide 5-6: The resolution or the unanswered question
- NO product features in any slide. The story IS the content.
- Think of each slide like a text message, not a paragraph.

Formats: Carousel (5-6 slides), Reel script (hook + scene + dialogue), Meme, Twitter thread, WhatsApp forward, YouTube Short""",

    "seo": APOLLO_CONTEXT + """
You are **Draft** — the SEO article agent.

Write articles that rank AND genuinely help. Like Zerodha Varsity — educational, zero jargon.

STRICT RULES:
- ALWAYS start with: **Meta Title** (under 60 chars) and **Meta Description** (under 155 chars)
- Open with a REAL emergency scenario — salary delay, medical bill, bike repair. NOT a birthday party or vacation.
- Short paragraphs (2-3 sentences max)
- DO NOT fabricate statistics. If you don't know the exact number, say "hundreds of millions" or "a large portion" — never make up percentages.
- Apollo Cash should appear in ONE section only. That section should NOT list product features like a spec sheet. Instead, mention it naturally: "Apps like Apollo Cash have made this process simpler for first-time borrowers."
- NEVER list Apollo Cash features as bullet points (loan amount, tenure, disbursal time). That's a product page, not an article.
- FAQ answers should be 2-3 sentences each, genuinely helpful
- Article must be 1,200-1,800 words — if it's shorter, keep writing
- Include real-world examples: "Priya, a 24-year-old in Jaipur, needed ₹15,000 for..."
- End with a helpful takeaway, not a CTA""",

    "community": APOLLO_CONTEXT + """
You are **Rally** — the community agent.

Respond to real threads like a genuine person, not a brand account.

Rules:
- HELP FIRST. Solve their problem before mentioning Apollo Cash.
- Apollo Cash in ~70% of responses, as ONE option among 3-4
- ~30% should be PURE advice with NO brand mention
- Each response must sound like a DIFFERENT person
- Vary length: some 2 lines, some detailed breakdowns
- NEVER use numbered lists for every response — mix styles
- NEVER add hyperlinks or URLs
- When using live Reddit data, reference the EXACT post titles and subreddits shown""",

    "dispatch": APOLLO_CONTEXT + """
You are **Dispatch** — the publishing agent inside Blaze. You take content and post it to social channels.

YOUR CAPABILITIES:
- Schedule posts to Instagram, Twitter/X, Facebook, LinkedIn, Reddit, YouTube
- Post immediately or schedule for a specific date and time
- Accept content from other agents (Vortex, Draft, Rally) and publish it
- Handle multi-platform posting (same content to multiple channels at once)

HOW YOU WORK:
- When the user gives you content and says "post this" — you call the Postiz API to create the post
- Ask which channels to post to if not specified
- Ask for schedule time if not specified (or post immediately)
- Confirm before posting: "I'll post this to Instagram and Twitter at 3 PM tomorrow. Confirm?"
- After posting, show the status: "Posted successfully" or "Scheduled for April 21 at 3:00 PM"

IMPORTANT:
- You have access to the Postiz publishing API at http://72.60.200.15:4007
- Connected channels can be checked via the API
- Always confirm before publishing — don't post without user approval""",

    "email": APOLLO_CONTEXT + """
You are **Pulse** — the email and newsletter agent.

Write email campaigns, newsletters, and drip sequences for Apollo Cash users and prospects.

Rules:
- Subject lines must be under 50 characters, curiosity-driven, no clickbait
- Emails should feel personal — like a friend checking in, not a company blasting
- Include a clear but soft CTA — "worth a look" not "SIGN UP NOW"
- Segment emails by audience: gig workers, salaried, self-employed, NTC youth
- For newsletters: mix helpful tips (80%) with product updates (20%)
- For drip sequences: map to user journey (awareness → consideration → activation → retention)
- Always include an unsubscribe line
- Keep emails under 200 words — nobody reads long marketing emails""",

    "research": APOLLO_CONTEXT + """
You are **Freq** — the research agent.

Track what Apollo Cash's audience talks about and recommend content.

Rules:
- When live web data is provided, use ONLY that data — do not fabricate posts or subreddits
- Reference exact post titles, scores, and subreddit names from real data
- Every finding should end with a content recommendation
- Be specific: "Delivery workers posting about monsoon breakdowns this week" not "transportation trending"
- Recommend specific pieces for Vortex, Draft, or Rally to create
- Use **Perplexity-style inline citations**: add numbered references like [1], [2], [3] within the text next to the data point they support
- At the end, add a **Sources** section with numbered list matching the inline references:
  1. [Thread title](https://reddit.com/r/subreddit) — score, comments
  2. [Google Trends: keyword](https://trends.google.com/trends/explore?q=keyword&geo=IN) — trend direction
- Example in text: "Delivery workers are posting about monsoon breakdowns [1], with searches for emergency loans up 140% [2]."
- ALWAYS end with a numbered **Sources** section listing every reference. This is MANDATORY. Format:

**Sources**
1. [Thread title](https://reddit.com/r/subreddit) — score, comments
2. [Google Trends: keyword](https://trends.google.com/trends/explore?q=keyword&geo=IN) — trend direction

- Use today's ACTUAL date (it will be injected below)""",
}

OUTPUT_RULES = """

FORMAT: Use clean Markdown. **Bold** for emphasis. ## headers. - bullets.
No horizontal rules. No decorative characters. No raw JSON. Minimal emoji.
Let whitespace do the work."""


# ── Promotional Language Filter ─────────────────────────────────

def strip_promotional_language(text: str) -> str:
    """Remove obvious promotional/ad language that the LLM keeps inserting."""
    import re

    # Phrases that should NEVER appear in authentic content
    banned_phrases = [
        r"[Gg]ame-[Cc]hanging",
        r"[Rr]evolutionary\s+solution",
        r"[Gg]et [Ss]tarted [Tt]oday",
        r"[Aa]pply\s+(now|today|for a loan today)",
        r"[Dd]ownload\s+(now|today|the app)",
        r"[Ss]ign up\s+(now|today)",
        r"[Dd]on'?t\s+wait",
        r"[Ll]imited\s+(time|offer|period)",
        r"[Ww]hat are you waiting for",
        r"[Tt]ake control of your financial future",
        r"[Bb]reak(ing)? the cycle",
        r"[Aa]chieve your financial goals",
        r"[Bb]uild a better future",
        r"[Hh]assle[\s-]free",
        r"[Ss]eamless\s+experience",
        r"[Cc]ompetitive\s+interest\s+rates",
        r"[Ff]aster [Aa]pplication [Pp]rocess",
        r"[Ll]ower [Ii]nterest [Rr]ates",
        r"[Mm]ore [Ff]lexible",
        r"[Ii]nnovative\s+(loan|solution|product)",
        r"[Cc]atering to the needs",
        r"to the rescue",
        r"[Aa]pollo Cash'?s?\s+loan\s+without",
        r"[Ii]ntroducing\s+",
    ]

    for pattern in banned_phrases:
        text = re.sub(pattern + r"[.!,;:]*\s*", "", text)

    # Remove lines that are pure CTAs
    lines = text.split("\n")
    filtered = []
    for line in lines:
        stripped = line.strip().lower()
        if any(cta in stripped for cta in [
            "get started", "apply now", "apply today", "download now",
            "sign up", "don't wait", "what are you waiting",
            "ready to break", "take control",
        ]):
            continue
        filtered.append(line)

    return "\n".join(filtered)


# ── Self-Improvement (inspired by Karpathy's autoresearch) ──────

def self_evaluate_and_improve(content: str, agent: str) -> str:
    """Autoresearch-style self-improvement loop.
    Evaluates → improves → keeps best version. Logs every experiment.
    """
    from agents.self_improve import autoresearch_loop
    from agents.llm_client import _call_cerebras, _call_ollama

    # Use failover for the improvement loop too
    def llm_fn(sys, prompt, temp, max_tok):
        try:
            return _call_cerebras(sys, prompt, temp, max_tok)
        except Exception:
            try:
                return _call_ollama(sys, prompt, temp, max_tok)
            except Exception:
                return ""

    try:
        system = AGENT_PERSONAS.get(agent, AGENT_PERSONAS["social"]) + OUTPUT_RULES
        result = autoresearch_loop(
            content=content,
            system_prompt=system,
            llm_fn=llm_fn,
            max_iterations=2,
            threshold=7.0,
            agent_name=agent,
        )
        best = result["best_content"]

        # Append quality scorecard to social/content outputs
        if agent in ("social", "seo", "community", "email") and len(best) > 300:
            eval_prompt = f"""Score this marketing content on these 8 criteria (1-10 each). Be strict.
Return ONLY this format, nothing else:
Hook: X/10
Visual Direction: X/10
Emotion: X/10
Specificity: X/10
Brand Mention: X/10
CTA: X/10
Length: X/10
Hinglish Touch: X/10
Average: X.X/10

Content:
{best[:1500]}"""
            try:
                scores = llm_fn("You are a strict content evaluator. Output ONLY the scores in the exact format requested.", eval_prompt, 0.2, 300)
                if "Average:" in scores:
                    best += f"\n\n---\n\n**Quality Scorecard** *(autoresearch evaluation)*\n\n{scores.strip()}"
            except Exception:
                pass

        return best
    except Exception:
        return content


# ── Chat Endpoint ───────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Conversational chat with live web data and self-improvement."""
    base_system = AGENT_PERSONAS.get(req.agent, AGENT_PERSONAS["social"])
    system = base_system + OUTPUT_RULES + "\n\nToday's date is April 19, 2026. Use this exact date when referencing 'today' or 'this week'."

    import os

    # Override model if specified
    if req.model:
        parts = req.model.split(":")
        if len(parts) == 2:
            os.environ["LLM_PROVIDER"] = parts[0]
            os.environ["CEREBRAS_MODEL"] = parts[1]
            if parts[0] == "ollama":
                os.environ["OLLAMA_MODEL"] = parts[1]

    # LLM call with retry + backoff (handles Cerebras 429 rate limits)
    def llm_call(system_prompt: str, user_prompt: str, temp: float = 0.8, max_tok: int = 4000) -> str:
        from agents.llm_client import _call_cerebras
        import time
        last_error = ""
        for attempt in range(3):
            try:
                return _call_cerebras(system_prompt, user_prompt, temp, max_tok)
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "rate" in last_error.lower():
                    time.sleep(1.5 * (attempt + 1))  # 1.5s, 3s, 4.5s backoff
                else:
                    break
        return f"LLM temporarily unavailable ({last_error[:80]}). Please try again in a moment."

    # Build conversation
    conversation_parts = []
    for msg in req.messages:
        prefix = "User" if msg.role == "user" else "You"
        conversation_parts.append(f"{prefix}: {msg.content}")
    conversation_text = "\n".join(conversation_parts)

    last_msg = req.messages[-1].content if req.messages else ""

    # Intent classification (Luna pattern) — classify and tune temperature
    word_count = len(last_msg.split())
    is_simple = word_count < 8 and not any(kw in last_msg.lower() for kw in ["generate","create","write","find","research"])
    temperature = 0.3 if is_simple else 0.7  # Simple = low temp, creative = higher

    # Detect intent
    is_generation = len(last_msg.split()) >= 5 and any(
        kw in last_msg.lower() for kw in [
            "generate", "create", "write", "make", "draft", "build",
            "post", "carousel", "reel", "meme", "thread", "article",
            "response", "respond", "reply", "content",
        ]
    )

    is_research = any(
        kw in last_msg.lower() for kw in [
            "find", "discover", "search", "browse", "trending", "trend",
            "what are people", "reddit", "competitor", "research", "analyze",
        ]
    ) and len(last_msg.split()) >= 4

    # For community/research: fetch REAL data and build response with Python (don't trust LLM to format it)
    if is_research:
        try:
            from agents.web_scraper import research_live, discover_threads

            is_community = any(kw in last_msg.lower() for kw in ["thread", "discover", "find", "reddit", "community", "respond", "reply"])

            if is_community:
                import re as _re
                from agents.web_scraper import scrape_reddit, search_reddit
                print(f"[RALLY] is_community=True, last_msg={last_msg[:50]}")

                # Parse user's message for specific subreddit and count
                sub_match = _re.search(r'r/(\w+)|/r/(\w+)|subreddit\s+(\w+)', last_msg)
                count_match = _re.search(r'(\d+)\s*(latest|recent|top|post|thread)', last_msg)
                requested_count = int(count_match.group(1)) if count_match else 5

                specific_sub = ""
                if sub_match:
                    # User asked for a specific subreddit
                    specific_sub = sub_match.group(1) or sub_match.group(2) or sub_match.group(3) or ""
                    print(f"[RALLY] Scraping specific sub: r/{specific_sub}, count={requested_count}")
                    raw_posts = scrape_reddit(specific_sub, limit=requested_count, sort="new")
                    print(f"[RALLY] Got {len(raw_posts)} posts from Reddit")
                    threads = [t for t in raw_posts if "error" not in t and t.get("title")][:requested_count]
                    print(f"[RALLY] Filtered to {len(threads)} valid threads")
                else:
                    # Default: discover across Indian finance subreddits
                    data = discover_threads()
                    threads = [t for t in data.get("threads", []) if "error" not in t and t.get("title")][:requested_count]

                # Filter: only when using default discovery (not specific subreddit request)
                if not sub_match:
                    relevant_keywords = ["money", "loan", "salary", "emi", "rent", "emergency", "financial", "broke", "debt", "cash", "income", "job", "unemploy", "invest", "save", "budget", "expense"]
                    filtered = [t for t in threads if any(kw in (t.get("title","") + t.get("body","")).lower() for kw in relevant_keywords)]
                    if filtered:
                        threads = filtered[:requested_count]

                if not threads:
                    # HONEST response when no results found — NEVER fabricate
                    sub_name = specific_sub if sub_match else "Indian finance subreddits"
                    return {"response": f"**No relevant threads found** in r/{sub_name} right now.\n\nThis could mean:\n- The subreddit has very few recent posts\n- Reddit is blocking requests from our server\n- The subreddit name might be different (check spelling)\n\n**Try:**\n- A different subreddit: `r/personalfinanceindia`, `r/IndiaInvestments`, `r/india`\n- A broader search: \"Find threads about emergency loans on Reddit\""}

                if threads:
                    discovered_count = len(threads)
                    # Build thread list for the LLM (ONE call for all replies)
                    thread_list = ""
                    for i, t in enumerate(threads):
                        # Only mention Apollo Cash if the thread is about NEEDING money urgently (loans, emergency, broke)
                        # NOT for investment, savings, or financial education posts
                        thread_text = (t.get("title","") + " " + t.get("body","")).lower()
                        is_need_money = any(kw in thread_text for kw in ["need money","loan","emergency","salary delay","broke","urgent","help me","struggling","can't pay","short on","rent due","medical bill","repair cost"])
                        is_investment = any(kw in thread_text for kw in ["invest","sip","mutual fund","cagr","xirr","portfolio","stock","nifty","sensex","etf","returns"])
                        mention = "Mention Apollo Cash BRIEFLY as ONE option" if is_need_money and not is_investment and i < 2 else "Do NOT mention Apollo Cash or any loan/finance app. Give pure helpful advice only. Do NOT invent features that Apollo Cash doesn't have."
                        length = "short (2-3 sentences)" if i % 2 == 0 else "detailed (4-6 sentences)"
                        thread_list += f"""
THREAD {i+1}: r/{t.get('subreddit','')} — "{t['title']}"
Body: {t.get('body','')[:200]}
Instructions: {mention}. Keep it {length}. Vary your style.
---
"""
                    # ONE LLM call for all replies
                    batch_prompt = f"""Write Reddit replies for each of these REAL threads. Each reply should sound like a different person. No URLs. No numbered lists for every reply. Vary tone and length.

{thread_list}

Format each reply as:
REPLY 1:
(your reply)

REPLY 2:
(your reply)
etc."""

                    all_replies = llm_call(system, batch_prompt, temp=0.9, max_tok=2000)
                    all_replies = strip_promotional_language(all_replies)

                    # Parse replies
                    import re
                    reply_blocks = re.split(r'REPLY\s*\d+\s*:', all_replies)
                    reply_blocks = [r.strip() for r in reply_blocks if r.strip()]

                    # Build final response with Python-controlled structure
                    parts = [f"I scanned Reddit and found **{discovered_count} real threads**. Here are the top {len(threads)} with my responses:\n"]

                    for i, t in enumerate(threads):
                        thread_url = t.get("url", f"https://reddit.com/r/{t.get('subreddit','')}")
                        parts.append(f"### Thread {i+1} — r/{t.get('subreddit', '')}")
                        parts.append(f"[**\"{t['title']}\"**]({thread_url}) — {t.get('score', 0)} upvotes, {t.get('num_comments', 0)} comments")
                        if t.get("author"):
                            parts.append(f"*by u/{t['author']}*")
                        if t.get("body"):
                            parts.append(f"\n> {t['body'][:200]}{'...' if len(t.get('body','')) > 200 else ''}\n")

                        reply = reply_blocks[i] if i < len(reply_blocks) else "Great question — would need more context to give specific advice."
                        actually_mentions = is_need_money and not is_investment and i < 2
                        parts.append(f"**My response:**\n{reply}")
                        parts.append(f"\n*Strategy: {'Mentions Apollo Cash contextually' if actually_mentions else 'Pure advice — no brand mention'}*\n")

                    response = "\n".join(parts)
                    return {"response": response}

            else:
                # Research / trends
                topic = " ".join(w for w in last_msg.lower().split() if w not in ["research","trending","analyze","what","are","people","about","on","right","now","the","discuss","discussing"])
                if len(topic) < 5:
                    topic = "personal loan India"
                data = research_live(topic)

                # Build research response with Python
                parts = [f"## Live Research Results\n*Scanned Reddit and Google Trends just now*\n"]

                reddit_posts = data.get("reddit", {}).get("posts", [])
                if reddit_posts:
                    real_posts = [p for p in reddit_posts if "error" not in p][:10]
                    parts.append(f"### Reddit ({len(real_posts)} posts found)\n")
                    for p in real_posts:
                        parts.append(f"- **\"{p['title']}\"** — r/{p.get('subreddit','')} ({p.get('score',0)} upvotes, {p.get('num_comments',0)} comments)")
                    parts.append("")

                trends = data.get("google_trends", {}).get("trends", {})
                if trends:
                    parts.append("### Google Trends (India, last 7 days)\n")
                    for kw, d in trends.items():
                        parts.append(f"- **{kw}**: {d.get('trend','stable')} (interest: {d.get('current','N/A')}/100)")
                    parts.append("")

                related = data.get("google_trends", {}).get("related_queries", {})
                if related:
                    for kw, r in related.items():
                        if r.get("rising_queries"):
                            parts.append(f"- Rising searches for **{kw}**: {', '.join(r['rising_queries'][:5])}")
                    parts.append("")

                # Now ask LLM for insights BASED on the real data
                data_summary = "\n".join(parts)
                insight_prompt = f"""Based on this REAL data I just scraped:

{data_summary}

Give 3-4 actionable content recommendations for Apollo Cash marketing. What should Vortex, Draft, and Rally create based on what's trending? Be specific."""

                insights = llm_call(system, insight_prompt, temp=0.7, max_tokens=1000)
                parts.append("\n### Content Recommendations\n")
                parts.append(insights)

                response = "\n".join(parts)
                response = strip_promotional_language(response)
                return {"response": response}

        except Exception as e:
            print(f"[RALLY/FREQ ERROR] {str(e)}")
            # Return honest error instead of falling through to LLM fabrication
            return {"response": f"**Research error:** {str(e)[:200]}\n\nThe live web scraper hit an issue. Try again, or try a different subreddit."}

    # Dispatch agent: handle posting commands
    if req.agent == "dispatch":
        is_post_command = any(kw in last_msg.lower() for kw in ["post", "publish", "schedule", "send", "share", "confirm", "yes"])
        if is_post_command and len(last_msg.split()) >= 3:
            try:
                import requests as http_requests
                # Check connected channels
                ch_resp = http_requests.get(f"{POSTIZ_URL}/integrations", headers={"Authorization": POSTIZ_KEY}, timeout=5)
                channels = ch_resp.json() if ch_resp.ok else []

                # Extract content from conversation (find the longest message)
                all_contents = [m.content for m in req.messages if m.role == "user" and len(m.content) > 50]
                post_content = all_contents[-1] if all_contents else last_msg

                if channels:
                    channel_names = ", ".join([c.get("name", c.get("providerName", "channel")) for c in channels])
                    # Post via Postiz
                    post_resp = http_requests.post(
                        f"{POSTIZ_URL}/posts",
                        headers={"Authorization": POSTIZ_KEY, "Content-Type": "application/json"},
                        json={"content": post_content[:500], "platforms": [c["id"] for c in channels]},
                        timeout=10
                    )
                    if post_resp.ok:
                        result = post_resp.json()
                        response = f"**Posted successfully!**\n\nContent sent to: {channel_names}\n\nPost ID: `{result.get('id', 'N/A')}`\n\nYou can view and manage this post in the Publish tab."
                    else:
                        response = f"**Post created** (queued for publishing)\n\nContent will be sent to: {channel_names}\n\nCheck the Publish tab to verify the schedule."
                else:
                    response = "**No channels connected yet.**\n\nGo to the **Publish** tab → click **Add Channel** to connect Instagram, Twitter, Facebook, etc.\n\nOnce connected, come back and I'll post your content."

                return {"response": response}
            except Exception as e:
                pass  # Fall through to normal chat

    # Normal chat flow (greetings, generation requests, etc.)
    if is_generation:
        instruction = "Generate the content NOW. Do not ask questions. Be thorough, specific, and emotional."
    else:
        instruction = "Respond conversationally. If greeting, introduce yourself briefly and ask what they'd like to create."

    prompt = f"""Conversation:
{conversation_text}

{instruction}"""

    response = llm_call(system, prompt, temp=temperature, max_tok=4000)

    if is_generation and len(response) > 200:
        response = strip_promotional_language(response)
        response = self_evaluate_and_improve(response, req.agent)

    return {"response": response}


# ── Live Web Scraping Endpoints ─────────────────────────────────

@app.post("/api/browse/reddit")
async def browse_reddit(req: RedditRequest):
    from agents.web_scraper import scrape_reddit, search_reddit
    if req.query:
        posts = search_reddit(req.query, subreddit=req.subreddit, limit=req.limit)
    else:
        posts = scrape_reddit(req.subreddit, limit=req.limit)
    return {"status": "live", "source": "reddit", "posts": posts, "count": len(posts)}

@app.post("/api/browse/trends")
async def browse_trends(req: TrendsRequest):
    from agents.web_scraper import get_google_trends
    keywords = [k.strip() for k in req.keywords.split(",")]
    return {"status": "live", "source": "google_trends", "data": get_google_trends(keywords)}

@app.post("/api/browse/discover")
async def browse_discover():
    from agents.web_scraper import discover_threads
    return {"status": "live", "source": "reddit_live", "data": discover_threads()}


# ── Orchestrator ────────────────────────────────────────────────

@app.post("/api/orchestrate")
async def orchestrate(req: GoalRequest):
    run = orchestrator.run(req.goal)
    return orchestrator.get_run_summary(run)


# ── Direct Agent Endpoints ──────────────────────────────────────

@app.post("/api/social/generate")
async def generate_social(req: SocialPostRequest):
    from agents.social_media_agent import generate_posts, save_posts
    posts = generate_posts(
        count=req.count,
        formats=[f.strip() for f in req.formats.split(",")],
        audience_segment=req.audience_segment,
        themes=[t.strip() for t in req.themes.split(",")],
    )
    filepath = save_posts(posts)
    return {"status": "success", "count": len(posts), "file": filepath, "posts": posts}

@app.post("/api/social/calendar")
async def generate_calendar():
    from agents.social_media_agent import generate_weekly_calendar
    return {"status": "success", "calendar": generate_weekly_calendar()}

@app.post("/api/seo/article")
async def generate_article(req: ArticleRequest):
    from agents.seo_agent import generate_article as gen_article, save_article, ARTICLE_BRIEFS
    brief = {"keyword": req.keyword, "secondary_keywords": [], "language": req.language, "audience_segment": req.audience_segment, "article_type": req.article_type}
    for b in ARTICLE_BRIEFS:
        if b["keyword"].lower() == req.keyword.lower():
            brief = b; break
    article = gen_article(brief)
    json_path, md_path = save_article(article)
    return {"status": "success", "article": article, "json_path": json_path, "md_path": md_path}

@app.post("/api/seo/keywords")
async def keyword_analysis():
    from agents.seo_agent import generate_keyword_analysis
    return {"status": "success", "analysis": generate_keyword_analysis()}

@app.post("/api/community/responses")
async def generate_community(req: CommunityRequest):
    from agents.community_agent import generate_responses, save_responses
    responses = generate_responses(count=req.count, platforms=[p.strip() for p in req.platforms.split(",")])
    filepath = save_responses(responses)
    mentions = sum(1 for r in responses if r.get("response", {}).get("mentions_apollo_cash", False))
    return {"status": "success", "count": len(responses), "mention_ratio": f"{mentions}/{len(responses)}", "responses": responses}

@app.post("/api/community/discover")
async def discover():
    from agents.community_agent import generate_thread_discovery
    return {"status": "success", "discovery": generate_thread_discovery()}

@app.post("/api/research/trends")
async def research_trends():
    from agents.research_agent import research_trending_topics, save_research
    trends = research_trending_topics()
    filepath = save_research(trends, "trending_topics")
    return {"status": "success", "trends": trends, "file": filepath}

@app.post("/api/research/sentiment/{segment}")
async def research_sentiment(segment: str):
    from agents.research_agent import research_audience_sentiment, save_research
    sentiment = research_audience_sentiment(segment)
    filepath = save_research(sentiment, f"sentiment_{segment}")
    return {"status": "success", "sentiment": sentiment, "file": filepath}

@app.post("/api/research/adapt")
async def adapt_strategy():
    from agents.research_agent import analyze_engagement_and_adapt, save_research
    mock = {"period": "last_7_days", "posts": [
        {"format": "reel", "theme": "salary delay", "likes": 2400, "shares": 180},
        {"format": "meme", "theme": "month end", "likes": 3200, "shares": 450},
        {"format": "reel", "theme": "first loan", "likes": 3800, "shares": 520},
    ]}
    adaptation = analyze_engagement_and_adapt(mock)
    filepath = save_research(adaptation, "engagement_adaptation")
    return {"status": "success", "adaptation": adaptation, "file": filepath}


# ── Data Endpoints ──────────────────────────────────────────────

@app.get("/api/outputs/{agent_type}")
async def get_outputs(agent_type: str):
    output_dir = Path("output") / agent_type
    if not output_dir.exists():
        return {"files": [], "count": 0}
    files = []
    for f in sorted(output_dir.glob("*.json")):
        files.append({"filename": f.name, "path": str(f), "size_bytes": f.stat().st_size})
    return {"files": files, "count": len(files)}

@app.get("/api/memory")
async def get_memory():
    return memory.all_memories()

@app.get("/api/runs")
async def get_runs():
    return {"runs": [orchestrator.get_run_summary(r) for r in orchestrator.runs], "count": len(orchestrator.runs)}

# ── Auto-Publishing Endpoints ───────────────────────────────────

class PublishRequest(BaseModel):
    platform: str = "instagram"
    content: dict = {}

@app.post("/api/publish")
async def publish_content(req: PublishRequest):
    """Publish content to a platform (real or simulated)."""
    from agents.auto_publisher import publish_instagram, publish_facebook, publish_twitter, _simulate, PLATFORM_HANDLERS
    handler = PLATFORM_HANDLERS.get(req.platform, _simulate)
    result = handler(req.content)
    return {"status": result.status, "platform": result.platform, "post_id": result.post_id, "url": result.url}

@app.post("/api/publish/batch")
async def publish_batch_content():
    """Publish all pending calendar posts."""
    from agents.auto_publisher import publish_batch, get_publish_log
    # Get latest social posts
    output_dir = Path("output/social_media")
    posts = []
    if output_dir.exists():
        for f in sorted(output_dir.glob("*.json"), reverse=True)[:1]:
            with open(f) as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    posts = data
    if posts:
        results = publish_batch(posts)
        return {"status": "success", "published": len(results), "results": [{"platform": r.platform, "status": r.status, "post_id": r.post_id} for r in results]}
    return {"status": "no_content", "message": "No posts to publish. Generate content first."}

@app.get("/api/publish/log")
async def publish_log():
    """Get the publishing history."""
    from agents.auto_publisher import get_publish_log
    log = get_publish_log()
    return {"entries": log, "count": len(log)}


# ── Postiz Integration ───────────────────────────────────────────

POSTIZ_URL = "http://72.60.200.15:4007/api/public/v1"
POSTIZ_KEY = "6a0740fd2d9dbb45a5a4c3673a42e34c0d768766db6287140bda0132d0d1724c"

@app.get("/api/postiz/status")
async def postiz_status():
    """Check Postiz connection status."""
    import requests
    try:
        r = requests.get(f"{POSTIZ_URL}/is-connected", headers={"Authorization": POSTIZ_KEY}, timeout=5)
        return r.json()
    except Exception as e:
        return {"connected": False, "error": str(e)}

@app.get("/api/postiz/channels")
async def postiz_channels():
    """Get connected social channels."""
    import requests
    try:
        r = requests.get(f"{POSTIZ_URL}/integrations", headers={"Authorization": POSTIZ_KEY}, timeout=5)
        return {"channels": r.json()}
    except Exception as e:
        return {"channels": [], "error": str(e)}

class PostizPostRequest(BaseModel):
    content: str
    platforms: list[str] = []
    schedule: str = ""

@app.post("/api/postiz/post")
async def postiz_create_post(req: PostizPostRequest):
    """Create a post via Postiz API — schedules or publishes immediately."""
    import requests
    try:
        payload = {
            "content": req.content,
            "platforms": req.platforms,
        }
        if req.schedule:
            payload["date"] = req.schedule
        r = requests.post(f"{POSTIZ_URL}/posts", headers={"Authorization": POSTIZ_KEY, "Content-Type": "application/json"}, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/postiz/posts")
async def postiz_get_posts():
    """Get scheduled/published posts."""
    import requests
    from datetime import datetime, timedelta
    try:
        start = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
        end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT23:59:59Z")
        r = requests.get(f"{POSTIZ_URL}/posts?startDate={start}&endDate={end}", headers={"Authorization": POSTIZ_KEY}, timeout=5)
        return {"posts": r.json()}
    except Exception as e:
        return {"posts": [], "error": str(e)}


@app.get("/api/experiments")
async def experiments():
    """View autoresearch experiment stats — how many iterations, scores, improvements."""
    from agents.self_improve import get_experiment_stats
    return get_experiment_stats()

@app.get("/api/health")
async def health():
    return {"status": "healthy", "llm_provider": llm.name(), "timestamp": datetime.now().isoformat()}

@app.post("/api/pipeline/run")
async def run_pipeline():
    goal = "Run all agents: generate 5 social posts, 1 SEO article, 5 community responses, weekly calendar, keyword analysis, thread discovery"
    run = orchestrator.run(goal)
    return orchestrator.get_run_summary(run)
