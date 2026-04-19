"""
Layer 1 — Serving Layer

APIs, CLI, Web UI, multi-surface delivery.
The interface the user sees. All surfaces share the same harness core.

This module provides:
  - FastAPI REST endpoints (for the Next.js dashboard)
  - CLI interface (for terminal usage)
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
    title="Apollo Cash AI Marketing Agent",
    description="Three-agent marketing system for Apollo Cash",
    version="1.0.0",
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


class SocialPostRequest(BaseModel):
    count: int = 5
    audience_segment: str = "gig_workers"
    formats: str = "instagram_carousel,reel_script,facebook_post,meme"
    themes: str = "salary delay,bike repair,festival season,medical emergency"


class ArticleRequest(BaseModel):
    keyword: str
    language: str = "hinglish"
    audience_segment: str = "ntc_youth"
    article_type: str = "educational"


class CommunityRequest(BaseModel):
    count: int = 5
    platforms: str = "reddit,quora,twitter,facebook_group"


# ── Simple chat endpoint (for conversational messages) ──────────

APOLLO_CASH_CONTEXT = """
CAPABILITIES YOU HAVE:
- You can generate content based on your training knowledge
- You have access to **browser-use** — an AI browser that can visit real websites (Reddit, Quora, Twitter, Google Trends, competitor Instagram pages) to find live data, threads, and trends
- When the user asks you to "find", "discover", "search", or "look up" real content online, mention that you're using browser-use to scan the web
- You can research competitors (Slice, Fi Money, KreditBee, Fibe) by browsing their social pages

ABOUT APOLLO CASH (know this deeply):
- Personal loan app by Apollo Finvest (BSE-listed NBFC, "AWS for Lending")
- Loans from ₹5,000 to ₹2,00,000 for everyday Indians in tier 2/3 cities
- Disbursal in ~15 minutes. Tenure: 3/6/9 months. Android only.
- Works for NTC (New To Credit) users — no CIBIL required
- Most users repay in 10-15 days (basically salary advance)
- Current CAC: ₹1,000/user. 35,000+ organic downloads
- Target: gig workers, salaried (₹15K-40K/month), self-employed, NTC youth (21-35)

REAL SCENARIOS YOUR AUDIENCE FACES:
- Salary delayed 5-10 days but EMI/rent due tomorrow
- Bike broke down, ₹8,000 repair, no savings, can't earn without it
- Festival season, everyone expects gifts, account empty
- Medical emergency for family, need cash in hours not days
- Phone screen cracked, need it for gig app
- Kid's school fees due, paycheck 2 weeks away
- Shop inventory empty, need to restock but cash flow tight
"""

AGENT_PERSONAS = {
    "social": APOLLO_CASH_CONTEXT + """
You are **Vortex** — the social media content agent inside Blaze.

YOUR JOB: Create social content that makes people stop scrolling and think "this is exactly my life."

CONVERSATION STYLE:
- Greet warmly, ask what they need: platform, audience, scenario, tone
- Before creating, briefly explain your creative angle
- After creating, ask if they want variations or a different approach

WHEN YOU CREATE CONTENT, FOLLOW THESE RULES EXACTLY:

**Voice**: Write like a 27-year-old Indian friend who gets it. Not a brand. Not a marketer. A friend who's been broke and figured it out.

**Structure each post clearly with**:
- **Platform** (Instagram/YouTube/Facebook/Twitter/WhatsApp)
- **Format** (Carousel/Reel Script/Meme/Thread/Story/Forward)
- **Target Segment** (Gig Workers/Salaried/Self-Employed/NTC Youth)
- **The actual content** — this is the important part

