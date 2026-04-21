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

SISTER AGENTS — if the user asks about another agent's job, redirect them:
- **Vortex**: social media (carousels, reels, memes, threads)
- **Draft**: SEO articles and blog posts
- **Rally**: community responses (Reddit, Quora, Twitter)
- **Freq**: research and trend analysis
- **Pulse**: email campaigns and newsletters
- **Dispatch**: publishing to social channels
Say: "That's [Agent Name]'s specialty — switch to them in the sidebar for best results."

CRITICAL DATA INTEGRITY RULES:
- NEVER fabricate Reddit posts, usernames, subreddits, or thread titles
- NEVER say "I can't access Reddit" — you CAN, via the Pullpush.io API
- NEVER create fake "realistic" posts and present them as real
- If real data is provided to you, use ONLY that data
- If no real data is provided, say "I need to scan Reddit first — ask me to find threads from a specific subreddit"
- NEVER invent features that Apollo Cash doesn't have. It is ONLY a personal loan app.
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
- You have access to the Postiz publishing API at https://srv1317892.hstgr.cloud
- Connected channels can be checked via the API
- Always confirm before publishing — don't post without user approval""",

    "email": APOLLO_CONTEXT + """
You are **Pulse** — the email and newsletter agent.

Write email campaigns, newsletters, and drip sequences for Apollo Cash users and prospects.

VOICE (match Apollo Finvest's actual tone — NOT literary, NOT melodramatic):
- Write like a smart friend texting, not a poet writing prose
- Short punchy sentences. No fluff. No "we've watched people struggle" emotional padding.
- Direct and confident: "Here's the deal." "You qualify." "15 minutes. Done."
- Use the same energy as Apollo Finvest's culture page: casual, startup, no-BS
- Think Stripe's emails or Razorpay's copy — clean, sharp, useful

Rules:
- Subject lines: under 50 chars, direct, no clickbait ("Your ₹5K is ready" not "A special message for you")
- Emails: under 150 words. Ruthlessly short.
- CTA: one line, soft ("Check it out" not "APPLY NOW")
- No melodrama, no sob stories, no "we understand your pain"
- Just facts, value, and a reason to care
- Always include unsubscribe line
- Write in PLAIN TEXT only — no bullet points, no numbered lists, no markdown formatting
- Email should look like a simple text email a friend would send — not a designed newsletter
- No bold, no headers, no horizontal rules — just paragraphs of plain text
- NO poetic endings. No "And the day after." dramatic one-liners. Just end normally like a real email.
- Sound like a startup founder sending a quick note, not a copywriter crafting prose

BAD EMAIL EXAMPLES (never write like this):
- "We see you." — too dramatic
- "This isn't about borrowing. It's about starting on your own terms." — too philosophical
- "And the day after." — too poetic
- "No one's chasing you." — trying too hard to be chill

GOOD EMAIL EXAMPLE (write like this for transactional/drip emails):
"Hey — you signed up but haven't used Apollo Cash yet. Your ₹5,000 limit is still active. Takes 15 min to get cash in your account if you ever need it. No CIBIL needed. Just keeping you posted. — Apollo Cash team"

For NEWSLETTERS, match Apollo Finvest's Substack tone (apollo.substack.com):
- Sharp, witty, industry-insider voice
- Uses Indian cultural references ("desi dads doing shaadi matchmaking")
- Slightly sarcastic about outdated banking practices
- Data-driven but conversational
- Example opening: "There's a certain smugness in the world of lending. You'll hear it over conference tables and VC calls: 'We collect six months of bank statements.' Congratulations. You've just unlocked 2016."
- Mix Hindi phrases naturally when it adds punch
- Challenge conventional wisdom, call out BS in the industry""",

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
No horizontal rules. No decorative characters. No raw JSON.
NEVER use emojis — no checkmarks, no colored circles, no chart icons. Zero emojis anywhere.
Let whitespace do the work.

