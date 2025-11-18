"""Example: Manual PR Review Trigger.

This example shows how to manually trigger a PR review and
interact with the PR Review Bot for testing purposes.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bots.pr_review_bot import PRReviewBot
from core.event_bus import EventBus, Event
from core.state_manager import StateManager
from utils.metrics import MetricsCollector


async def trigger_manual_review():
    """Manually trigger a PR review for testing."""
    print("=== Manual PR Review Trigger ===\n")

    # Configuration
    config = {
        "github_token": os.getenv("GITHUB_TOKEN"),
        "monitored_repositories": ["bsw-arch/PIPE"],
        "pr_quest_url": os.getenv("PR_QUEST_URL", "http://pr-quest:8000"),
        "llm_model": "gpt-4o-mini",
        "check_interval": 300,  # Long interval for manual testing
        "log_level": "DEBUG",
    }

    if not config["github_token"]:
        print("ERROR: GITHUB_TOKEN not set")
        return

    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager(state_dir="./state")
    metrics = MetricsCollector()

    # Create bot
    bot = PRReviewBot(
        name="pr_review_bot_manual",
        config=config,
        event_bus=event_bus,
        state_manager=state_manager,
        metrics=metrics,
    )

    # Initialize bot
    if not await bot.initialize():
        print("Failed to initialize bot")
        return

    # Get PR details from user
    print("Enter PR details for review:")
    repo = input("Repository (e.g., owner/repo): ").strip()
    pr_number = input("PR number: ").strip()

    if not repo or not pr_number:
        print("Invalid input")
        return

    try:
        pr_number = int(pr_number)
    except ValueError:
        print("PR number must be an integer")
        return

    # Simulate PR created event
    print(f"\n🔍 Triggering review for {repo}#{pr_number}...")

    await event_bus.publish(
        Event(
            event_type="integration.pr_created",
            source="manual_trigger",
            data={
                "repository": repo,
                "pr_number": pr_number,
            },
        )
    )

    # Wait for event to be processed
    await asyncio.sleep(2)

    # Process the review
    print("\n⚙️  Processing review...")

    # Run one cycle of the bot's execute loop manually
    await bot._monitor_github_prs()
    await bot._process_pending_reviews()

    print("\n✅ Review processing complete!")
    print("\nCheck the PR on GitHub for the review comment.")

    # Show pending reviews
    if bot.pending_reviews:
        print("\n📋 Pending Reviews:")
        for pr_key, pr_info in bot.pending_reviews.items():
            print(f"\n  {pr_key}:")
            print(f"    Status: {pr_info['status']}")
            if "decision" in pr_info:
                print(f"    Decision: {pr_info['decision']}")
                print(f"    Risk Level: {pr_info['risk_level']}")
                print(f"    XP Awarded: {pr_info['xp_awarded']}")

    # Cleanup
    await bot.cleanup()


async def simulate_pr_workflow():
    """Simulate a complete PR review workflow."""
    print("=== Simulated PR Workflow ===\n")

    # This example shows the complete flow of events
    event_bus = EventBus()

    events_received = []

    async def log_event(event: Event):
        events_received.append(event)
        print(f"📨 Event: {event.event_type}")
        print(f"   Source: {event.source}")
        print(f"   Data: {event.data}")
        print()

    # Subscribe to all PR review events
    event_bus.subscribe("pr_review.queued", log_event)
    event_bus.subscribe("pr_review.complete", log_event)
    event_bus.subscribe("pr_review.metrics", log_event)

    # Simulate PR lifecycle
    print("1. Integration PR Created")
    await event_bus.publish(
        Event(
            event_type="integration.pr_created",
            source="github_webhook",
            data={
                "repository": "bsw-arch/PIPE",
                "pr_number": 123,
                "pr_url": "https://github.com/bsw-arch/PIPE/pull/123",
                "title": "Add Cognee AI memory integration",
                "author": "developer1",
            },
        )
    )

    await asyncio.sleep(1)

    print("\n2. PR Review Queued")
    await event_bus.publish(
        Event(
            event_type="pr_review.queued",
            source="pr_review_bot",
            data={
                "repo": "bsw-arch/PIPE",
                "pr_number": 123,
                "pr_url": "https://github.com/bsw-arch/PIPE/pull/123",
                "title": "Add Cognee AI memory integration",
                "author": "developer1",
                "status": "queued",
            },
        )
    )

    await asyncio.sleep(1)

    print("\n3. PR Review Complete (Auto-Approved)")
    await event_bus.publish(
        Event(
            event_type="pr_review.complete",
            source="pr_review_bot",
            data={
                "pr_key": "bsw-arch/PIPE#123",
                "pr_url": "https://github.com/bsw-arch/PIPE/pull/123",
                "analysis_id": "analysis_abc123",
                "decision": "auto_approved",
                "risk_level": "NONE",
                "clusters": 3,
                "risks": 0,
                "xp_awarded": 150,
            },
        )
    )

    await asyncio.sleep(1)

    print("\n4. Metrics Published")
    await event_bus.publish(
        Event(
            event_type="pr_review.metrics",
            source="pr_review_bot",
            data={
                "total_reviews": 15,
                "pending_reviews": 2,
                "decisions": {
                    "auto_approved": 10,
                    "flagged_for_review": 3,
                    "approved_with_suggestions": 2,
                },
            },
        )
    )

    await asyncio.sleep(1)

    print(f"\n✅ Workflow complete! {len(events_received)} events received")


async def demonstrate_quality_gates():
    """Demonstrate how quality gates work."""
    print("=== Quality Gates Demonstration ===\n")

    from integrations.pr_quest_models import (
        PRAnalysisResult,
        RiskLevel,
        Risk,
        CodeCluster,
    )
    from bots.pr_review_bot import ReviewDecision

    # Mock PR Review Bot for demonstration
    config = {
        "github_token": "mock_token",
        "auto_approve_threshold": "NONE",
        "flag_review_threshold": "MODERATE",
        "reject_threshold": "CRITICAL",
    }

    print("Quality Gate Thresholds:")
    print(f"  Auto-Approve: {config['auto_approve_threshold']}")
    print(f"  Flag for Review: {config['flag_review_threshold']}")
    print(f"  Reject: {config['reject_threshold']}")
    print()

    # Example 1: Clean PR (auto-approve)
    print("Example 1: Clean PR (No Risks)")
    print("  Risk Level: NONE")
    print(f"  Decision: {ReviewDecision.AUTO_APPROVED.value}")
    print()

    # Example 2: PR with suggestions (approved with suggestions)
    print("Example 2: PR with Minor Suggestions")
    print("  Risk Level: LOW")
    print("  Suggestions: 5 improvements")
    print(f"  Decision: {ReviewDecision.APPROVED_WITH_SUGGESTIONS.value}")
    print()

    # Example 3: Moderate risk (flag for review)
    print("Example 3: PR with Moderate Risk")
    print("  Risk Level: MODERATE")
    print("  Risks: Code duplication, complex logic")
    print(f"  Decision: {ReviewDecision.FLAGGED_FOR_REVIEW.value}")
    print()

    # Example 4: Critical security risk (reject)
    print("Example 4: PR with Security Vulnerability")
    print("  Risk Level: CRITICAL")
    print("  Risks: SQL injection vulnerability")
    print(f"  Decision: {ReviewDecision.REJECTED_SECURITY.value}")
    print()

    # Example 5: Breaking changes (reject)
    print("Example 5: PR with Breaking Changes")
    print("  Risk Level: CRITICAL")
    print("  Risks: Breaking API changes")
    print(f"  Decision: {ReviewDecision.REJECTED_BREAKING_CHANGES.value}")
    print()


async def main():
    """Main example menu."""
    print("PR Review Bot Examples\n")
    print("Select an example:")
    print("1. Trigger manual PR review")
    print("2. Simulate PR workflow")
    print("3. Demonstrate quality gates")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        await trigger_manual_review()
    elif choice == "2":
        await simulate_pr_workflow()
    elif choice == "3":
        await demonstrate_quality_gates()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
