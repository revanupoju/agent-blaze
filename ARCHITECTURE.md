# Agent Blaze

Architecture Overview · April 2026 · Sai Revanth Anupoju

## What Blaze Is

Blaze is an AI-powered marketing agent platform built for Apollo Cash. Six specialized AI agents — Vortex, Draft, Rally, Freq, Pulse, and Dispatch — continuously generate, refine, and distribute marketing content across channels.

Every piece of content is grounded through real web data (Reddit, Google Trends, HackerNews, YouTube, X Trends, Economic Times via Browserbase) and refined through a recursive self-improvement loop inspired by Karpathy's autoresearch. The agents don't just generate once — they evaluate their own output, identify weaknesses, and iterate until quality hits 9/10.

## Tech Stack

| Layer | Choice |
|-------|--------|
| **Frontend** | Next.js 16 on Vercel, TypeScript, Tailwind CSS 4 |
| **Backend** | Python 3.11, FastAPI on Railway |
| **LLM** | Qwen 3 235B on Cerebras (~2,200 tok/sec), Llama 3.1 8B failover |
| **Agent Memory** | Mem0 (semantic vector memory) + server-side session store |
| **Web Browsing** | Browserbase (cloud Chrome) + Playwright for JS-heavy pages |
| **Web Scraping** | Reddit JSON API, pytrends, HackerNews Firebase API, YouTube, X Trends |
| **Publishing** | Postiz (self-hosted on VPS) — X, LinkedIn, Instagram, Reddit |
| **State** | Zustand with localStorage persistence |
| **Fonts** | Instrument Serif (display), Sora (body) |
| **Hosting** | Vercel (frontend), Railway (backend), Hostinger VPS (Postiz), Browserbase (cloud Chrome) |

## The Six Agents

| Agent | Name | Purpose | Data Sources |
|-------|------|---------|--------------|
| Social Media | **Vortex** | Instagram carousels, reel scripts, memes, Twitter threads, WhatsApp forwards | LLM generation + autoresearch |
| SEO Writer | **Draft** | Blog articles targeting high-intent personal finance keywords | LLM generation + autoresearch |
| Community | **Rally** | Find real Reddit/Quora conversations and respond authentically | Reddit JSON API, Pullpush.io |
| Research | **Freq** | Track trends, audience sentiment, recommend content strategy | Reddit, Google Trends, HackerNews, YouTube, X Trends, Browserbase |
| Email | **Pulse** | Welcome emails, drip sequences, newsletters, re-engagement campaigns | LLM generation + autoresearch |
| Publisher | **Dispatch** | Connect social channels (OAuth), post content directly | Postiz API, OAuth integration |

## 3-Layer Memory Architecture

### Layer 1: Chat Session Memory (Server-Side)
- Server maintains conversation history per thread (last 20 messages)
- Enables follow-ups: "make it shorter", "change the city to Pune"
- 50 concurrent sessions, auto-evicts oldest

### Layer 2: Semantic Long-Term Memory (Mem0)
- Every conversation auto-stored in Mem0 after response
- Each agent has its own memory namespace (`agent-social`, `agent-seo`, etc.)
- Semantic vector search — finds relevant past content by meaning, not keywords
- Cross-agent memory: Vortex can recall what Freq researched
- Memories auto-extracted from conversations

### Layer 3: Autoresearch Experiment Log
- Every content generation logged to `experiment_log.jsonl`
- Tracks: iteration count, quality score, keep/discard status, weaknesses
- Winning patterns influence future generations
- Viewable via `/api/experiments` endpoint

**Memory flow per request:**
```
User asks "Write a reel about bike repairs"
    ↓
1. Mem0 search → find relevant past memories for this agent
2. Inject memories into system prompt as context
3. LLM generates with awareness of past content (avoids repetition)
4. Response stored back to Mem0 for future recall
5. Session history updated for follow-up context
```

## Live Data Sources (7 Sources, No API Keys for 6)

| Source | Method | What It Gets | API Key? |
|--------|--------|-------------|----------|
| **Reddit** | JSON API + Pullpush fallback | Real posts, scores, comments from finance subreddits | No |
| **Google Trends** | pytrends library | Interest over time, rising queries for India | No |
| **Hacker News** | Firebase API | Fintech/India-related stories from the tech community | No |
| **YouTube** | Search page scraping | Top video titles and links for trending finance topics | No |
| **X/Twitter Trends** | trends24.in scraping | Real-time trending hashtags and topics in India | No |
| **Browserbase** | Playwright + cloud Chrome | Any JS-heavy page: Economic Times, ProductHunt, competitor sites | Yes (free tier) |
| **Pullpush.io** | REST API | Reddit archive fallback when direct API is blocked | No |

### Browserbase Integration

Freq uses Browserbase (cloud headless Chrome) to browse JS-heavy pages that JSON APIs can't reach:

```
User: "Browse https://economictimes.indiatimes.com/topic/personal-loan"
    ↓
1. Detect URL in message → trigger Browserbase
2. Create Browserbase session via API
3. Connect Playwright via CDP (Chrome DevTools Protocol)
4. Navigate to URL, wait for JS rendering
5. Extract page content (titles, body text, headlines)
6. Pass to LLM for analysis + content recommendations
7. Return insights with real source attribution
```

**Browserbase capabilities:**
- Browse any public website with full JS rendering
- Extract content from pages that block API access
- Ad blocking enabled by default
- Sessions expire after 5 minutes (auto-cleanup)

**Sites that work:** HackerNews, Economic Times, trends24.in, Google Search
**Sites blocked:** ProductHunt (Cloudflare), Instagram (login wall), Quora (security wall)

