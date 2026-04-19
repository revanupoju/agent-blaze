"""Agent 2: SEO + Article Generation Agent for Apollo Cash."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from agents.llm_client import generate, generate_json
from agents.prompts import SEO_ARTICLE_SYSTEM, SEO_ARTICLE_USER_TEMPLATE
from config.settings import SEO_KEYWORDS, AUDIENCE_SEGMENTS

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "articles"

# Pre-defined article briefs for high-priority content
ARTICLE_BRIEFS = [
    {
        "keyword": "personal loan kaise le",
        "secondary_keywords": ["personal loan eligibility", "loan apply kaise kare", "first time loan India"],
        "language": "english",
        "audience_segment": "ntc_youth",
        "article_type": "educational",
        "title_hint": "Complete guide for first-time borrowers in Hindi",
    },
    {
        "keyword": "emergency loan for salary delay",
        "secondary_keywords": ["salary late loan", "instant cash when salary delayed", "short term loan India"],
        "language": "english",
        "audience_segment": "salaried_tier2",
        "article_type": "problem_solving",
        "title_hint": "What to do when salary is delayed and bills are due",
    },
    {
        "keyword": "loan without CIBIL score",
        "secondary_keywords": ["no CIBIL loan app", "NTC loan India", "first time loan no credit history", "CIBIL score nahi hai"],
        "language": "english",
        "audience_segment": "ntc_youth",
        "article_type": "myth_busting",
        "title_hint": "Debunking the myth that you need CIBIL to get a loan",
    },
    {
        "keyword": "small loan app for gig workers",
        "secondary_keywords": ["delivery boy loan", "Swiggy Zomato rider loan", "gig worker emergency money"],
        "language": "english",
        "audience_segment": "gig_workers",
        "article_type": "audience_specific",
        "title_hint": "Financial guide specifically for delivery partners and gig workers",
    },
    {
        "keyword": "medical emergency loan India",
        "secondary_keywords": ["hospital bill loan", "urgent medical loan", "medical emergency mein loan kaise le"],
        "language": "english",
        "audience_segment": "self_employed",
        "article_type": "use_case_landing",
        "title_hint": "How to arrange money fast during a medical emergency",
    },
]


def generate_article(brief: dict) -> dict:
    """Generate a single SEO article from a brief."""
    prompt = SEO_ARTICLE_USER_TEMPLATE.format(
        keyword=brief["keyword"],
        secondary_keywords=", ".join(brief["secondary_keywords"]),
        language=brief["language"],
        audience_segment=brief["audience_segment"],
        article_type=brief["article_type"],
    )
    article = generate_json(SEO_ARTICLE_SYSTEM, prompt, max_tokens=6000)
    return article


def generate_keyword_analysis() -> dict:
    """Analyze and prioritize keywords for content strategy."""
    all_keywords = []
    for category, keywords in SEO_KEYWORDS.items():
        for kw in keywords:
            all_keywords.append({"keyword": kw, "category": category})

    analysis_prompt = f"""
Analyze these keywords for Apollo Cash (instant personal loan app for tier 2/3 India):

{json.dumps(all_keywords, indent=2)}

For each keyword, estimate:
- Search intent (informational / navigational / transactional)
- Estimated competition level (low / medium / high)
- Priority for Apollo Cash (1-10, 10 = highest)
- Suggested content type (blog / landing page / FAQ / comparison)
- Suggested article angle

Return a JSON object:
{{
  "analysis": [
    {{
      "keyword": "...",
      "category": "...",
      "search_intent": "...",
      "competition": "...",
      "priority_score": 8,
      "content_type": "...",
      "suggested_angle": "...",
      "estimated_monthly_searches": "low/medium/high"
    }}
  ],
  "top_5_priorities": ["keyword1", "keyword2", ...],
  "content_gaps": ["topics we should cover but aren't in the keyword list"],
  "quick_wins": ["low competition + high intent keywords to target first"]
}}

Return ONLY the JSON object.
"""
    return generate_json(SEO_ARTICLE_SYSTEM, analysis_prompt)


def save_article(article: dict, filename: str | None = None) -> tuple[str, str]:
    """Save article as both JSON (metadata) and Markdown (content)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = article.get("slug", "untitled")
    if filename is None:
        filename = slug

    # Save JSON with metadata
    json_path = OUTPUT_DIR / f"{filename}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(article, f, indent=2, ensure_ascii=False)

    # Save readable markdown
    md_content = f"""---
title: "{article.get('meta_title', '')}"
description: "{article.get('meta_description', '')}"
slug: "{slug}"
keyword: "{article.get('primary_keyword', '')}"
language: "{article.get('language', 'english')}"
audience: "{article.get('target_audience', '')}"
type: "{article.get('article_type', '')}"
---

{article.get('content_markdown', '')}
"""
    md_path = OUTPUT_DIR / f"{filename}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return str(json_path), str(md_path)


def run_full_pipeline(num_articles: int = 3) -> dict:
    """Run the complete SEO article generation pipeline."""
    articles = []
    briefs = ARTICLE_BRIEFS[:num_articles]

    for brief in briefs:
        article = generate_article(brief)
        json_path, md_path = save_article(article)
        articles.append({
            "brief": brief,
            "article": article,
            "json_path": json_path,
            "md_path": md_path,
        })

    # Generate keyword analysis
    keyword_analysis = generate_keyword_analysis()
    analysis_path = OUTPUT_DIR / "keyword_analysis.json"
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(keyword_analysis, f, indent=2, ensure_ascii=False)

    return {
        "total_articles": len(articles),
        "articles": articles,
        "keyword_analysis": keyword_analysis,
        "analysis_path": str(analysis_path),
    }
