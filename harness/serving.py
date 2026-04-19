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

NEVER fabricate URLs. Do NOT link to apollocash.com. Just mention "Apollo Cash" by name.
"""

AGENT_PERSONAS = {
    "social": APOLLO_CONTEXT + """
You are **Vortex** — the social media agent.

Create content that makes people think "this is my life." Write like a 27-year-old friend, not a brand.

Content rules:
- Tell ONE story per post. One person, one problem, one moment.
- Use specific details: ₹7,500 not "some money." Wednesday 11 PM, not "one day."
- Show emotion: shame of asking family, relief when sorted, anxiety watching due dates
- Apollo Cash in ~60% of posts. 40% pure relatable content, NO brand.
- NEVER: "Apply now", "Download", "Get started", hard CTAs
- End with feeling or question, never a CTA
- Each post must sound like a DIFFERENT person wrote it

Formats: Carousel (5-6 slides), Reel script (hook + scene + dialogue), Meme, Twitter thread, WhatsApp forward, YouTube Short""",

    "seo": APOLLO_CONTEXT + """
You are **Draft** — the SEO article agent.

Write articles that rank AND genuinely help. Like Zerodha Varsity — educational, zero jargon.

Rules:
- Start with the reader's pain, not Apollo Cash
- Short paragraphs (2-3 sentences max)
- Meta title under 60 chars with keyword
- Include real scenarios as examples
- One section about Apollo Cash (not the whole article)
- FAQ section with 4-5 real questions
- 1,200-1,800 words""",

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

    "research": APOLLO_CONTEXT + """
You are **Freq** — the research agent.

Track what Apollo Cash's audience talks about and recommend content.

Rules:
- When live web data is provided, use ONLY that data — do not fabricate posts or subreddits
- Reference exact post titles, scores, and subreddit names from real data
- Every finding should end with a content recommendation
- Be specific: "Delivery workers posting about monsoon breakdowns this week" not "transportation trending"
- Recommend specific pieces for Vortex, Draft, or Rally to create""",
}

OUTPUT_RULES = """

FORMAT: Use clean Markdown. **Bold** for emphasis. ## headers. - bullets.
No horizontal rules. No decorative characters. No raw JSON. Minimal emoji.
Let whitespace do the work."""


# ── Self-Improvement (inspired by Karpathy's autoresearch) ──────

def self_evaluate_and_improve(content: str, agent: str) -> str:
    """Evaluate content quality and improve if below threshold.
    Runs a generate→evaluate→improve loop, keeping the best version.
    """
    from agents.llm_client import generate

    eval_prompt = f"""Rate this marketing content 1-10 on: relatability, authenticity, emotional impact, specificity.
Give ONE number (the average) and list 2 specific weaknesses.
Format: SCORE: X/10 then WEAKNESSES: then the list.

Content:
{content[:1500]}"""

    try:
        evaluation = generate(
            "You are a strict content quality evaluator. Be harsh but specific.",
            eval_prompt, temperature=0.3, max_tokens=300
        )

        # Extract score
        import re
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', evaluation)
        score = float(score_match.group(1)) if score_match else 6.0

        if score >= 7.0:
            return content  # Good enough

        # Below threshold — improve
        improved = generate(
            AGENT_PERSONAS.get(agent, AGENT_PERSONAS["social"]) + OUTPUT_RULES,
            f"""This content scored {score}/10. The evaluation said:
{evaluation}

Rewrite it to fix the weaknesses. Make it more specific, more emotional, more human.
Output ONLY the improved content:

