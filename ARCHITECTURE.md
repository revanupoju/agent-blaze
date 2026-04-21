# Agent Blaze

Architecture Overview · April 2026 · Sai Revanth Anupoju

## What Blaze Is

Blaze is an AI-powered marketing agent platform built for Apollo Cash. Six specialized AI agents — Vortex, Draft, Rally, Freq, Pulse, and Dispatch — continuously generate, refine, and distribute marketing content across channels.

Every piece of content is grounded through real web data (Reddit, Google Trends) and refined through a recursive self-improvement loop inspired by Karpathy's autoresearch. The agents don't just generate once — they evaluate their own output, identify weaknesses, and iterate until quality hits 9/10.

## Tech Stack

| Layer | Choice |
|-------|--------|
| **Frontend** | Next.js 16 on Vercel, TypeScript, Tailwind CSS 4 |
| **Backend** | Python 3.11, FastAPI on Railway |
| **LLM** | Qwen 3 235B on Cerebras (primary), Llama 3.1 8B failover |
| **Agent Memory** | Mem0 (semantic vector memory) + server-side session store |
| **Publishing** | Postiz (self-hosted on VPS) — X, LinkedIn, Instagram, Reddit |
| **Web Scraping** | Reddit JSON API, pytrends (Google Trends), BeautifulSoup |
| **State** | Zustand with localStorage persistence |
| **Fonts** | Instrument Serif (display), Sora (body) |
| **Hosting** | Vercel (frontend), Railway (backend), Hostinger VPS (Postiz) |

## The Six Agents

| Agent | Name | Purpose |
|-------|------|---------|
| Social Media | **Vortex** | Instagram carousels, reel scripts, memes, Twitter threads, WhatsApp forwards |
| SEO Writer | **Draft** | Blog articles targeting high-intent personal finance keywords |
| Community | **Rally** | Find real Reddit/Quora conversations and respond authentically |
| Research | **Freq** | Track trends, audience sentiment, recommend content strategy |
| Email | **Pulse** | Welcome emails, drip sequences, newsletters, re-engagement campaigns |
| Publisher | **Dispatch** | Connect social channels (OAuth), post content, schedule publishing |

## 3-Layer Memory Architecture

### Layer 1: Chat Session Memory (Server-Side)
- Server maintains conversation history per thread (last 20 messages)
- Enables follow-ups: "make it shorter", "change the city to Pune"
- Stored in-memory on Railway, keyed by thread ID
- 50 concurrent sessions, auto-evicts oldest

### Layer 2: Semantic Long-Term Memory (Mem0)
- Every conversation auto-stored in Mem0 after response
- Each agent has its own memory namespace (`agent-social`, `agent-seo`, etc.)
- Semantic vector search — finds relevant past content by meaning, not keywords
- Cross-agent memory: Vortex can recall what Freq researched
- Memories auto-extracted from conversations (Mem0 handles this)

### Layer 3: Autoresearch Experiment Log
- Every content generation logged to `experiment_log.jsonl`
- Tracks: iteration count, quality score, keep/discard status, weaknesses
- Winning patterns influence future generations
- Viewable via `/api/experiments` endpoint

**Memory flow per request:**
```
User asks "Write a reel about bike repairs"
    ↓
1. Mem0 search: find relevant past memories for this agent
2. Inject memories into system prompt as context
3. LLM generates with awareness of past content (avoids repetition)
4. Response stored back to Mem0 for future recall
5. Session history updated for follow-up context
```

## The Agent Harness (5 Layers)

```
Layer 1 — Serving        FastAPI REST + Next.js dashboard
Layer 2 — Orchestration  7-step ReAct loop, intent classification
Layer 3 — Memory         Mem0 semantic memory + session store + experiment log
Layer 4 — Tools          Web scraper, content generators, Postiz publisher
Layer 5 — LLM Core       Cerebras failover chain (Qwen 3 → Llama 3.1 → Ollama)
```

## The 7 Steps: What Happens When You Hit Send

| Step | Name | What Happens |
|------|------|--------------|
| 1 | **User goal** | Raw text from chat input + session_id |
| 2 | **Intent capture** | Classify: greeting, generation, research, connect, or post |
| 3 | **Load memory** | Mem0 semantic search → inject relevant memories + session history |
| 4 | **Live data fetch** | For Rally/Freq: scrape Reddit and Google Trends for real data |
| 5 | **LLM reasoning** | Failover chain generates content with full context |
| 6 | **Post-processing** | Strip promotional language, run autoresearch (up to 5 iterations, threshold 9.0) |
| 7 | **Store & return** | Save to Mem0 + session store, log experiment, return response |

## Self-Improvement Engine (Autoresearch Pattern)

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):

