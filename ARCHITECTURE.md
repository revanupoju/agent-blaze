# Agent Blaze — Architecture Overview

## System Overview

Agent Blaze is an AI-powered marketing agent platform for Apollo Cash. It uses four specialized AI agents to continuously generate and distribute marketing content across channels.

## The Four Agents

| Agent | Name | Purpose |
|-------|------|---------|
| Social Media | **Vortex** | Generates Instagram carousels, reel scripts, memes, Twitter threads, WhatsApp forwards, YouTube Shorts |
| SEO Writer | **Draft** | Writes 1200-1800 word blog articles targeting high-intent personal finance keywords with proper SEO structure |
| Community | **Rally** | Finds real conversations on Reddit, Quora, Twitter and crafts authentic, helpful responses |
| Research | **Freq** | Analyzes trends, audience sentiment, competitor strategies, and recommends content adjustments |

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: SERVING                                           │
│  Next.js (Vercel) + FastAPI (Railway)                       │
│  Login → Dashboard → Chat UI → Agent responses              │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: ORCHESTRATION                                     │
│  ReAct Loop: Intent → Memory → Reason → Execute → Verify   │
│  Routes goals to the right agent, manages tool calling      │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: CONTEXT & MEMORY                                  │
│  Short-term (session) + Long-term (persistent to disk)      │
│  Tracks content history, engagement data, strategy          │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: TOOL LAYER                                        │
│  14 callable tools across all agents                        │
│  Content generation, SEO, community, research, analytics    │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: LLM CORE                                          │
│  Cerebras (Llama 3.1) — cloud, ultra-fast                   │
│  Ollama (Llama 3.1) — local, offline, private               │
│  Swappable: change one env variable to switch providers     │
└─────────────────────────────────────────────────────────────┘
```

## Harness Loop (ReAct Pattern)

Every user goal goes through this loop:

```
User Goal → Intent Capture → Load Memory → LLM Reasoning
    → Tool Execution → Verify Output → Persist to Memory
    → Done or Loop (repeat until goal met)
```

- **Intent Capture**: Parse what the user wants (which agent, what content type, what audience)
- **Load Memory**: Inject prior content history, engagement data, strategy insights
- **LLM Reasoning**: The model plans what to do and which tools to call
- **Tool Execution**: Run the selected tool (e.g., `generate_social_posts`)
- **Verify**: Check output quality (tone, format, no corporate speak)
- **Persist**: Save results to memory for future context

## Tool Registry (14 Tools)

### Vortex (Social Media)
- `generate_social_posts` — Create posts across formats and segments
- `generate_content_variations` — A/B variations of the same scenario
- `generate_weekly_calendar` — Full 7-day content schedule

### Draft (SEO)
- `generate_seo_article` — Full article from a target keyword
- `keyword_analysis` — Priority scoring and competition assessment

### Rally (Community)
- `generate_community_responses` — Authentic thread responses
- `discover_threads` — Find relevant conversations daily

### Freq (Research)
- `research_trends` — Trending topics and viral formats
- `research_audience_sentiment` — Segment-specific insights
- `adapt_strategy` — Engagement-based content adjustments

### Utilities
- `list_audience_segments` — View target segments
- `list_seo_keywords` — View keyword targets
- `list_communities` — View target communities
- `read_output` — Read generated output files

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React, Tailwind CSS, Zustand |
| Backend | Python, FastAPI, Uvicorn |
| LLM | Cerebras (Llama 3.1 8B), Ollama (local) |
| Hosting | Vercel (frontend), Railway (backend) |
| Fonts | Instrument Serif (display), Sora (body) |

## Deployment

```
agentblaze.vercel.app (Frontend)
    ↓ API calls
agent-blaze-api-production.up.railway.app (Backend)
    ↓ LLM calls
Cerebras Cloud / Ollama Local (LLM inference)
```

## Target Audience Segments

1. **Gig Workers** — Zomato/Swiggy riders, Uber/Ola drivers, delivery partners
2. **Salaried (Tier 2/3)** — Earning ₹15K-40K/month in smaller cities
3. **Self-Employed** — Kirana owners, auto drivers, street vendors
4. **NTC Youth (21-35)** — First-time borrowers, no credit history

## Self-Improvement Engine (Autoresearch Pattern)

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch), every piece of generated content goes through a recursive improvement loop:

```
1. Generate content (the "experiment")
2. Evaluate quality (score 1-10 on relatability, authenticity, emotion, specificity)
3. If score >= 7 → keep (like val_bpb improving)
4. If score < 7 → identify weaknesses → rewrite → re-evaluate
5. Keep best version, discard regressions
6. Log every experiment to experiment_log.jsonl
```

This means the agents don't just generate once — they **iterate on their own output** until it meets quality standards. The experiment log tracks:
- Total experiments run
- Keep vs discard ratio
- Average quality score per agent
- Improvement trends over time

The loop caps at 2 iterations in chat (for speed) and 5 iterations in batch mode.

## LLM Failover Chain

Like Luna's 4-provider failover:

```
Cerebras (Qwen 3 235B / Llama 3.1 8B)
    ↓ on 429 or error
Ollama (local Llama 3.1)
    ↓ on error
Fail gracefully with message
```

## Content Strategy

- Content is **conversational first** — agents ask clarifying questions before generating
- **70% of community responses** mention Apollo Cash naturally, **30% give pure advice** for trust building
- Never uses "Apply now", "Download today" or any hard calls to action
- Every post tells a **story**, not an ad
- Supports both **English** (default) and **Hinglish** (toggle)

## How to Run Locally

```bash
# Backend
cd "AI Marketing Agent"
pip install -r requirements.txt
cp .env.example .env  # Add CEREBRAS_API_KEY
python3 server.py     # FastAPI on :8000

# Frontend
cd dashboard
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev  # Next.js on :3000
```
