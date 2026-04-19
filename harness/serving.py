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

    # For community/research: fetch REAL data and build response with Python (don't trust LLM to format it)
    if is_research:
        try:
            from agents.web_scraper import research_live, discover_threads

            is_community = any(kw in last_msg.lower() for kw in ["thread", "discover", "find", "reddit", "community", "respond", "reply"])

            if is_community:
                data = discover_threads()
                threads = [t for t in data.get("threads", []) if "error" not in t and t.get("title")][:5]

                if threads:
                    # Build response with REAL data — Python formats the structure, LLM only writes replies
                    parts = [f"I scanned Reddit and found **{data['discovered']} real threads**. Here are the top {len(threads)} with my responses:\n"]

                    for i, t in enumerate(threads):
                        parts.append(f"### Thread {i+1} — r/{t.get('subreddit', '')}")
                        parts.append(f"**\"{t['title']}\"** — {t.get('score', 0)} upvotes, {t.get('num_comments', 0)} comments")
                        if t.get("author"):
                            parts.append(f"*by u/{t['author']}*")
                        if t.get("body"):
                            parts.append(f"\n> {t['body'][:250]}{'...' if len(t.get('body','')) > 250 else ''}\n")

                        # Generate ONLY the reply using LLM
                        mention_apollo = i < 3  # First 3 mention Apollo, last 2 pure advice
                        reply_prompt = f"""Write a single Reddit reply to this post. Sound like a real person, not a brand.
Post title: "{t['title']}"
Post body: "{t.get('body', '')[:300]}"
Subreddit: r/{t.get('subreddit', '')}
{"Mention Apollo Cash naturally as ONE option among others." if mention_apollo else "Do NOT mention Apollo Cash. Give pure helpful advice only."}
Keep it {"short (2-3 sentences)" if i % 2 == 0 else "detailed (4-6 sentences)"}. No URLs. No numbered lists for every response — vary the style."""

                        reply = generate(system, reply_prompt, temperature=0.9, max_tokens=400)
                        reply = strip_promotional_language(reply)
                        parts.append(f"**My response:**\n{reply}")
                        parts.append(f"\n*Strategy: {'Mentions Apollo Cash as one option' if mention_apollo else 'Pure advice — trust building, no brand mention'}*\n")

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

                insights = generate(system, insight_prompt, temperature=0.8, max_tokens=1000)
                parts.append("\n### Content Recommendations\n")
                parts.append(insights)

                response = "\n".join(parts)
                response = strip_promotional_language(response)
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

    response = generate(system, prompt, temperature=0.8, max_tokens=4000)

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

@app.get("/api/health")
async def health():
    return {"status": "healthy", "llm_provider": llm.name(), "timestamp": datetime.now().isoformat()}

@app.post("/api/pipeline/run")
async def run_pipeline():
    goal = "Run all agents: generate 5 social posts, 1 SEO article, 5 community responses, weekly calendar, keyword analysis, thread discovery"
    run = orchestrator.run(goal)
    return orchestrator.get_run_summary(run)
