"""
Example: Review Integration PR with PR-QUEST

This example demonstrates the complete workflow for reviewing a
cross-domain integration PR using PR-QUEST LLM-powered analysis.

Workflow:
1. Create integration request
2. Submit GitHub PR
3. Trigger PR-QUEST analysis
4. Store results in Cognee
5. Update governance status
6. Export review as markdown

Prerequisites:
- PR-QUEST running at http://localhost:3000
- GITHUB_TOKEN environment variable
- OPENAI_API_KEY for PR-QUEST LLM features
- Cognee configured

Usage:
    python examples/pr_quest/review_integration_pr.py
"""

import asyncio
import os
from datetime import datetime

# Import PIPE components
from src.integrations.pr_quest_client import get_pr_quest_client, cleanup_pr_quest_client
from src.integrations.pr_quest_models import determine_decision_from_analysis
from src.integrations.cognee_client import get_cognee_client
from src.governance.datapoints import PRReviewDataPoint, pr_review_to_datapoint


async def example_1_basic_pr_review():
    """Basic PR review workflow - analyze and print results."""
    print("\n" + "=" * 60)
    print("Example 1: Basic PR Review")
    print("=" * 60 + "\n")

    # Initialize PR-QUEST client
    pr_quest = await get_pr_quest_client("http://localhost:3000")

    # Example PR URL (replace with your own)
    pr_url = "https://github.com/bsw-arch/PIPE/pull/123"

    print(f"📝 Analyzing PR: {pr_url}")
    print("⏳ Sending to PR-QUEST for LLM-powered analysis...\n")

    # Analyze the PR
    start_time = datetime.now()
    result = await pr_quest.analyze_pr(
        pr_url=pr_url,
        include_llm_analysis=True  # Use LLM for intelligent clustering
    )
    duration = (datetime.now() - start_time).total_seconds()

    # Display results
    print(f"✅ Analysis complete in {duration:.2f} seconds")
    print(f"   Analysis ID: {result.analysis_id}")
    print(f"   Repository: {result.repository}")
    print(f"   PR Number: {result.pr_number}\n")

    print(f"📦 Code Clusters: {len(result.clusters)}")
    for i, cluster in enumerate(result.clusters, 1):
        print(f"   {i}. {cluster.description}")
        print(f"      Files: {', '.join(cluster.files[:3])}" +
              (f" (+{len(cluster.files) - 3} more)" if len(cluster.files) > 3 else ""))
        print(f"      Lines changed: {cluster.line_count}\n")

    print(f"⚠️  Detected Risks: {len(result.risks)} ({result.overall_risk_level.value})")
    for i, risk in enumerate(result.risks, 1):
        print(f"   {i}. [{risk.severity.value}] {risk.type.value}: {risk.description}")
        if risk.location:
            print(f"      Location: {risk.location}")
        if risk.recommendation:
            print(f"      Fix: {risk.recommendation}")
        print(f"      Confidence: {risk.confidence:.0%}\n")

    print(f"💡 Suggestions: {len(result.suggestions)}")
    for i, suggestion in enumerate(result.suggestions, 1):
        print(f"   {i}. {suggestion}\n")

    print(f"🎮 XP Awarded: {result.xp_awarded} points\n")

    # Determine decision
    decision = determine_decision_from_analysis(result, auto_approve_threshold=0.95)
    print(f"🎯 Recommended Decision: {decision.value}\n")

    return result, duration


async def example_2_store_in_cognee():
    """Store PR review in Cognee for pattern learning."""
    print("\n" + "=" * 60)
    print("Example 2: Store PR Review in Cognee")
    print("=" * 60 + "\n")

    # Get analysis result from example 1
    result, duration = await example_1_basic_pr_review()

    # Initialize Cognee client
    cognee = await get_cognee_client()

    print("💾 Storing PR review in Cognee AI memory...")

    # Convert to PRReviewDataPoint
    decision = determine_decision_from_analysis(result)
    pr_review_dp = pr_review_to_datapoint(
        pr_analysis=result,
        decision=decision.value,
        reviewer="PRReviewBot",
        review_duration=int(duration),
        integration_id="INT-BNI-PIPE-001",  # Link to integration
        source_domain="BNI",
        target_domain="PIPE",
    )

    # Add to Cognee
    await cognee.add_datapoints([pr_review_dp])
    print("✅ DataPoint added to Cognee")

    # Cognify to build knowledge graph
    print("🧠 Building knowledge graph...")
    await cognee.cognify_governance_data()
    print("✅ Knowledge graph updated\n")

    # Now the review is searchable
    print("🔍 Searching for similar PR reviews...")
    similar_reviews = await cognee.search_integrations(
        "PR reviews with security vulnerabilities",
        limit=3
    )

    print(f"   Found {len(similar_reviews)} similar reviews\n")

    return pr_review_dp


