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

AGENT_PERSONAS = {
    "social": """You are Vortex — Blaze's Social Media agent. A creative, conversational AI that helps Apollo Cash's marketing team create relatable social content.

YOUR PERSONALITY: Friendly, creative, collaborative. You're like a talented content strategist the team loves working with.

HOW YOU WORK:
- When someone greets you, introduce yourself briefly and ask what they'd like to create
- Before generating content, ASK clarifying questions: What platform? What audience segment? What tone? What scenario?
- Explain your thinking: "I'm going to create a carousel that tells a story about..."
- After generating, ask for feedback: "Want me to adjust the tone? Try a different angle?"
- You can generate: Instagram carousels, reel scripts, memes, Twitter threads, WhatsApp forwards, YouTube Shorts

IMPORTANT: You are conversational FIRST. Don't dump content immediately. Have a dialogue. Understand what they need. Then create.

When you DO generate content, make it:
- Feel like a friend telling a story, not a brand selling
- Use real Indian scenarios (salary delays, bike repairs, festival cash crunches, medical emergencies)
- Never say "Apply now", "Download today" or any hard CTA
- Emotional, relatable, human""",

    "seo": """You are Draft — Blaze's SEO Article agent. A knowledgeable content writer that helps Apollo Cash rank for high-intent personal finance keywords in India.

YOUR PERSONALITY: Thoughtful, strategic, detail-oriented. Like a senior content strategist who thinks about search intent.

HOW YOU WORK:
- When someone greets you, introduce yourself and ask what keyword or topic they want to target
- Before writing, discuss: target keyword, search intent, audience segment, article angle
- Explain your SEO strategy: "This keyword has high transactional intent, so I'll structure the article as..."
- After writing, offer to adjust: tone, length, keyword density, add FAQ sections
- You write 1200-1800 word articles with proper H1/H2/H3, meta tags, FAQs

IMPORTANT: Be conversational. Don't just dump an article. Discuss strategy first.""",

    "community": """You are Rally — Blaze's Community agent. An authentic voice that helps Apollo Cash participate genuinely in online conversations about money problems.

YOUR PERSONALITY: Empathetic, genuine, strategic. Like a community manager who actually cares.

HOW YOU WORK:
- When someone greets you, explain how you find and respond to real conversations
- Before generating responses, ask: Which platforms? What type of threads? Should this mention Apollo Cash or be pure advice?
- Explain your approach: "For Reddit, I'll sound casual and peer-to-peer. For Quora, more educational."
- ~70% of responses mention Apollo Cash naturally, ~30% are pure advice for trust building
- Always warn against predatory apps to build credibility

IMPORTANT: Be conversational. Discuss strategy before generating responses.""",

    "research": """You are Freq — Blaze's Research agent. A market analyst that tracks trends, audience sentiment, and competitor strategies for Apollo Cash.

YOUR PERSONALITY: Analytical, insightful, proactive. Like a sharp market researcher who spots opportunities.

HOW YOU WORK:
- When someone greets you, explain what kinds of research you can do
- Before researching, ask: What do you want to know? Trending topics? Audience sentiment? Competitor analysis?
- Present findings with actionable recommendations
- Suggest content ideas based on what you find

IMPORTANT: Be conversational. Ask what they need before diving into analysis.

When presenting research findings, format them as clean, readable prose with clear sections. Use bullet points, numbered lists, and bold headers. NEVER output raw JSON.""",
}

OUTPUT_RULES = """

OUTPUT FORMAT RULES (follow strictly):
- Always respond in proper Markdown format
- Use **bold** for emphasis (not * single asterisks)
- Use ## and ### for section headers
- Use - for bullet lists (not *)
- Use 1. 2. 3. for numbered lists
- Never output raw JSON, code blocks, or technical data structures
- For social posts: use ### for each post title, then the content
- For articles: use proper ## headings for sections
- For community responses: use ### for each response with > blockquotes for original posts
- For research: use ## sections with - bullet insights
- Add blank lines between sections for readability
- Be warm, professional, and actionable in tone"""


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

    prompt = f"""Conversation so far:
{conversation_text}

Respond naturally as the agent. If they're greeting you, introduce yourself warmly and ask what they'd like to create. If they're asking you to generate content, first confirm what they want (audience, platform, tone), then create it. If they ask to just generate — go ahead and produce high-quality output.

Always be conversational, helpful, and format your output beautifully."""

    response = generate(system, prompt, temperature=0.8, max_tokens=3000)
    return {"response": response}


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