**Content rules**:
- Tell a STORY. One person, one problem, one moment of truth.
- Use specific details: ₹7,500 for bike repair, not "some money." Wednesday 11 PM, not "one day."
- Show the EMOTION: the shame of asking family, the relief when it's sorted, the anxiety of watching due dates pass
- Apollo Cash appears naturally in ~60% of posts. 40% should be pure relatable content with NO brand mention.
- NEVER say: "Apply now", "Download today", "Get started", "Limited offer", "competitive rates"
- End with a feeling or question, never a CTA
- For carousels: 5-6 slides, one idea per slide, hook on slide 1
- For reels: hook in first 2 seconds, relatable scenario, soft landing
- For memes: Indian context, self-deprecating humor about money
- For threads: each tweet standalone but builds a narrative

**GOOD content** (match this energy):
"3 AM. Mom's in the hospital. They need ₹15,000 deposit. You have ₹2,400. Who do you call at 3 AM? Nobody. That's the point."

"Month end be like: checking account balance → closing the app → checking again hoping the number changed → it didn't"

**BAD content** (never do this):
"Apollo Cash to the rescue! Download now for instant loans!"
"Get quick disbursement with minimal documentation. Apply today!"
""",

    "seo": APOLLO_CASH_CONTEXT + """
You are **Draft** — the SEO content agent inside Blaze.

YOUR JOB: Write blog articles that rank on Google for high-intent personal finance keywords AND genuinely help the reader.

CONVERSATION STYLE:
- Ask what keyword to target, or suggest high-opportunity keywords
- Discuss search intent: is the searcher ready to borrow, or just learning?
- Explain your article angle before writing
- After writing, offer to adjust tone, add sections, or target a different angle

WHEN YOU WRITE ARTICLES, FOLLOW THESE RULES:

**Keyword strategy** — these are your priority keywords:
- "instant personal loan app India" (transactional)
- "loan without CIBIL score" (high intent)
- "emergency loan for salary delay" (problem-aware)
- "small loan app for gig workers" (audience-specific)
- "personal loan kaise le" (Hindi search intent)
- "safe loan apps India 2026" (comparison/trust)

**Article structure**:
- **Meta title** (under 60 chars, includes keyword)
- **Meta description** (under 155 chars)
- Start with the reader's pain — don't start with Apollo Cash
- Use ## and ### headings with keywords naturally placed
- Short paragraphs (2-3 sentences max)
- Include real scenarios as examples
- One section about how Apollo Cash helps (not the whole article)
- FAQ section with 4-5 questions people actually search
- Soft CTA at end — "worth exploring" not "download now"
- Word count: 1,200-1,800 words

**Tone**: Like Zerodha Varsity — educational, zero jargon, genuinely helpful. The reader should learn something even if they never use Apollo Cash.

**Article types you can write**:
- Educational: "How Personal Loans Work: A First-Timer's Guide"
- Problem-solving: "Salary Delayed? 5 Options Before Payday"
- Myth-busting: "No CIBIL Score? You Can Still Get a Loan. Here's How."
- Comparison: "Borrowing from Family vs Loan Apps — An Honest Look"
- Audience-specific: "Gig Worker's Guide to Managing Irregular Income"
""",

    "community": APOLLO_CASH_CONTEXT + """
You are **Rally** — the community engagement agent inside Blaze.

YOUR JOB: Find real conversations about money problems online and respond like a genuinely helpful person — not a brand account.

CONVERSATION STYLE:
- Ask which platforms and what types of threads to target
- Discuss the authenticity strategy: when to mention Apollo Cash, when to give pure advice
- Show the original thread/post context alongside your response
- After generating, ask if the tone feels authentic enough

WHEN YOU CREATE RESPONSES, FOLLOW THESE RULES:

**Platforms and their cultures**:
- **Reddit** (r/IndiaInvestments, r/india, r/personalfinanceindia): Casual, peer-to-peer. Users hate obvious marketing. Use "I was in a similar situation" framing.
- **Quora**: More detailed, educational. Users expect thorough answers with context.
- **Twitter/X**: Brief, empathetic, punchy. Match the emotional tone of the original tweet.
- **Facebook Groups** (gig workers, small business owners): Warm, community-oriented. Like talking to a neighbor.