{content[:1500]}""",
            temperature=0.9, max_tokens=3000
        )
        return improved if improved and len(improved) > 50 else content
    except Exception:
        return content


# ── Chat Endpoint ───────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Conversational chat with live web data and self-improvement."""
    base_system = AGENT_PERSONAS.get(req.agent, AGENT_PERSONAS["social"])
    system = base_system + OUTPUT_RULES

    from agents.llm_client import generate
    import os

    # Override model if specified
    if req.model:
        parts = req.model.split(":")
        if len(parts) == 2:
            os.environ["LLM_PROVIDER"] = parts[0]
            os.environ["CEREBRAS_MODEL"] = parts[1]
            if parts[0] == "ollama":
                os.environ["OLLAMA_MODEL"] = parts[1]

    # Build conversation
    conversation_parts = []
    for msg in req.messages:
        prefix = "User" if msg.role == "user" else "You"
        conversation_parts.append(f"{prefix}: {msg.content}")
    conversation_text = "\n".join(conversation_parts)

    last_msg = req.messages[-1].content if req.messages else ""

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

    # Fetch live web data for research requests
    live_context = ""
    if is_research:
        try:
            from agents.web_scraper import research_live, discover_threads

            if any(kw in last_msg.lower() for kw in ["thread", "discover", "find", "reddit", "community", "respond"]):
                data = discover_threads()
                if data.get("threads"):
                    lines = [f"\n\n**LIVE REDDIT DATA (scraped just now, {data['discovered']} threads found):**\n"]
                    for t in data["threads"][:12]:
                        if "error" not in t:
                            lines.append(f"- **\"{t['title']}\"** — r/{t.get('subreddit','')} — {t.get('score',0)} upvotes, {t.get('num_comments',0)} comments")
                            if t.get("body"):
                                lines.append(f"  Post: {t['body'][:200]}")
                    live_context = "\n".join(lines)
            else:
                topic = " ".join(w for w in last_msg.lower().split() if w not in ["research","trending","analyze","what","are","people","about","on","right","now","the"])
                if len(topic) < 5:
                    topic = "personal loan India"
                data = research_live(topic)

                lines = ["\n\n**LIVE WEB DATA (scraped just now):**\n"]

                reddit_posts = data.get("reddit", {}).get("posts", [])
                if reddit_posts:
                    lines.append(f"**Reddit** ({len(reddit_posts)} posts):")
                    for p in reddit_posts[:10]:
                        if "error" not in p:
                            lines.append(f"- \"{p['title']}\" — r/{p.get('subreddit','')} — {p.get('score',0)} upvotes")

                trends = data.get("google_trends", {}).get("trends", {})
                if trends:
                    lines.append("\n**Google Trends (India, last 7 days):**")
                    for kw, d in trends.items():
                        lines.append(f"- \"{kw}\": {d.get('trend','stable')} (interest score: {d.get('current','N/A')}/100)")

                related = data.get("google_trends", {}).get("related_queries", {})
                if related:
                    for kw, r in related.items():
                        if r.get("rising_queries"):
                            lines.append(f"- Rising searches for \"{kw}\": {', '.join(r['rising_queries'][:4])}")

                live_context = "\n".join(lines)
        except Exception as e:
            live_context = f"\n\n(Web scraping error: {str(e)[:100]})"

    # Build instruction
    if is_generation:
        instruction = "Generate the content NOW. Do not ask questions. Be thorough, specific, and emotional."
    elif is_research and live_context:
        instruction = """USE THE LIVE DATA BELOW. These are REAL posts from Reddit and REAL trends from Google.
Reference the EXACT titles, subreddits, and scores shown. Do NOT invent data.
Present insights based on what you actually see in the data."""
    else:
        instruction = "Respond conversationally. If greeting, introduce yourself briefly and ask what they'd like to create."

    prompt = f"""Conversation:
{conversation_text}
{live_context}

{instruction}"""

    response = generate(system, prompt, temperature=0.8, max_tokens=4000)

    # Self-improvement: evaluate and improve if it's a generation request
    if is_generation and len(response) > 200:
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

@app.get("/api/health")
async def health():
    return {"status": "healthy", "llm_provider": llm.name(), "timestamp": datetime.now().isoformat()}

@app.post("/api/pipeline/run")
async def run_pipeline():
    goal = "Run all agents: generate 5 social posts, 1 SEO article, 5 community responses, weekly calendar, keyword analysis, thread discovery"
    run = orchestrator.run(goal)
    return orchestrator.get_run_summary(run)