async def example_3_export_markdown():
    """Export PR review as markdown for governance documentation."""
    print("\n" + "=" * 60)
    print("Example 3: Export Review as Markdown")
    print("=" * 60 + "\n")

    pr_quest = await get_pr_quest_client("http://localhost:3000")

    # Get analysis ID from example 1
    result, _ = await example_1_basic_pr_review()

    print("📄 Exporting review as markdown...")

    # Export to markdown
    markdown = await pr_quest.export_markdown(result.analysis_id)

    print(f"✅ Exported {len(markdown)} characters\n")
    print("Markdown preview (first 500 chars):")
    print("-" * 60)
    print(markdown[:500])
    print("..." if len(markdown) > 500 else "")
    print("-" * 60 + "\n")

    # Save to file
    filename = f"pr_review_{result.pr_number}_{result.analysis_id[:8]}.md"
    with open(filename, "w") as f:
        f.write(markdown)

    print(f"💾 Saved to: {filename}\n")

    return markdown


async def example_4_interactive_review():
    """Interactive review with step-by-step guidance."""
    print("\n" + "=" * 60)
    print("Example 4: Interactive Review Steps")
    print("=" * 60 + "\n")

    pr_quest = await get_pr_quest_client("http://localhost:3000")

    # Get analysis result
    result, _ = await example_1_basic_pr_review()

    print("🎯 Fetching interactive review steps...")

    # Get review steps
    steps = await pr_quest.get_review_steps(result.analysis_id)

    print(f"✅ Retrieved {len(steps)} review steps\n")

    # Display each step
    for i, step in enumerate(steps, 1):
        print(f"Step {i}: {step.title}")
        print(f"   Cluster: {step.cluster_id}")
        if step.guidance:
            print(f"   Guidance: {step.guidance}")
        print(f"   Diff size: {len(step.diff_section)} characters")
        print(f"   Notes: {len(step.notes)}\n")

    return steps


async def example_5_xp_leaderboard():
    """View reviewer XP leaderboard for gamification."""
    print("\n" + "=" * 60)
    print("Example 5: Reviewer XP Leaderboard")
    print("=" * 60 + "\n")

    pr_quest = await get_pr_quest_client("http://localhost:3000")

    print("🏆 Fetching XP leaderboard...\n")

    # Get leaderboard
    leaderboard = await pr_quest.get_xp_leaderboard(limit=10)

    print(f"Top {len(leaderboard)} Reviewers:")
    print("-" * 60)
    print(f"{'Rank':<6} {'Username':<20} {'XP':<8} {'Reviews':<10} {'Level':<6}")
    print("-" * 60)

    for reviewer in leaderboard:
        print(
            f"#{reviewer.rank:<5} {reviewer.username:<20} "
            f"{reviewer.total_xp:<8} {reviewer.reviews_completed:<10} {reviewer.level:<6}"
        )

    print("-" * 60 + "\n")

    # Show achievements for top reviewer
    if leaderboard:
        top_reviewer = leaderboard[0]
        print(f"🎖️  {top_reviewer.username}'s Achievements:")
        for achievement in top_reviewer.achievements:
            print(f"   ⭐ {achievement}")
        print()

    return leaderboard


async def example_6_pattern_learning():
    """Learn from historical PR reviews to improve future analysis."""
    print("\n" + "=" * 60)
    print("Example 6: Pattern Learning from Historical Reviews")
    print("=" * 60 + "\n")

    # Store a few PR reviews in Cognee (simulated)
    cognee = await get_cognee_client()

    print("📚 Learning from historical PR reviews...\n")

    # Search for past security issues
    print("🔍 Searching: 'PR reviews with SQL injection risks'")
    results = await cognee.search_integrations(
        "PR reviews with SQL injection risks",
        limit=5
    )

    print(f"   Found {len(results)} similar past reviews\n")

    # Search for integration patterns
    print("🔍 Searching: 'BNI to PIPE integration reviews'")
    results = await cognee.search_integrations(
        "BNI to PIPE integration reviews",
        limit=5
    )

    print(f"   Found {len(results)} relevant integration reviews\n")

    # Suggest fixes based on historical data
    print("💡 Example: Suggesting fixes based on precedent")
    print("   If PR has SQL injection risk:")
    print("   → Historical reviews suggest: 'Use parameterized queries'")
    print("   → Success rate with this fix: 95%\n")

    return results


