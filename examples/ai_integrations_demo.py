"""
AI Integrations Demo - MCP + OpenSpec + Cognee

This example demonstrates how to use all three AI integrations together:
1. MCP for external tool access (GitHub, Slack, Postgres)
2. OpenSpec for API specification management
3. Cognee for knowledge graph and memory

Scenario: Complete workflow for a new API change
"""

import asyncio
from datetime import datetime
from src.governance.governance_manager import GovernanceManager
from src.core.event_bus import Event, EventBus
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector


async def integrated_api_change_workflow():
    """
    Demonstrate complete workflow:
    1. Query GitHub for similar PRs (MCP)
    2. Query Cognee for similar past changes
    3. Create OpenSpec proposal for API change
    4. Go through governance approval
    5. Cognify the decision for future reference
    6. Notify team via Slack (MCP)
    """
    # Initialize components
    event_bus = EventBus()
    state_manager = StateManager()
    metrics = MetricsCollector()
    governance = GovernanceManager()

    print("=" * 80)
    print("AI Integrations Demo: Complete API Change Workflow")
    print("=" * 80)
    print()

    # =================================================================
    # STEP 1: Query GitHub for Similar PRs using MCP
    # =================================================================
    print("[STEP 1] Querying GitHub for similar PRs (via MCP)...")
    print("-" * 80)

    github_request_id = "DEMO-GH-001"

    # Publish MCP tool call to search GitHub
    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="DEMO",
            data={
                "request_id": github_request_id,
                "server": "github",
                "tool": "search_pull_requests",
                "arguments": {
                    "repo": "pipe-ecosystem",
                    "query": "API changes authentication",
                    "state": "closed",
                },
            },
        )
    )

    print(f"  ✓ GitHub search requested (MCP)")
    print(f"    Request ID: {github_request_id}")
    print(f"    Searching for: Similar authentication API changes")
    await asyncio.sleep(0.5)

    # Simulate GitHub response
    github_results = [
        {"number": 42, "title": "Add OAuth endpoints", "merged_at": "2024-01-15"},
        {"number": 67, "title": "Update auth tokens", "merged_at": "2024-02-10"},
    ]

    print(f"  ✓ Found {len(github_results)} similar PRs:")
    for pr in github_results:
        print(f"    - PR #{pr['number']}: {pr['title']}")
    print()

    # =================================================================
    # STEP 2: Query Cognee for Historical Context
    # =================================================================
    print("[STEP 2] Querying knowledge graph for past decisions (via Cognee)...")
    print("-" * 80)

    cognee_request_id = "DEMO-COG-001"

    # Publish Cognee query
    await event_bus.publish(
        Event(
            event_type="cognee.query",
            source="DEMO",
            data={
                "request_id": cognee_request_id,
                "query": "What were the outcomes of past authentication API changes?",
            },
        )
    )

    print(f"  ✓ Cognee query sent")
    print(f"    Request ID: {cognee_request_id}")
    print(f"    Query: Past authentication API change outcomes")
    await asyncio.sleep(0.5)

    # Simulate Cognee insights
    cognee_insights = [
        "Most authentication changes required 2-3 weeks implementation",
        "Breaking changes in auth required 6-month deprecation period",
        "All auth changes needed security team approval",
    ]

    print(f"  ✓ Knowledge graph insights:")
    for insight in cognee_insights:
        print(f"    • {insight}")
    print()

    # =================================================================
    # STEP 3: Create OpenSpec Proposal
    # =================================================================
    print("[STEP 3] Creating OpenSpec proposal for API change...")
    print("-" * 80)

    proposal_name = "add-2fa-authentication"

    print(f"  ✓ OpenSpec proposal created: {proposal_name}")
    print(f"    Location: openspec/changes/{proposal_name}/")
    print(f"    Files:")
    print(f"      - proposal.md (goal and motivation)")
    print(f"      - tasks.md (implementation tasks)")
    print(f"      - spec-delta.yaml (API changes)")
    print()

    # Simulate proposal content
    proposal_summary = {
        "title": "Add Two-Factor Authentication",
        "endpoints": [
            "POST /auth/2fa/enable",
            "POST /auth/2fa/verify",
            "DELETE /auth/2fa/disable",
        ],
        "breaking_change": False,
        "affected_domains": ["BNI", "BNP", "AXIS", "IV"],
    }

    print(f"  Proposal Summary:")
    print(f"    Title: {proposal_summary['title']}")
    print(f"    New Endpoints: {len(proposal_summary['endpoints'])}")
    for endpoint in proposal_summary["endpoints"]:
        print(f"      - {endpoint}")
    print(f"    Breaking Change: {proposal_summary['breaking_change']}")
    print(f"    Affected Domains: {', '.join(proposal_summary['affected_domains'])}")
    print()

    # =================================================================
    # STEP 4: Governance Review & Approval
    # =================================================================
    print("[STEP 4] Submitting to governance review...")
    print("-" * 80)

    # Request integration change
    integration = await governance.request_integration(
        source_domain="BNI",
        target_domain="ALL",
        integration_type="api_change",
        purpose="Add two-factor authentication endpoints",
        metadata={
            "openspec_proposal": proposal_name,
            "breaking_change": False,
            "github_prs_reviewed": [42, 67],
            "cognee_insights_considered": True,
        },
    )

    print(f"  ✓ Integration change requested")
    print(f"    Integration ID: {integration['integration_id']}")
    print(f"    Review ID: {integration['review_id']}")
    print()

    # Assign reviewers
    reviewers = ["security@pipe.com", "architect@pipe.com"]
    governance.review_pipeline.assign_reviewers(integration["review_id"], reviewers)

    print(f"  ✓ Reviewers assigned:")
    for reviewer in reviewers:
        print(f"    - {reviewer}")
    print()

    # Simulate review approvals
    print(f"  Reviewing proposal...")
    for reviewer in reviewers:
        governance.review_pipeline.approve_review(integration["review_id"], reviewer)
        print(f"    ✓ Approved by: {reviewer}")

    # Final approval
    await governance.approve_integration(
        integration["integration_id"],
        reviewer="admin@pipe.com",
        notes="2FA authentication API approved. All governance checks passed.",
    )

    print(f"  ✓ Integration APPROVED by admin@pipe.com")
    print()

    # =================================================================
    # STEP 5: Cognify the Decision
    # =================================================================
    print("[STEP 5] Cognifying decision for future reference...")
    print("-" * 80)

    # Publish approval event (Cognee will automatically cognify it)
    await event_bus.publish(
        Event(
            event_type="integration.approved",
            source="GOVERNANCE",
            data={
                "integration_id": integration["integration_id"],
                "proposal": proposal_summary["title"],
                "openspec_change": proposal_name,
                "approved_by": "admin@pipe.com",
                "approved_at": datetime.now().isoformat(),
                "review_duration_days": 3,
                "reviewers": reviewers,
                "endpoints_added": len(proposal_summary["endpoints"]),
                "breaking_change": False,
                "affected_domains": proposal_summary["affected_domains"],
            },
        )
    )

    print(f"  ✓ Decision cognified into knowledge graph")
    print(f"    Event: integration.approved")
    print(f"    Entities extracted: Integration, Domains, Reviewers")
    print(f"    Relationships created: INTEGRATES_WITH, APPROVED_BY, AFFECTS")
    print(f"    Future queries will include this decision")
    print()

    # =================================================================
    # STEP 6: Notify Team via Slack (MCP)
    # =================================================================
    print("[STEP 6] Notifying team via Slack (via MCP)...")
    print("-" * 80)

    slack_request_id = "DEMO-SLACK-001"

    # Publish Slack notification via MCP
    await event_bus.publish(
        Event(
            event_type="mcp.tool.call",
            source="DEMO",
            data={
                "request_id": slack_request_id,
                "server": "slack",
                "tool": "post_message",
                "arguments": {
                    "channel": "#api-changes",
                    "text": f"""
🎉 *API Change Approved*

*Proposal:* {proposal_summary['title']}
*Integration ID:* {integration['integration_id']}
*Endpoints Added:* {len(proposal_summary['endpoints'])}
*Breaking Change:* No
*Affected Domains:* {', '.join(proposal_summary['affected_domains'])}

*OpenSpec:* `openspec/changes/{proposal_name}/`

Ready to implement! 🚀
                    """.strip(),
                },
            },
        )
    )

    print(f"  ✓ Slack notification sent")
    print(f"    Channel: #api-changes")
    print(f"    Message: API change approval announcement")
    print()

    # =================================================================
    # WORKFLOW COMPLETE
    # =================================================================
    print("=" * 80)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 80)
    print()

    print("Summary:")
    print(f"  • Queried GitHub for {len(github_results)} similar PRs")
    print(f"  • Retrieved {len(cognee_insights)} insights from knowledge graph")
    print(f"  • Created OpenSpec proposal: {proposal_name}")
    print(f"  • Obtained {len(reviewers)} governance approvals")
    print(f"  • Cognified decision for future AI context")
    print(f"  • Notified team via Slack")
    print()

    print("Next Steps:")
    print(
        "  1. Implement changes: Follow tasks in openspec/changes/add-2fa-authentication/tasks.md"
    )
    print("  2. Apply spec changes: /openspec:apply add-2fa-authentication")
    print("  3. Archive after completion: /openspec:archive add-2fa-authentication")
    print()

    print("Benefits of Integrated AI Tools:")
    print("  ✓ MCP: External tool access (GitHub, Slack, databases)")
    print("  ✓ OpenSpec: Clear API specification and change tracking")
    print("  ✓ Cognee: Institutional memory and historical context")
    print("  ✓ PIPE: Governance, compliance, and integration management")
    print()

    # Return summary for testing
    return {
        "github_prs_found": len(github_results),
        "cognee_insights": len(cognee_insights),
        "openspec_proposal": proposal_name,
        "integration_id": integration["integration_id"],
        "approvals_received": len(reviewers),
        "notification_sent": True,
        "workflow_duration_seconds": 10,
    }


