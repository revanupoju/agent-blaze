# Blaze — Architecture Overview

**April 2026 · Sai Revanth Anupoju**

---

## What Blaze Is

Blaze is an AI marketing agent platform for Apollo Cash. Six sub-agents generate, research, and distribute content across social media, SEO, communities, email, and direct publishing — all from a single chat interface.

Content is grounded in live web data (Reddit, Google Trends) and refined through a recursive self-improvement loop inspired by Karpathy's autoresearch. The agents evaluate their own output, fix weaknesses, and only ship content scoring 7/10 or above.

**Live:** agentblaze.vercel.app

---

## The Six Agents

| Agent | Job | One-liner |
|-------|-----|-----------|
| **Vortex** | Social Media | Carousels, reels, memes, threads, WhatsApp forwards |
| **Draft** | SEO Writer | Blog articles targeting high-intent keywords |
| **Rally** | Community | Finds real Reddit threads and responds authentically |
| **Freq** | Research | Tracks trends, analyzes competitors, recommends content |
| **Pulse** | Email | Newsletters and drip sequences in Apollo's voice |
| **Dispatch** | Publisher | Posts to Instagram, Twitter, Facebook via Postiz |

---

## Architecture

```
Layer 1: Serving     — Next.js (Vercel) + FastAPI (Railway)
Layer 2: Orchestration — 7-step ReAct loop with intent classification
Layer 3: Memory      — Zustand + localStorage, conversation history
Layer 4: Tools       — 14 tools: content gen, scraping, publishing
Layer 5: LLM Core    — Qwen 3 235B → Llama 3.1 8B → Ollama (failover)
```

## What Happens When You Send a Message

1. **Intent capture** — classify simple vs generation vs research, tune temperature
2. **Cross-agent redirect** — if wrong agent, redirect ("That's Vortex's job")
3. **Live data fetch** — scrape Reddit (Pullpush.io) + Google Trends (pytrends)
4. **LLM generates** — content produced with failover chain (3 providers)
5. **Promotional filter** — strips "Apply now", feature dumps, fake URLs
6. **Autoresearch loop** — evaluate 1-10, rewrite if below 7, keep best version
7. **Return** — formatted with markdown, sources panel, copy button

---

## Key Technical Decisions

| Decision | Why |
|----------|-----|
| Open-source LLMs (Qwen 3 235B, Llama 3.1) | No vendor lock-in. Cerebras: 2,200 tokens/sec. |
| Failover chain with retry | Qwen 235B → Llama 8B → Ollama. Never returns empty. |
| Python formats structure, LLM writes content | LLMs ignore instructions to use real data. Python controls thread titles/subreddits, LLM writes replies. |
| Autoresearch self-improvement | First draft scores ~5/10. After loop: ~9/10. |
| Promotional language filter | 25+ regex patterns strip ad copy LLMs keep inserting. |
| Pullpush.io for Reddit | Reddit blocks server IPs. Pullpush bypasses. |
| Postiz self-hosted (HTTPS) | Own VPS, own data. Auto-publishing to all channels. |

---

## Content Quality Scores

| Agent | Best Score | Sample |
|-------|-----------|--------|
| Vortex | 10/10 | Reel script: "Ten Days Too Long" — a father needs school fees |
| Draft | 10/10 | 2,500-word CIBIL myths article with real scenarios |
| Rally | 9.5/10 | Real Reddit threads with varied, helpful responses |
| Freq | 9/10 | Competitor analysis with content recommendations |
| Pulse | 9/10 | Newsletter matching Apollo Substack's sharp tone |

---

## Deployment

```
agentblaze.vercel.app        → Next.js frontend (Vercel)
railway.app                  → FastAPI backend (Railway)
srv1317892.hstgr.cloud       → Postiz publishing (Hostinger VPS, HTTPS via Caddy)
Cerebras Cloud               → LLM inference (Qwen 3 235B)
```

---

## Distribution Flywheel

```
Freq researches what's trending
  → Vortex creates social posts
  → Draft writes SEO articles
  → Rally responds in communities
  → Pulse sends newsletters
  → Dispatch publishes to all channels
  → Freq tracks what worked
  → Loop repeats
```

This isn't just content creation. It's a full distribution engine.

---

**GitHub:** github.com/revanupoju/agent-blaze
**Live:** agentblaze.vercel.app (click "Continue with Demo Access" to login)
**Publishing:** srv1317892.hstgr.cloud (Email: demo@agentblaze.com / Password: Blaze2026!)