SOURCE RULES (CRITICAL):
- NEVER fabricate source links, Reddit post scores, YouTube view counts, or Google Trends percentages
- NEVER invent Reddit posts or usernames and cite them as sources
- NEVER make up growth percentages like "120% increase" unless you have real data
- If you are using your own knowledge (not scraped data), do NOT include a Sources section at all
- ONLY include a Sources section when REAL scraped data was provided to you by the system
- Google Trends links are OK if the keyword is real: https://trends.google.com/trends/explore?q=KEYWORD&geo=IN
- But do NOT fabricate the trend percentage — just link to the page and let the user check"""


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
    from agents.llm_client import generate_with_failover

    def llm_fn(sys, prompt, temp, max_tok):
        return generate_with_failover(sys, prompt, temp, max_tok)

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

        # Quality scorecard removed — not needed for demo

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
        from agents.llm_client import generate_with_failover
        return generate_with_failover(system_prompt, user_prompt, temp, max_tok)

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

    # Check if this is a follow-up question about previous results (not a new research request)
    has_prior_context = len(req.messages) > 2 and any(
        "real threads" in m.content.lower() or "Thread 1" in m.content or "My response:" in m.content
        for m in req.messages if m.role == "assistant"
    )
    is_followup = has_prior_context and not any(
        kw in last_msg.lower() for kw in ["find new", "scrape again", "search for", "latest from r/"]
    )

    # For community/research: fetch REAL data (but not on follow-ups — use conversation context)
    if is_research and not is_followup:
        try:
            from agents.web_scraper import research_live, discover_threads

            is_community = req.agent in ("community",) and any(kw in last_msg.lower() for kw in ["thread", "discover", "find", "reddit", "community", "respond", "reply"])

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
                    batch_prompt = f"""Write Reddit replies for each of these REAL threads.

