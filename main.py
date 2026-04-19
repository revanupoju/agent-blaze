"""
Apollo Cash AI Marketing Agent — Main Pipeline Runner

Run all three sub-agents to generate marketing content:
  1. Social Media Content Engine
  2. SEO + Article Agent
  3. Community Distribution Agent

Usage:
  python main.py                  # Run all agents
  python main.py --agent social   # Run only social media agent
  python main.py --agent seo      # Run only SEO agent
  python main.py --agent community # Run only community agent
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from agents.social_media_agent import run_full_pipeline as run_social
from agents.seo_agent import run_full_pipeline as run_seo
from agents.community_agent import run_full_pipeline as run_community


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║       🚀 Apollo Cash AI Marketing Agent                   ║
║       Paison ki tension khatam                            ║
╚═══════════════════════════════════════════════════════════╝
    """)


def run_all():
    """Run the complete marketing pipeline."""
    print_banner()
    results = {}
    start = datetime.now()

    # Agent 1: Social Media
    print("\n▸ [Agent 1] Social Media Content Engine")
    print("  Generating posts across formats and segments...")
    try:
        social_results = run_social(total_posts=18)
        results["social_media"] = {
            "status": "success",
            "total_posts": social_results["total_posts"],
            "posts_file": social_results["posts_file"],
            "calendar_file": social_results["calendar_file"],
        }
        print(f"  ✓ Generated {social_results['total_posts']} posts")
        print(f"  ✓ Weekly calendar saved to {social_results['calendar_file']}")
    except Exception as e:
        results["social_media"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Error: {e}")

    # Agent 2: SEO Articles
    print("\n▸ [Agent 2] SEO + Article Agent")
    print("  Generating articles and keyword analysis...")
    try:
        seo_results = run_seo(num_articles=3)
        results["seo_articles"] = {
            "status": "success",
            "total_articles": seo_results["total_articles"],
            "articles": [
                {"keyword": a["brief"]["keyword"], "md_path": a["md_path"]}
                for a in seo_results["articles"]
            ],
            "analysis_path": seo_results["analysis_path"],
        }
        print(f"  ✓ Generated {seo_results['total_articles']} articles")
        print(f"  ✓ Keyword analysis saved to {seo_results['analysis_path']}")
    except Exception as e:
        results["seo_articles"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Error: {e}")

    # Agent 3: Community Distribution
    print("\n▸ [Agent 3] Community Distribution Agent")
    print("  Generating community responses and discovery report...")
    try:
        community_results = run_community(num_responses=12)
        results["community"] = {
            "status": "success",
            "total_responses": community_results["total_responses"],
            "responses_file": community_results["responses_file"],
            "discovery_file": community_results["discovery_file"],
            "mention_ratio": community_results["mention_ratio"],
        }
        print(f"  ✓ Generated {community_results['total_responses']} responses")
        print(f"  ✓ Apollo Cash mentioned in {community_results['mention_ratio']} responses")
        print(f"  ✓ Thread discovery report saved")
    except Exception as e:
        results["community"] = {"status": "error", "error": str(e)}
        print(f"  ✗ Error: {e}")

    # Summary
    elapsed = (datetime.now() - start).total_seconds()
    results["pipeline_meta"] = {
        "run_time_seconds": round(elapsed, 1),
        "timestamp": datetime.now().isoformat(),
    }

    summary_path = Path("output/pipeline_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Pipeline complete in {elapsed:.1f}s")
    print(f"Summary: {summary_path}")
    print(f"{'='*60}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Apollo Cash AI Marketing Agent")
    parser.add_argument(
        "--agent",
        choices=["social", "seo", "community", "all"],
        default="all",
        help="Which agent to run",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of items to generate",
    )
    args = parser.parse_args()

    if args.agent == "all":
        run_all()
    elif args.agent == "social":
        print_banner()
        print("▸ Running Social Media Content Engine...")
        result = run_social(total_posts=args.count or 18)
        print(f"✓ Generated {result['total_posts']} posts → {result['posts_file']}")
    elif args.agent == "seo":
        print_banner()
        print("▸ Running SEO + Article Agent...")
        result = run_seo(num_articles=args.count or 3)
        print(f"✓ Generated {result['total_articles']} articles")
    elif args.agent == "community":
        print_banner()
        print("▸ Running Community Distribution Agent...")
        result = run_community(num_responses=args.count or 12)
        print(f"✓ Generated {result['total_responses']} responses")


if __name__ == "__main__":
    main()