**Response strategy**:
- **Always help first**. Solve their problem before any mention of Apollo Cash.
- Apollo Cash appears in ~70% of responses, as ONE option among 3-4 you suggest
- ~30% of responses should be PURE advice with NO brand mention at all — this builds trust
- When you mention Apollo Cash, share a "personal experience": "I used it when I was in a similar spot"
- Always warn against predatory apps (contacts/gallery access = red flag)
- Vary length: sometimes 2 lines, sometimes a detailed breakdown
- Never post links unless the thread specifically asks for app recommendations

**For each response, show**:
- **Platform** and community name
- **Original post** (the thread/question you're responding to)
- **Your response** (the actual reply)
- **Strategy note** (why this approach for this context)

**GOOD response example**:
Thread: "Need ₹20K for mom's medical bills, salary next week"
> "Really sorry about your mom. Hope she's doing better. Few options: (1) Ask HR for salary advance — many companies do this for medical emergencies. (2) Credit card cash advance if you have one, but interest is steep. (3) Instant loan apps like Apollo Cash, Fibe, KreditBee — I've used Apollo Cash and it was straightforward, got the money in 15 min. (4) Check if the hospital offers a payment plan. Whatever you do, avoid any app that asks for your contacts list."

**BAD response**: "Try Apollo Cash! Instant loans up to ₹2 lakh!"
""",

    "research": APOLLO_CASH_CONTEXT + """
You are **Freq** — the research and trends agent inside Blaze.

YOUR JOB: Track what Apollo Cash's target audience is talking about, what competitors are doing, and recommend content strategy adjustments.

CONVERSATION STYLE:
- Ask what they want to research: trends, sentiment, competitors, or strategy
- Present findings as clear insights with actionable recommendations
- Connect every finding to a specific content opportunity
- Suggest what Vortex, Draft, or Rally should create based on your findings

WHAT YOU CAN RESEARCH:

**1. Trending Topics**
- What financial events are happening now (festivals, tax season, school fees, wedding season)
- What viral content formats are working on Indian Instagram/YouTube
- What money-related conversations are trending on Twitter/Reddit
- Seasonal triggers that create cash crunches for our audience

**2. Audience Sentiment**
- What are gig workers posting about on social media?
- What questions are people asking on Reddit/Quora about loans?
- What language/slang do they use when talking about money?
- What are their biggest fears about borrowing?
- What would make them trust a loan app?

**3. Competitor Analysis**
- What are Slice, Fi Money, KreditBee, Fibe doing on social?
- What content formats are working for them?
- What gaps exist that Apollo Cash can fill?

**4. Strategy Recommendations**
- Based on engagement data, what should we do more/less of?
- What content types drive the most shares?
- What posting times work best for each segment?
- What new angles should we test?

**How to present findings**:
- Lead with the insight, not the data
- Every finding should end with "This means we should..."
- Group findings by theme, not by source
- Be specific: "Delivery workers are posting about monsoon bike breakdowns this week" not "transportation is trending"
- Recommend specific content pieces for Vortex, Draft, or Rally to create
""",
}

OUTPUT_RULES = """

OUTPUT FORMAT RULES (follow strictly):
- Always respond in proper Markdown format
- Use **bold** for key terms and emphasis
- Use ## and ### for section headers
- Use - for bullet lists (not *)
- Use 1. 2. 3. for numbered lists
- Never output raw JSON, code blocks, or technical data
- Add blank lines between paragraphs for breathing room
- Never use horizontal rules, dividers, or separator lines
- Never use decorative characters like ━━━ or ════
- Minimal emoji — at most 1-2 per response, only if natural
- Keep formatting clean — let whitespace do the work
- Be warm, specific, and actionable"""


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Conversational chat with full message history."""
    base_system = AGENT_PERSONAS.get(req.agent, AGENT_PERSONAS["social"])
    system = base_system + OUTPUT_RULES

    from agents.llm_client import generate

    # Build conversation for context
    conversation_parts = []
    for msg in req.messages:
        prefix = "User" if msg.role == "user" else "You"
        conversation_parts.append(f"{prefix}: {msg.content}")

    conversation_text = "\n".join(conversation_parts)

    # Detect if user is giving a specific content request vs just chatting
    last_msg = req.messages[-1].content if req.messages else ""
    is_generation_request = len(last_msg.split()) >= 5 and any(
        kw in last_msg.lower() for kw in [
            "generate", "create", "write", "make", "draft", "build",
            "post", "carousel", "reel", "meme", "thread", "article",
            "response", "respond", "reply", "find", "research",
            "analyze", "trend", "calendar", "schedule", "content",
        ]
    )

    # Check if this is a research/discovery request that needs live web data
    is_research_request = any(
        kw in last_msg.lower() for kw in [
            "find", "discover", "search", "look up", "browse", "scrape",
            "trending", "trend", "what are people", "reddit", "quora",
            "competitor", "research", "analyze online", "real threads",
        ]
    )

    live_data_context = ""
    if is_research_request and len(last_msg.split()) >= 4:
        try:
            from agents.web_scraper import research_live, discover_threads

            if any(kw in last_msg.lower() for kw in ["thread", "discover", "find", "reddit", "community"]):
                # Rally / community discovery
                discovery = discover_threads()
                if discovery.get("threads"):
                    thread_summaries = []
                    for t in discovery["threads"][:10]:
                        thread_summaries.append(
                            f"- **{t.get('title', '')}** (r/{t.get('subreddit', '')}, {t.get('score', 0)} upvotes, {t.get('num_comments', 0)} comments)\n  {t.get('body', '')[:150]}..."
                        )
                    live_data_context = f"\n\n**LIVE DATA — I just scanned Reddit and found {discovery['discovered']} relevant threads:**\n\n" + "\n\n".join(thread_summaries)
            else:
                # Freq / general research
                topic = last_msg.lower().replace("research", "").replace("trending", "").replace("analyze", "").strip()
                if len(topic) < 5:
                    topic = "personal loan India"
                research = research_live(topic)

                reddit_posts = research.get("reddit", {}).get("posts", [])
                trends = research.get("google_trends", {}).get("trends", {})

                parts = []
                if reddit_posts:
                    parts.append(f"**LIVE Reddit Data** ({len(reddit_posts)} posts found):")
                    for p in reddit_posts[:8]:
                        parts.append(f"- **{p.get('title', '')}** (r/{p.get('subreddit', '')}, {p.get('score', 0)} upvotes)")

                if trends:
                    parts.append("\n**LIVE Google Trends Data:**")
                    for kw, data in trends.items():
                        parts.append(f"- **{kw}**: {data.get('trend', 'stable')} (current interest: {data.get('current', 'N/A')})")
                        related = research.get("google_trends", {}).get("related_queries", {}).get(kw, {})
                        if related.get("rising_queries"):
                            parts.append(f"  Rising queries: {', '.join(related['rising_queries'][:3])}")

                if parts:
                    live_data_context = "\n\n" + "\n".join(parts)
        except Exception as e:
            live_data_context = f"\n\n(Web scraping attempted but hit an issue: {str(e)[:100]})"

    if is_generation_request:
        instruction = "The user has given a specific content request. Generate the content NOW — do not ask clarifying questions. Produce your best work immediately. Be thorough and detailed."
    elif is_research_request and live_data_context:
        instruction = "I just scraped the live web for real data. Use the LIVE DATA below to provide genuine, data-backed insights. Reference specific posts, trends, and numbers from the real data. Do NOT make up data — use what was actually found."
    else:
        instruction = "The user is chatting. Respond conversationally. If greeting you, introduce yourself briefly and ask what they'd like to create."

    prompt = f"""Conversation so far:
{conversation_text}
{live_data_context}

{instruction}

Format your output beautifully using Markdown."""

    response = generate(system, prompt, temperature=0.8, max_tokens=4000)
    return {"response": response}


# ── Live Web Scraping endpoints ─────────────────────────────────

class BrowseRequest(BaseModel):
    task: str
    agent: str = "research"


class RedditRequest(BaseModel):
    subreddit: str = "personalfinanceindia"
    query: str = ""
    limit: int = 10


class TrendsRequest(BaseModel):
    keywords: str = "personal loan India"


@app.post("/api/browse/reddit")
async def browse_reddit(req: RedditRequest):
    """Fetch real Reddit posts — live data, no API key needed."""
    from agents.web_scraper import scrape_reddit, search_reddit
    if req.query:
        posts = search_reddit(req.query, subreddit=req.subreddit, limit=req.limit)
    else:
        posts = scrape_reddit(req.subreddit, limit=req.limit)
    return {"status": "live", "source": "reddit", "posts": posts, "count": len(posts)}


@app.post("/api/browse/trends")
async def browse_trends(req: TrendsRequest):
    """Fetch real Google Trends data — live, no API key needed."""
    from agents.web_scraper import get_google_trends
    keywords = [k.strip() for k in req.keywords.split(",")]
    trends = get_google_trends(keywords)
    return {"status": "live", "source": "google_trends", "data": trends}


@app.post("/api/browse/research")
async def browse_research(req: BrowseRequest):
    """Full live research sweep — Reddit + Google Trends."""
    from agents.web_scraper import research_live
    results = research_live(req.task)
    return {"status": "live", "source": "web_scraping", "data": results}


@app.post("/api/browse/discover")
async def browse_discover():
    """Discover real threads about money problems across Reddit."""
    from agents.web_scraper import discover_threads
    results = discover_threads()
    return {"status": "live", "source": "reddit_live", "data": results}


# ── Orchestrator endpoint (the harness loop) ────────────────────

@app.post("/api/orchestrate")
async def orchestrate(req: GoalRequest):
    """Run the full harness loop for a user goal.

    This is the main entry point — it captures intent, loads memory,
    runs the ReAct loop, executes tools, and returns results.
    """
    run = orchestrator.run(req.goal)
    return orchestrator.get_run_summary(run)


# ── Direct agent endpoints ──────────────────────────────────────

@app.post("/api/social/generate")
async def generate_social(req: SocialPostRequest):
    """Generate social media posts directly (bypassing orchestrator)."""
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
    """Generate a weekly content calendar."""
    from agents.social_media_agent import generate_weekly_calendar
    calendar = generate_weekly_calendar()
    return {"status": "success", "calendar": calendar}


@app.post("/api/seo/article")
async def generate_article(req: ArticleRequest):
    """Generate an SEO article."""
    from agents.seo_agent import generate_article as gen_article, save_article, ARTICLE_BRIEFS
    brief = {
        "keyword": req.keyword,
        "secondary_keywords": [],
        "language": req.language,
        "audience_segment": req.audience_segment,
        "article_type": req.article_type,
    }
    for b in ARTICLE_BRIEFS:
        if b["keyword"].lower() == req.keyword.lower():
            brief = b
            break
    article = gen_article(brief)
    json_path, md_path = save_article(article)
    return {"status": "success", "article": article, "json_path": json_path, "md_path": md_path}


@app.post("/api/seo/keywords")
async def keyword_analysis():
    """Run keyword analysis."""
    from agents.seo_agent import generate_keyword_analysis
    analysis = generate_keyword_analysis()
    return {"status": "success", "analysis": analysis}


@app.post("/api/community/responses")
async def generate_community(req: CommunityRequest):
    """Generate community responses."""
    from agents.community_agent import generate_responses, save_responses
    responses = generate_responses(
        count=req.count,
        platforms=[p.strip() for p in req.platforms.split(",")],
    )
    filepath = save_responses(responses)
    mentions = sum(1 for r in responses if r.get("response", {}).get("mentions_apollo_cash", False))
    return {
        "status": "success",
        "count": len(responses),
        "file": filepath,
        "mention_ratio": f"{mentions}/{len(responses)}",
        "responses": responses,
    }


@app.post("/api/community/discover")
async def discover_threads():
    """Run thread discovery."""
    from agents.community_agent import generate_thread_discovery
    discovery = generate_thread_discovery()
    return {"status": "success", "discovery": discovery}


# ── Research endpoints ──────────────────────────────────────────

@app.post("/api/research/trends")
async def research_trends():
    """Research trending topics and content opportunities."""
    from agents.research_agent import research_trending_topics, save_research
    trends = research_trending_topics()
    filepath = save_research(trends, "trending_topics")
    return {"status": "success", "trends": trends, "file": filepath}


@app.post("/api/research/sentiment/{segment}")
async def research_sentiment(segment: str):
    """Research audience sentiment for a segment."""
    from agents.research_agent import research_audience_sentiment, save_research
    sentiment = research_audience_sentiment(segment)
    filepath = save_research(sentiment, f"sentiment_{segment}")
    return {"status": "success", "sentiment": sentiment, "file": filepath}


@app.post("/api/research/adapt")
async def adapt_strategy():
    """Analyze engagement and adapt strategy."""
    from agents.research_agent import analyze_engagement_and_adapt, save_research
    mock_engagement = {
        "period": "last_7_days",
        "posts": [
            {"format": "reel", "theme": "salary delay", "likes": 2400, "shares": 180, "comments": 95},
            {"format": "carousel", "theme": "bike repair", "likes": 1800, "shares": 120, "comments": 60},
            {"format": "meme", "theme": "month end", "likes": 3200, "shares": 450, "comments": 200},
            {"format": "reel", "theme": "first loan experience", "likes": 3800, "shares": 520, "comments": 310},
        ],
    }
    adaptation = analyze_engagement_and_adapt(mock_engagement)
    filepath = save_research(adaptation, "engagement_adaptation")
    return {"status": "success", "adaptation": adaptation, "file": filepath}


# ── Data endpoints (read generated content) ─────────────────────

@app.get("/api/outputs/{agent_type}")
async def get_outputs(agent_type: str):
    """Get all generated outputs for an agent type."""
    output_dir = Path("output") / agent_type
    if not output_dir.exists():
        return {"files": [], "count": 0}

    files = []
    for f in sorted(output_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError:
                data = None
        files.append({
            "filename": f.name,
            "path": str(f),
            "size_bytes": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "data": data,
        })
    return {"files": files, "count": len(files)}


@app.get("/api/outputs/{agent_type}/{filename}")
async def get_output_file(agent_type: str, filename: str):
    """Get a specific output file."""
    filepath = Path("output") / agent_type / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath, "r", encoding="utf-8") as f:
        if filename.endswith(".json"):
            return json.load(f)
        return {"content": f.read()}


# ── Memory & harness state ──────────────────────────────────────

@app.get("/api/memory")
async def get_memory():
    """Get all memory entries."""
    return memory.all_memories()


@app.get("/api/runs")
async def get_runs():
    """Get all harness runs."""
    return {
        "runs": [orchestrator.get_run_summary(r) for r in orchestrator.runs],
        "count": len(orchestrator.runs),
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "llm_provider": llm.name(),
        "timestamp": datetime.now().isoformat(),
    }


# ── Pipeline (run all agents) ──────────────────────────────────

@app.post("/api/pipeline/run")
async def run_pipeline():
    """Run the full marketing pipeline through the orchestrator."""
    goal = """Run the complete Apollo Cash marketing pipeline:
1. Generate 18 social media posts across all audience segments and formats
2. Generate 3 SEO articles for top keywords
3. Generate 12 community responses across all platforms
4. Generate a weekly content calendar
5. Run keyword analysis
6. Run thread discovery

Execute all tools needed and report results."""
    run = orchestrator.run(goal)
    return orchestrator.get_run_summary(run)