QUALITY RULES:
- Each reply must ADD something the poster doesn't already know — a specific insight, a personal experience, a concrete recommendation
- For investment posts: mention specific fund names, platforms (Groww, Zerodha, Kuvera), exact numbers, or share a real-sounding personal experience
- For money problem posts: give actionable steps, not just sympathy
- NEVER just paraphrase what the poster said — add NEW value
- Each reply must sound like a DIFFERENT person with different expertise level
- Vary length: some short and punchy (2 lines), some detailed with specifics (5-6 lines)
- No URLs. No numbered lists for every reply.

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

    # Dispatch agent: handle connect + posting commands
    if req.agent == "dispatch":
        import requests as http_requests

        # Handle channel connection requests
        all_platform_keywords = ["x", "twitter", "tweet", "linkedin", "facebook", "fb", "instagram", "insta", "ig", "reddit", "youtube", "yt", "threads", "tiktok", "pinterest"]
        is_connect = any(kw in last_msg.lower() for kw in ["connect", "add channel", "link", "set up", "setup"])
        # Also treat bare platform names as connect requests
        if not is_connect and last_msg.strip().lower() in all_platform_keywords:
            is_connect = True
        if is_connect:
            # Detect which platform
            platforms = {
                "x": ["x", "twitter", "tweet"],
                "linkedin": ["linkedin"],
                "linkedin-page": ["linkedin page"],
                "facebook": ["facebook", "fb"],
                "instagram": ["instagram", "insta", "ig"],
                "reddit": ["reddit"],
                "youtube": ["youtube", "yt"],
                "threads": ["threads"],
                "tiktok": ["tiktok"],
                "pinterest": ["pinterest"],
            }
            detected = None
            for provider, keywords in platforms.items():
                if any(kw in last_msg.lower() for kw in keywords):
                    detected = provider
                    break

            if detected:
                try:
                    cookie = await get_postiz_cookie()
                    if cookie:
                        r = http_requests.get(
                            f"{POSTIZ_INTERNAL}/integrations/social/{detected}",
                            headers={"Authorization": f"Bearer {cookie}", "Cookie": f"auth={cookie}"},
                            timeout=10
                        )
                        if r.ok:
                            data = r.json()
                            if "url" in data:
                                return {"response": f"**Ready to connect {detected.upper()}!**\n\n[Click here to authorize {detected.upper()}]({data['url']})\n\nThis will open {detected.upper()}'s login page. Authorize Agent Blaze, and you'll be redirected back. Your channel will appear automatically."}
                            else:
                                return {"response": f"Couldn't get OAuth URL for {detected}. Make sure the API keys are configured."}
                    return {"response": "Could not authenticate with the publishing service. Please try again."}
                except Exception as e:
                    return {"response": f"Error connecting to {detected}: {str(e)[:100]}"}
            else:
                available = "X (Twitter), Instagram, Facebook, LinkedIn, Reddit, YouTube, TikTok, Threads, Pinterest"
                return {"response": f"Which platform would you like to connect? Just say something like:\n\n- *Connect my Twitter*\n- *Add Instagram*\n- *Link my LinkedIn*\n\n**Available:** {available}"}

        # Handle posting — check conversation history for content
        is_post_intent = any(kw in last_msg.lower() for kw in ["post", "publish", "schedule", "send", "share", "thread"])
        references_earlier = any(kw in last_msg.lower() for kw in ["this", "above", "that", "it", "the content", "same"])
        has_content = len(last_msg.split()) >= 10

        if is_post_intent:
            try:
                ch_resp = http_requests.get(f"{POSTIZ_URL}/integrations", headers={"Authorization": POSTIZ_KEY}, timeout=5)
                channels = ch_resp.json() if ch_resp.ok else []

                if not channels:
                    return {"response": "**No channels connected yet.**\n\nConnect a platform first — click the X, Instagram, or LinkedIn button above."}

                channel_names = ", ".join([c.get("name", c.get("providerName", "channel")) for c in channels])

                # Find content to post: current message, or from conversation history
                post_content = None
                if has_content:
                    post_content = last_msg
                elif references_earlier or not has_content:
                    # Look through conversation history for the longest user message (likely the content)
                    user_msgs = [m.content for m in req.messages if m.role == "user" and len(m.content) > 30]
                    # Also check assistant messages (content may have been generated by another agent)
                    asst_msgs = [m.content for m in req.messages if m.role == "assistant" and len(m.content) > 50]
                    all_content = user_msgs + asst_msgs
                    if all_content:
                        post_content = max(all_content, key=len)

                if not post_content:
                    return {"response": f"Sure! What content would you like to post to **{channel_names}**?\n\nType or paste your content below, and I'll publish it for you."}

                # Extract media URLs if attached
                import re
                media_match = re.findall(r'\[Attached media: (.*?)\]', post_content)
                image_urls = []
                if media_match:
                    image_urls = [u.strip() for u in media_match[0].split(",")]
                    post_content = re.sub(r'\s*\[Attached media:.*?\]', '', post_content).strip()

                # Preview the content before posting
                preview = post_content[:150] + ("..." if len(post_content) > 150 else "")
                from datetime import datetime as dt_now
                post_payload = {
                    "type": "now",
                    "shortLink": False,
                    "date": dt_now.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "tags": [],
                    "posts": [{
                        "integration": {"id": c["id"]},
                        "value": [{"content": post_content[:500], "image": [{"path": url} for url in image_urls]}],
                        "settings": {"who_can_reply_post": "everyone"}
                    } for c in channels]
                }
                post_resp = http_requests.post(
                    f"{POSTIZ_URL}/posts",
                    headers={"Authorization": POSTIZ_KEY, "Content-Type": "application/json"},
                    json=post_payload,
                    timeout=10
                )
                if post_resp.ok:
                    result = post_resp.json()
                    post_id = result[0].get("postId", "N/A") if isinstance(result, list) else "N/A"
                    response = f"**Posted to {channel_names}!** ✓\n\n> {preview}\n\nPost ID: `{post_id}`"
                else:
                    response = f"**Failed to post:** {post_resp.text[:200]}"

                return {"response": response}
            except Exception as e:
                pass  # Fall through to normal chat

    # Cross-agent redirect — Python-controlled, not LLM-dependent
    redirects = {
        "social": {"keywords": ["carousel", "reel", "meme", "instagram post", "youtube short", "whatsapp forward", "social media"], "agent": "Vortex", "job": "social media content"},
        "seo": {"keywords": ["blog", "article", "seo", "landing page"], "agent": "Draft", "job": "SEO articles"},
        "community": {"keywords": ["reddit response", "quora answer", "community reply", "thread response"], "agent": "Rally", "job": "community responses"},
        "email": {"keywords": ["email", "newsletter", "drip sequence", "welcome email"], "agent": "Pulse", "job": "email campaigns"},
        "dispatch": {"keywords": ["post to", "publish to", "schedule post", "send to instagram"], "agent": "Dispatch", "job": "publishing to channels"},
    }
    agent_names = {"social": "Vortex", "seo": "Draft", "community": "Rally", "research": "Freq", "email": "Pulse", "dispatch": "Dispatch"}
    my_name = agent_names.get(req.agent, req.agent)
    for agent_id, cfg in redirects.items():
        if req.agent != agent_id and any(kw in last_msg.lower() for kw in cfg["keywords"]):
            return {"response": f"That's **{cfg['agent']}'s** specialty — {cfg['job']}. Switch to **{cfg['agent']}** in the sidebar for the best results.\n\nI'm **{my_name}** — I handle research, trends, and content strategy."}

    # Normal chat flow (greetings, generation requests, etc.)
    if is_generation:
        instruction = "Generate the content NOW. Do not ask questions. Be thorough, specific, and emotional."
    elif is_followup:
        instruction = "The user is asking a follow-up question about your previous response. Use the conversation history above to answer. Reference specific details from your earlier messages. Do NOT re-generate or re-scrape — just discuss what was already shared."
    else:
        instruction = "Respond conversationally. If greeting, introduce yourself briefly and ask what they'd like to create."

    prompt = f"""Full conversation history (use this for context on follow-up questions):
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

POSTIZ_URL = "https://srv1317892.hstgr.cloud/api/public/v1"
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


POSTIZ_INTERNAL = "https://srv1317892.hstgr.cloud/api"
POSTIZ_AUTH_COOKIE = ""
POSTIZ_AUTH_TIME = 0

async def get_postiz_cookie():
    """Login to Postiz and get auth cookie. Re-login every 30 min."""
    global POSTIZ_AUTH_COOKIE, POSTIZ_AUTH_TIME
    import time
    if POSTIZ_AUTH_COOKIE and (time.time() - POSTIZ_AUTH_TIME) < 1800:
        return POSTIZ_AUTH_COOKIE
    import requests
    try:
        r = requests.post(f"{POSTIZ_INTERNAL}/auth/login",
            json={"email": "demo@agentblaze.com", "password": "Blaze2026!", "provider": "LOCAL"},
            timeout=10)
        if r.ok:
            POSTIZ_AUTH_COOKIE = r.headers.get("auth", "")
            for cookie in r.cookies:
                if cookie.name == "auth":
                    POSTIZ_AUTH_COOKIE = cookie.value
            POSTIZ_AUTH_TIME = time.time()
    except Exception as e:
        print(f"[POSTIZ AUTH ERROR] {e}")
    return POSTIZ_AUTH_COOKIE

@app.get("/api/connect/{provider}")
async def connect_channel(provider: str):
    """Get OAuth URL for a social provider — returns JSON with the URL."""
    import requests
    cookie = await get_postiz_cookie()
    if not cookie:
        return {"error": "Could not authenticate with Postiz"}
    r = requests.get(f"{POSTIZ_INTERNAL}/integrations/social/{provider}",
        headers={"Authorization": f"Bearer {cookie}", "Cookie": f"auth={cookie}"},
        timeout=10)
    if r.ok:
        data = r.json()
        if "url" in data:
            return {"url": data["url"]}
        return {"error": "No OAuth URL returned"}
    return {"error": f"Postiz returned {r.status_code}"}

@app.delete("/api/connect/{provider}")
async def disconnect_channel(provider: str):
    """Disconnect a social channel by provider name."""
    import requests
    cookie = await get_postiz_cookie()
    if not cookie:
        return {"error": "Could not authenticate with Postiz"}
    # Get channels list to find the matching one
    r = requests.get(f"{POSTIZ_INTERNAL}/integrations/list",
        headers={"Authorization": f"Bearer {cookie}", "Cookie": f"auth={cookie}"},
        timeout=10)
    if r.ok:
        data = r.json()
        integrations = data.get("integrations", [])
        for integration in integrations:
            if integration.get("identifier", "").lower() == provider.lower():
                # Delete this channel
                dr = requests.delete(f"{POSTIZ_INTERNAL}/integrations",
                    headers={"Authorization": f"Bearer {cookie}", "Cookie": f"auth={cookie}", "Content-Type": "application/json"},
                    json={"id": integration["id"]},
                    timeout=10)
                if dr.ok:
                    return {"success": True, "message": f"Disconnected {provider}"}
                return {"error": f"Failed to disconnect: {dr.text}"}
        return {"error": f"No {provider} channel found"}
    return {"error": "Could not fetch channels"}

from fastapi import UploadFile, File as FastAPIFile

@app.post("/api/media/upload")
async def upload_media(file: UploadFile = FastAPIFile(...)):
    """Upload media file to Postiz and return the URL."""
    import requests
    contents = await file.read()
    r = requests.post(
        f"{POSTIZ_URL}/upload",
        headers={"Authorization": POSTIZ_KEY},
        files={"file": (file.filename, contents, file.content_type)},
        timeout=30
    )
    if r.ok:
        data = r.json()
        return {"url": data.get("path", ""), "id": data.get("id", "")}
    return {"error": f"Upload failed: {r.text}"}

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
