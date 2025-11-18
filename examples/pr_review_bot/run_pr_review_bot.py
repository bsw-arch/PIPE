"""Example: Running the PR Review Bot.

This example demonstrates how to run the PR Review Bot for automated
code review of integration PRs using PR-QUEST.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bots.pr_review_bot import PRReviewBot
from core.event_bus import EventBus, Event
from core.state_manager import StateManager
from utils.metrics import MetricsCollector


async def main():
    """Run the PR Review Bot example."""
    print("=== PR Review Bot Example ===\n")

    # Configuration
    config = {
        "github_token": os.getenv("GITHUB_TOKEN"),
        "monitored_repositories": [
            "bsw-arch/PIPE",
            # Add your repositories here
        ],
        "pr_quest_url": os.getenv("PR_QUEST_URL", "http://pr-quest:8000"),
        "llm_model": "gpt-4o-mini",
        "check_interval": 60,
        "log_level": "INFO",
        # Quality gates
        "auto_approve_threshold": "NONE",
        "flag_review_threshold": "MODERATE",
        "reject_threshold": "CRITICAL",
        # Human reviewers
        "human_reviewers": ["senior-dev", "tech-lead"],
    }

    # Validate GitHub token
    if not config["github_token"]:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        print("Please set GITHUB_TOKEN to your GitHub personal access token")
        return

    # Initialize core components
    event_bus = EventBus()
    state_manager = StateManager(state_dir="./state")
    metrics = MetricsCollector()

    # Create PR Review Bot
    bot = PRReviewBot(
        name="pr_review_bot",
        config=config,
        event_bus=event_bus,
        state_manager=state_manager,
        metrics=metrics,
    )

    # Set up event listeners
    async def on_review_complete(event: Event):
        """Handle PR review completion events."""
        data = event.data
        print(f"\n✅ PR Review Complete!")
        print(f"   PR: {data['pr_key']}")
        print(f"   Decision: {data['decision']}")
        print(f"   Risk Level: {data['risk_level']}")
        print(f"   Clusters: {data['clusters']}")
        print(f"   Risks: {data['risks']}")
        print(f"   XP Awarded: {data['xp_awarded']}")

    async def on_review_queued(event: Event):
        """Handle PR review queued events."""
        data = event.data
        print(f"\n📋 PR Queued for Review")
        print(f"   PR: {data['repo']}#{data['pr_number']}")
        print(f"   Title: {data['title']}")
        print(f"   Author: {data['author']}")

    async def on_metrics(event: Event):
        """Handle metrics events."""
        data = event.data
        print(f"\n📊 Review Metrics:")
        print(f"   Total Reviews: {data['total_reviews']}")
        print(f"   Pending: {data['pending_reviews']}")
        print(f"   Decisions: {data['decisions']}")

    # Subscribe to events
    event_bus.subscribe("pr_review.complete", on_review_complete)
    event_bus.subscribe("pr_review.queued", on_review_queued)
    event_bus.subscribe("pr_review.metrics", on_metrics)

    print("Starting PR Review Bot...")
    print(f"Monitoring repositories: {config['monitored_repositories']}")
    print(f"PR-QUEST URL: {config['pr_quest_url']}\n")

    # Run bot
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
