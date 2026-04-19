# Blaze

Architecture Overview · April 2026 · Sai Revanth Anupoju

## What Blaze Is

Blaze is an AI-powered marketing agent platform built for Apollo Cash. The core of the product is four specialized AI agents — Vortex, Draft, Rally, and Freq — that continuously generate and distribute marketing content across channels to drive awareness and user acquisition.

Every piece of content is grounded through real web data (Reddit, Google Trends) and refined through a recursive self-improvement loop inspired by Karpathy's autoresearch. The agents don't just generate once — they evaluate their own output, identify weaknesses, and iterate until quality meets the threshold.

## Tech Stack

| Layer | Choice |
|-------|--------|
| **Frontend** | Next.js 16 on Vercel, TypeScript, Tailwind CSS 4 |
| **Backend** | Python 3.11, FastAPI on Railway |
| **LLM** | Qwen 3 235B on Cerebras (primary), with Llama 3.1 8B and Ollama as failover |
| **State** | Zustand with localStorage persistence |
| **Web Scraping** | Reddit JSON API, pytrends (Google Trends), BeautifulSoup |
| **Fonts** | Instrument Serif (display), Sora (body) |
| **Auth** | Demo login with session persistence |
| **Hosting** | Vercel (frontend), Railway (backend) |

## The Four Agents

| Agent | Name | Purpose | Icon |
|-------|------|---------|------|
| Social Media | **Vortex** | Instagram carousels, reel scripts, memes, Twitter threads, WhatsApp forwards, YouTube Shorts | Spiral vortex |
| SEO Writer | **Draft** | Blog articles targeting high-intent personal finance keywords with proper SEO structure | Three lines |
| Community | **Rally** | Find real conversations on Reddit/Quora/Twitter and respond authentically | Lightning scribble |
| Research | **Freq** | Track trends, audience sentiment, competitor strategies, recommend content | Frequency wave |

## How It Works: The Agent Harness

Blaze is built as a 5-layer system where every layer is swappable independently.

- **Layer 1, Serving.** FastAPI REST endpoints and Next.js dashboard. The only layer that touches the UI.
- **Layer 2, Orchestration.** The 7-step ReAct loop lives in the chat handler and emits typed step events for live UI status.
- **Layer 3, Context and Memory.** System prompt, intent classifier, and Zustand store with localStorage persistence for chat history.
- **Layer 4, Tools.** 14 pure tool handlers shaped as (dataset, args) returning structured data. Web scraper, content generators, and research tools.
- **Layer 5, LLM Core.** OpenAI-compatible fetch with failover: Cerebras (Qwen 3 235B), then Cerebras (Llama 3.1 8B), then Ollama local.

## The 7 Steps: What Happens When You Hit Send

| Step | Name | What Happens |
|------|------|--------------|
| 1 | **User goal** | The raw text from the chat input |
| 2 | **Intent capture** | Classify as simple (temp 0.3) or generation/research (temp 0.7-0.9) |
| 3 | **Load memory** | Build the system prompt, add agent persona and conversation history |
| 4 | **Live data fetch** | For research/community: scrape Reddit and Google Trends for real data |
| 5 | **LLM reasoning** | Call the failover chain. The model generates content or writes replies |
| 6 | **Post-processing** | Strip promotional language, run autoresearch self-improvement loop |
| 7 | **Done or loop** | If quality score < 7/10, improve and re-evaluate. Loop caps at 2 rounds |

## Worked Example

*Prompt: Find real Reddit threads about salary delays and write responses*

- Steps 1 and 2. Raw question arrives. Intent is research + community, temperature set to 0.9.
- Step 3. System prompt and Rally persona are wired in, around 2 KB total.
- Step 4. Python scrapes Reddit via JSON API for threads matching "salary delayed", "need money urgently", "emergency loan". Returns real post titles, subreddits, scores, and body text.
- Step 5. LLM receives all threads in ONE batch prompt. Writes a unique reply for each thread — varying tone, length, and style. 3/5 mention Apollo Cash, 2/5 pure advice.
- Step 6. Promotional filter strips any "Apply now", feature dumps, or fake URLs. Autoresearch evaluator scores the output. If below 7/10, rewrites with weaknesses fixed.
- Step 7. Best version returned to user. Experiment logged to experiment_log.jsonl.

## The 14 Agent Tools

| Tool | Purpose | Example Prompt |
|------|---------|----------------|
| `generate_social_posts` | Create posts across formats and segments | "Generate 5 Instagram carousels" |
| `generate_content_variations` | A/B variations of the same scenario | "Try 3 angles for this story" |
| `generate_weekly_calendar` | Full 7-day content schedule | "Plan next week's content" |
| `generate_seo_article` | Full article from a target keyword | "Write about loan without CIBIL" |
| `keyword_analysis` | Priority scoring and competition | "Which keywords should we target?" |
| `generate_community_responses` | Authentic thread responses | "Respond to Reddit threads" |
| `discover_threads` | Find relevant conversations daily | "What's being discussed today?" |
| `research_trends` | Trending topics and viral formats | "What's trending this week?" |
| `research_audience_sentiment` | Segment-specific insights | "What are gig workers feeling?" |
| `adapt_strategy` | Engagement-based adjustments | "What should we change?" |
| `scrape_reddit` | Live Reddit data via JSON API | (internal — feeds Rally and Freq) |
| `search_reddit` | Search Reddit for keywords | (internal — feeds Rally and Freq) |
| `get_google_trends` | Live Google Trends data | (internal — feeds Freq) |
| `discover_threads` | Cross-subreddit thread discovery | (internal — feeds Rally) |

## Self-Improvement Engine (Autoresearch Pattern)

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch), every piece of generated content goes through a recursive improvement loop:

```
1. Generate content (the "experiment")
2. Evaluate quality on 5 dimensions:
   - Relatability (would someone in tier 2/3 India relate?)
   - Authenticity (sounds like a person, not a brand?)
   - Emotional impact (makes you feel something?)
   - Specificity (real amounts, times, places?)
   - Non-promotional (no "Apply now", no feature dumps?)
3. Score 1-10. If >= 7 → keep. If < 7 → improve.
4. Identify weaknesses → rewrite → re-evaluate
5. Keep best version, discard regressions
6. Log every experiment to experiment_log.jsonl
```

The experiment log tracks:
- Total experiments run
- Keep vs discard ratio per agent
- Average quality score over time
- Improvement trends

## LLM Failover Chain

```
Cerebras (Qwen 3 235B) — primary, most capable
    ↓ on 429 rate limit (retry with 1.5s backoff, 3 attempts)
Cerebras (Llama 3.1 8B) — fast fallback
    ↓ on error
Ollama (local) — offline fallback (when running locally)
    ↓ on error
Graceful error message
```

## Promotional Language Filter

A post-processing regex filter that strips ad copy the LLM keeps inserting despite prompts. Catches 25+ patterns including:
- "Game-changing", "Revolutionary solution"
- "Get started today", "Apply now", "Download now"
- "Competitive interest rates", "Hassle-free"
- "Take control of your financial future"
- "Apollo Cash's loan without CIBIL"
- Any line that's a pure CTA

## Live Web Scraping (No API Keys)

| Source | Method | What It Gets |
|--------|--------|-------------|
| **Reddit** | JSON API (add `.json` to any URL) | Real posts, scores, comments, authors from r/personalfinanceindia, r/india, r/IndiaInvestments |
| **Google Trends** | pytrends library | Interest over time, rising queries, related topics for India |
| **General web** | requests + BeautifulSoup | Any public web page content |

All scraping is free, open source, no API keys needed.

## Content Strategy

- Content is **conversational first** — agents ask clarifying questions before generating
- **50-60% of social posts** mention Apollo Cash naturally, **40-50% are pure stories** with no brand
- **70% of community responses** mention Apollo Cash as one option, **30% give pure advice** for trust building
- Never uses "Apply now", "Download today" or any hard CTA
- Every post tells a **story**, not an ad
- Supports both **English** (default) and **Hinglish** (toggle)

## Target Audience Segments

| Segment | Description | Pain Points |
|---------|-------------|-------------|
| **Gig Workers** | Zomato/Swiggy riders, Uber/Ola drivers, delivery partners | Irregular income, bike/phone repairs, no salary slip |
| **Salaried (Tier 2/3)** | Earning ₹15K-40K/month in smaller cities | Salary delays, month-end crunch, festival expenses |
| **Self-Employed** | Kirana owners, auto drivers, street vendors | Cash flow gaps, inventory restocking, seasonal income |
| **NTC Youth (21-35)** | First-time borrowers, no credit history | No CIBIL, fear of loan sharks, embarrassment about borrowing |

## Key Architectural Decisions

| Decision | Why |
|----------|-----|
| **Open-source LLMs (Qwen 3 235B, Llama 3.1)** | No vendor lock-in. Swap providers without contract friction. Cerebras pushes ~2,200 tokens/sec on Qwen 3 235B. |
| **Failover chain with retry** | A marketing agent that fails on a single 429 would not meet the bar. |
| **Python controls structure, LLM writes content** | LLMs ignore instructions to use real data. Python formats thread titles/subreddits from scraped data, LLM only writes the reply text. Guarantees real data in output. |
| **Autoresearch self-improvement** | Content quality varies wildly between generations. Evaluate → improve → keep-best loop raises average quality from ~5/10 to ~8/10. |
| **Promotional language filter** | No LLM reliably avoids ad copy. Regex post-processing catches what prompts miss. |
| **localStorage persistence** | Demo account stays logged in across refreshes. Chat history preserved. Zero backend auth needed for the demo. |

## Deployment

```
agentblaze.vercel.app (Next.js frontend)
    ↓ API calls
agent-blaze-api-production.up.railway.app (FastAPI backend)
    ↓ LLM calls
Cerebras Cloud (Qwen 3 235B / Llama 3.1 8B)
    ↓ web scraping
Reddit JSON API + Google Trends (pytrends)
```

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

# Switch to Ollama (local, offline)
# Edit .env: LLM_PROVIDER=ollama, OLLAMA_MODEL=llama3.1
# Make sure Ollama is running: ollama serve
```

## Repository Structure

```
/agents
  social_media_agent.py    — Vortex content generation
  seo_agent.py             — Draft article generation
  community_agent.py       — Rally response generation
  research_agent.py        — Freq trend analysis
  web_scraper.py           — Live Reddit + Google Trends scraping
  self_improve.py          — Autoresearch self-improvement loop
  browser_skill.py         — Browser-use capability definitions
  llm_client.py            — Multi-provider LLM client
  prompts.py               — All agent system prompts

/harness
  serving.py               — FastAPI endpoints + agent personas
  orchestrator.py          — ReAct orchestration loop
  memory.py                — Short-term + long-term memory
  tools.py                 — 14 tool definitions
  llm_core.py              — Provider-agnostic LLM interface

/dashboard
  src/app/page.tsx          — Main app with auth + coach marks
  src/components/chat/      — Chat UI with streaming + markdown
  src/components/layout/    — Sidebar + navigation
  src/components/views/     — Dashboard, calendar, harness views
  src/stores/ui-store.ts    — Zustand with localStorage persistence
  public/                   — Agent SVG icons + Blaze logo

/config
  settings.py              — Audience segments, keywords, schedules
```