## The Agent Harness (5 Layers)

```
Layer 1 — Serving        FastAPI REST + Next.js dashboard
Layer 2 — Orchestration  7-step ReAct loop, intent classification
Layer 3 — Memory         Mem0 semantic + session store + experiment log
Layer 4 — Tools          Web scraper, Browserbase, content generators, Postiz publisher
Layer 5 — LLM Core       Cerebras failover chain (Qwen 3 → Llama 3.1 → Ollama)
```

## The 7 Steps: What Happens When You Hit Send

| Step | Name | What Happens |
|------|------|--------------|
| 1 | **User goal** | Raw text from chat input + session_id |
| 2 | **Intent capture** | Classify: greeting, generation, research, browse, connect, or post |
| 3 | **Load memory** | Mem0 semantic search → inject relevant memories + session history |
| 4 | **Live data fetch** | For Freq: Browserbase browse / Reddit / Trends. For Rally: Reddit scrape |
| 5 | **LLM reasoning** | Failover chain generates content with full context |
| 6 | **Post-processing** | Strip promotional language + hallucinated URLs, run autoresearch (5 iterations, threshold 9.0) |
| 7 | **Store & return** | Save to Mem0 + session store, log experiment, return response |

## Self-Improvement Engine (Autoresearch Pattern)

Inspired by Karpathy's autoresearch — every content piece iterates until quality hits 9/10:

```
Iteration 1: Generate → Evaluate → Score 6.5/10
             Weaknesses: "too promotional, vague amounts"
             
Iteration 2: Rewrite fixing weaknesses → Score 7.8/10
             7.8 > 6.5 → KEEP

Iteration 3: Rewrite again → Score 9.2/10
             Above 9.0 threshold → STOP, return best
```

**Agent-specific evaluation:**

| Agent Type | Evaluation Criteria |
|-----------|-------------------|
| Social/SEO/Community | Relatability, Authenticity, Emotional Impact, Specificity, Non-promotional |
| Email | Relatability, Tone (friend vs corporation), Emotional Impact, Specificity, Readability |

**Training results:**
| Agent | Avg Score | Best Score |
|-------|-----------|------------|
| Vortex | 8.8/10 | 9.0 |
| Draft | 9.0/10 | 9.0 |
| Pulse | 7.6/10 | 8.8 |

## Dispatch: Social Publishing Pipeline

**Connect flow (no Postiz UI needed):**
```
User clicks X button in Dispatch
→ Backend calls Postiz internal API → gets OAuth URL
→ User redirected to Twitter/LinkedIn login → authorizes
→ Channel connected → shows with platform logo + green check
```

**Post flow:**
```
User says "Post this on X"
→ Dispatch finds content from conversation history
→ Uploads media to Postiz if attached
→ Posts via Postiz API with correct payload format
→ Returns confirmation with post ID
```

**Supported platforms:** X (Twitter), LinkedIn, Instagram, Facebook, Reddit, YouTube, TikTok, Threads, Pinterest

## Regulatory Guardrails (All Agents)

**SEBI Compliance:**
- Apollo Finvest is an NBFC, NOT a SEBI-registered investment advisor
- Agents NEVER give investment advice (mutual funds, stocks, SIPs, portfolio allocation)
- Rally filters out investment threads — only responds to lending/emergency topics
- All agents redirect investment questions to SEBI-registered advisors

**Data Integrity:**
- NEVER fabricate Reddit posts, usernames, or thread titles
- NEVER generate or hallucinate URLs — reference articles by title only
- Only real URLs from scraped data or the Apollo Cash Play Store link
- Post-processing regex strips any fabricated links that slip through
- If no real data available, agents say so honestly — never invent data

**Content Compliance:**
- Rally only responds to finance/lending threads (keyword filter + exclusion list)
- Investment, politics, dating, religion threads are auto-skipped
- Promotional language filter catches 25+ ad-copy patterns

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

## Deployment

```
agentblaze.vercel.app (Next.js frontend)
    ↓ API calls
agent-blaze-api-production.up.railway.app (FastAPI backend)
    ↓ LLM calls          ↓ Memory          ↓ Browsing
Cerebras Cloud         Mem0 Cloud       Browserbase (cloud Chrome)
    ↓ web scraping                          ↓ publishing
Reddit + Google Trends + HN + YT        srv1317892.hstgr.cloud (Postiz)
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
  web_scraper.py           — Reddit + Google Trends + HN + YouTube + X Trends
  browser_skill.py         — Browserbase + Playwright for JS-heavy page browsing
  self_improve.py          — Autoresearch loop (5 iterations, 9.0 threshold)
  auto_publisher.py        — Platform-specific post handlers
  llm_client.py            — Multi-provider LLM client with failover

/harness
  serving.py               — FastAPI endpoints, agent personas, session memory, Browserbase routing
  orchestrator.py          — ReAct orchestration loop
  memory.py                — Mem0 semantic memory integration
  tools.py                 — Tool definitions
  llm_core.py              — Provider-agnostic LLM interface

/dashboard
  src/app/page.tsx          — Main app with auth + OAuth redirect handling
  src/components/chat/      — Chat UI with streaming, media upload, platform connect buttons
  src/components/layout/    — Sidebar + navigation
  src/components/views/     — Dashboard home, calendar, publish view
  src/stores/ui-store.ts    — Zustand with localStorage persistence
  public/                   — Agent SVG icons + platform logos

/config
  settings.py              — Audience segments, keywords, schedules

/data/memory               — Fallback memory store
/output/experiments         — Autoresearch experiment logs
/output/browser             — Browserbase session results
```