async def demo_query_patterns():
    """
    Demonstrate common query patterns across all three integrations.
    """
    print("\n" + "=" * 80)
    print("Common Query Patterns")
    print("=" * 80)
    print()

    # MCP Queries
    print("MCP Query Patterns:")
    print("-" * 40)
    print("1. GitHub: Search repositories, PRs, issues")
    print("   await mcp_call('github', 'search_pull_requests', {...})")
    print()
    print("2. Slack: Post messages, get channel info")
    print("   await mcp_call('slack', 'post_message', {...})")
    print()
    print("3. Postgres: Query analytics data")
    print("   await mcp_call('postgres', 'execute_query', {...})")
    print()

    # OpenSpec Queries
    print("OpenSpec Patterns:")
    print("-" * 40)
    print("1. Create proposal: /openspec:proposal 'description'")
    print("2. Apply changes: /openspec:apply proposal-name")
    print("3. Archive completed: /openspec:archive proposal-name")
    print("4. Validate spec: openspec validate proposal-name")
    print()

    # Cognee Queries
    print("Cognee Query Patterns:")
    print("-" * 40)
    print("1. Historical decisions:")
    print("   'What integrations were approved last month?'")
    print()
    print("2. Compliance trends:")
    print("   'Show compliance trends for AXIS domain'")
    print()
    print("3. Similar integrations:")
    print("   'Find integrations similar to authentication'")
    print()
    print("4. Temporal analysis:")
    print("   'How has integration approval time changed over 6 months?'")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║       PIPE AI Integrations Demo                               ║")
    print("║       MCP + OpenSpec + Cognee                                 ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("\n")

    # Run main workflow
    result = asyncio.run(integrated_api_change_workflow())

    # Show query patterns
    asyncio.run(demo_query_patterns())

    print("Demo completed successfully! ✨")
    print()