```
Iteration 1: Generate content → Evaluate on 5 dimensions → Score 6.5/10
             Weaknesses: "too promotional, vague amounts"
             Score < 9.0 → IMPROVE

Iteration 2: Rewrite fixing weaknesses → Score 7.8/10
             Weaknesses: "CTA still present"
             7.8 > 6.5 → KEEP (discard old)
             Score < 9.0 → IMPROVE

Iteration 3: Rewrite again → Score 9.2/10
             Above threshold → STOP, return best version
```

**Evaluation dimensions (agent-specific):**

For social/SEO/community:
- Relatability, Authenticity, Emotional Impact, Specificity, Non-promotional

For email:
- Relatability, Tone (friend vs corporation), Emotional Impact, Specificity, Readability

**Training results:**
| Agent | Avg Score | Best Score |
|-------|-----------|------------|
| Vortex | 8.8/10 | 9.0 |
| Draft | 9.0/10 | 9.0 |
| Rally | 7.7/10 | — |
| Pulse | 7.6/10 | 8.8 |

## Dispatch: Social Publishing Pipeline

Dispatch handles channel management and publishing — no external UI needed.

**Connect flow:**
```
User clicks X button → Frontend calls /api/connect/x
→ Backend authenticates with Postiz → Gets OAuth URL
→ User redirected to Twitter/LinkedIn login → Authorizes
→ Channel connected → Shows in Dispatch with platform logo
```

**Post flow:**
```
User says "Post this on X" → Dispatch finds content from chat history
→ Uploads media to Postiz if attached → Posts via Postiz API
→ Returns confirmation with post ID
```

**Supported platforms:** X (Twitter), LinkedIn, Instagram, Facebook, Reddit, YouTube, TikTok, Threads, Pinterest

## Regulatory Compliance (All Agents)

- Apollo Finvest is an NBFC, NOT a SEBI-registered investment advisor
- Agents NEVER give investment advice (mutual funds, stocks, SIPs, portfolio allocation)
- Rally filters out investment threads — only responds to lending/emergency topics
- All agents redirect investment questions to SEBI-registered advisors
- No fabricated data — if Reddit returns nothing relevant, agents say so honestly

## LLM Failover Chain

```
Cerebras (Qwen 3 235B) — primary, ~2,200 tok/sec
    ↓ on 429 rate limit (retry with 1.5s backoff, 3 attempts)
Cerebras (Llama 3.1 8B) — fast fallback
    ↓ on error
Ollama (local) — offline fallback
    ↓ on error
Graceful error message
```

## Promotional Language Filter

Post-processing regex filter strips ad copy the LLM inserts despite prompts. Catches 25+ patterns:
- "Game-changing", "Revolutionary", "Hassle-free"
- "Get started today", "Apply now", "Download now"
- "Competitive interest rates", "Take control of your financial future"
- Any line that's a pure CTA

## Live Web Scraping (No API Keys)

| Source | Method | What It Gets |
|--------|--------|-------------|
| **Reddit** | JSON API | Real posts, scores, comments from r/personalfinanceindia, r/IndiaInvestments |
| **Google Trends** | pytrends | Interest over time, rising queries for India |
| **Pullpush.io** | REST API | Reddit archive fallback when direct API is blocked |

Relevance filtering: only finance/lending threads pass through. Investment, politics, dating threads are excluded.

## Deployment

```
agentblaze.vercel.app (Next.js frontend)
    ↓ API calls
agent-blaze-api-production.up.railway.app (FastAPI backend)
    ↓ LLM calls                    ↓ Memory
Cerebras Cloud                  Mem0 Cloud
    ↓ web scraping                  ↓ publishing
Reddit + Google Trends          srv1317892.hstgr.cloud (Postiz on VPS)
                                    ↓ OAuth
                                X, LinkedIn, Instagram...
```

## Repository Structure

```
/agents
  social_media_agent.py    — Vortex content generation
  seo_agent.py             — Draft article generation
  community_agent.py       — Rally response generation
  research_agent.py        — Freq trend analysis
  web_scraper.py           — Live Reddit + Google Trends scraping
  self_improve.py          — Autoresearch self-improvement loop (5 iters, 9.0 threshold)
  auto_publisher.py        — Platform-specific post handlers
  llm_client.py            — Multi-provider LLM client with failover

/harness
  serving.py               — FastAPI endpoints, agent personas, session memory
  orchestrator.py          — ReAct orchestration loop
  memory.py                — Mem0 semantic memory integration
  tools.py                 — Tool definitions
  llm_core.py              — Provider-agnostic LLM interface

/dashboard
  src/app/page.tsx          — Main app with auth + OAuth redirect handling
  src/components/chat/      — Chat UI with streaming, media upload, platform connect
  src/components/layout/    — Sidebar + navigation
  src/components/views/     — Dashboard home, calendar, publish view
  src/stores/ui-store.ts    — Zustand with localStorage persistence
  public/                   — Agent SVG icons + platform logos

/config
  settings.py              — Audience segments, keywords, schedules

/data/memory               — Fallback memory store (JSON)
/output/experiments         — Autoresearch experiment logs
```