async def example_7_full_governance_workflow():
    """Complete governance workflow from request to approval."""
    print("\n" + "=" * 60)
    print("Example 7: Full Governance Workflow")
    print("=" * 60 + "\n")

    pr_quest = await get_pr_quest_client("http://localhost:3000")
    cognee = await get_cognee_client()

    # Step 1: Integration Request
    print("Step 1: Integration Request")
    print("   Source: BNI (Blockchain Network Infrastructure)")
    print("   Target: PIPE (Pipeline Orchestration)")
    print("   Type: Hub connection")
    print("   Status: Approved for implementation\n")

    # Step 2: Developer creates PR
    pr_url = "https://github.com/bsw-arch/PIPE/pull/999"
    print(f"Step 2: Developer creates GitHub PR")
    print(f"   PR URL: {pr_url}\n")

    # Step 3: Automated PR Review
    print("Step 3: Automated PR Review with PR-QUEST")
    print("   ⏳ Analyzing PR...")
    start_time = datetime.now()
    result = await pr_quest.analyze_pr(pr_url, include_llm_analysis=True)
    duration = (datetime.now() - start_time).total_seconds()
    print(f"   ✅ Analysis complete in {duration:.2f}s")
    print(f"   📊 Results: {len(result.clusters)} clusters, {len(result.risks)} risks")
    print(f"   ⚠️  Risk level: {result.overall_risk_level.value}\n")

    # Step 4: Determine decision
    print("Step 4: Governance Decision")
    decision = determine_decision_from_analysis(result, auto_approve_threshold=0.95)
    print(f"   🎯 Decision: {decision.value}")

    if decision.value == "APPROVE":
        print("   ✅ Auto-approved - No risks detected")
        print("   📝 Action: Merge PR automatically\n")
    elif decision.value == "REJECT":
        print("   ❌ Auto-rejected - Critical risks detected")
        print("   📝 Action: Block PR merge, notify developer\n")
    else:  # NEEDS_REVIEW
        print("   ⏸️  Flagged for human review - Moderate risks detected")
        print("   📝 Action: Assign to governance reviewer\n")

    # Step 5: Store in Cognee
    print("Step 5: Store in Cognee for Learning")
    pr_review_dp = pr_review_to_datapoint(
        pr_analysis=result,
        decision=decision.value,
        reviewer="PRReviewBot",
        review_duration=int(duration),
        integration_id="INT-BNI-PIPE-999",
        source_domain="BNI",
        target_domain="PIPE",
    )
    await cognee.add_datapoints([pr_review_dp])
    await cognee.cognify_governance_data()
    print("   ✅ Review stored in AI memory\n")

    # Step 6: Export documentation
    print("Step 6: Export Governance Documentation")
    markdown = await pr_quest.export_markdown(result.analysis_id)
    filename = f"governance/reviews/INT-BNI-PIPE-999-review.md"
    print(f"   📄 Exported to: {filename}\n")

    # Step 7: Metrics
    print("Step 7: Metrics & Gamification")
    print(f"   🎮 XP Awarded: {result.xp_awarded} points")
    print(f"   ⏱️  Review Duration: {duration:.2f}s")
    print(f"   📊 Automated vs Manual: 100% automated\n")

    print("=" * 60)
    print("Workflow Complete!")
    print("=" * 60 + "\n")

    return result, decision


async def main():
    """Run all examples."""
    try:
        # Example 1: Basic PR review
        await example_1_basic_pr_review()

        # Example 2: Store in Cognee
        await example_2_store_in_cognee()

        # Example 3: Export markdown
        await example_3_export_markdown()

        # Example 4: Interactive review
        await example_4_interactive_review()

        # Example 5: XP leaderboard
        await example_5_xp_leaderboard()

        # Example 6: Pattern learning
        await example_6_pattern_learning()

        # Example 7: Full workflow
        await example_7_full_governance_workflow()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        await cleanup_pr_quest_client()
        print("\n✅ Cleanup complete")


if __name__ == "__main__":
    print("=" * 60)
    print("PR-QUEST Integration Examples for PIPE Governance")
    print("=" * 60)

    # Check environment
    if "GITHUB_TOKEN" not in os.environ:
        print("\n⚠️  Warning: GITHUB_TOKEN not set")
        print("   Set with: export GITHUB_TOKEN=ghp_xxx\n")

    if "OPENAI_API_KEY" not in os.environ:
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("   PR-QUEST LLM features will not work")
        print("   Set with: export OPENAI_API_KEY=sk-xxx\n")

    # Run examples
    asyncio.run(main())
