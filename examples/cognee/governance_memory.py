"""
Cognee AI Memory for PIPE Governance

This example demonstrates how to use Cognee to build AI memory
for governance decisions, integration patterns, and compliance tracking.

The three-store architecture enables:
- Semantic search across governance history
- Graph navigation of domain relationships
- Learning from past decisions
"""

import asyncio
from src.integrations.cognee_client import get_cognee_client, SearchMode
from src.governance.datapoints import (
    DomainDataPoint,
    IntegrationDataPoint,
    ReviewDecisionDataPoint,
    ComplianceRecordDataPoint,
    IntegrationPatternDataPoint,
)


async def example_1_add_domains():
    """
    Example 1: Add domains to AI memory.

    This creates DataPoints for all 9 domains in the BSW ecosystem
    and builds a knowledge graph of their relationships.
    """
    print("\n" + "=" * 60)
    print("Example 1: Building Domain Knowledge Graph")
    print("=" * 60)

    client = await get_cognee_client()

    # Create domain DataPoints
    domains = [
        DomainDataPoint(
            code="BNI",
            name="Blockchain Network Infrastructure",
            capabilities=["blockchain", "distributed_ledger", "consensus"],
            status="active",
            description="Core blockchain infrastructure for the ecosystem",
        ),
        DomainDataPoint(
            code="BNP",
            name="Blockchain Network Protocol",
            capabilities=["protocol", "smart_contracts", "tokenization"],
            status="active",
            description="Protocol layer for blockchain operations",
        ),
        DomainDataPoint(
            code="PIPE",
            name="Platform for Integration, Processing, and Execution",
            capabilities=["integration", "orchestration", "governance"],
            status="active",
            description="Central integration hub with governance",
        ),
        DomainDataPoint(
            code="AXIS",
            name="Authentication and Identity Services",
            capabilities=["identity", "authentication", "authorization"],
            status="active",
            description="Identity and access management",
        ),
        DomainDataPoint(
            code="IV",
            name="Identity Verification",
            capabilities=["verification", "kyc", "compliance"],
            status="active",
            description="Identity verification and KYC",
        ),
    ]

    # Add domains to Cognee
    await client.add_datapoints(domains)
    print(f"✓ Added {len(domains)} domains to AI memory")

    # Cognify to build knowledge graph
    await client.cognify_governance_data()
    print("✓ Built knowledge graph from domain data")

    # Search for domains with specific capabilities
    results = await client.search_integrations(
        "domains with blockchain capabilities", limit=3
    )
    print(f"\n✓ Found {len(results)} domains with blockchain capabilities")


async def example_2_track_integrations():
    """
    Example 2: Track integration patterns.

    Learn from successful integrations to suggest optimal paths
    for future integration requests.
    """
    print("\n" + "=" * 60)
    print("Example 2: Learning Integration Patterns")
    print("=" * 60)

    client = await get_cognee_client()

    # Create integration DataPoints
    integrations = [
        IntegrationDataPoint(
            integration_id="INT-001",
            source_domain="BNI",
            target_domain="PIPE",
            integration_type="hub",
            description="Hub connection for blockchain infrastructure data flow",
            status="connected",
            priority="high",
            created_timestamp=1234567890000,
            approved_timestamp=1234567891000,
            approvers=["reviewer-1", "reviewer-2"],
        ),
        IntegrationDataPoint(
            integration_id="INT-002",
            source_domain="BNP",
            target_domain="PIPE",
            integration_type="hub",
            description="Protocol layer integration for smart contract execution",
            status="connected",
            priority="high",
            created_timestamp=1234567892000,
            approved_timestamp=1234567893000,
            approvers=["reviewer-1", "reviewer-3"],
        ),
        IntegrationDataPoint(
            integration_id="INT-003",
            source_domain="AXIS",
            target_domain="IV",
            integration_type="direct",
            description="Direct authentication flow for identity verification",
            status="connected",
            priority="critical",
            created_timestamp=1234567894000,
            approved_timestamp=1234567895000,
            approvers=["reviewer-2", "reviewer-3"],
        ),
    ]

    await client.add_datapoints(integrations)
    print(f"✓ Added {len(integrations)} integrations to memory")

    await client.cognify_governance_data()
    print("✓ Learned integration patterns")

    # Find similar integrations
    similar = await client.search_integrations(
        "hub integrations for blockchain domains", limit=5
    )
    print(f"\n✓ Found {len(similar)} similar integration patterns")

    # Suggest integration path
    suggestion = await client.suggest_integration_path("EcoX", "PIPE")
    print(f"\n✓ Integration suggestion confidence: {suggestion['confidence']:.2f}")


async def example_3_compliance_memory():
    """
    Example 3: Build compliance memory.

    Track compliance issues across domains and find similar issues
    using semantic search.
    """
    print("\n" + "=" * 60)
    print("Example 3: Compliance Issue Tracking")
    print("=" * 60)

    client = await get_cognee_client()

    # Create compliance DataPoints
    compliance_records = [
        ComplianceRecordDataPoint(
            record_id="COMP-001",
            entity_id="BNI",
            entity_type="domain",
            domain="BNI",
            category="security_policy",
            level="compliant",
            findings="All security policies properly implemented",
            recommendations="Continue current security practices",
            check_timestamp=1234567890000,
        ),
        ComplianceRecordDataPoint(
            record_id="COMP-002",
            entity_id="INT-001",
            entity_type="integration",
            domain="PIPE",
            category="integration_standards",
            level="partial",
            findings="Integration follows hub pattern but lacks rate limiting",
            recommendations="Implement rate limiting to achieve full compliance",
            check_timestamp=1234567891000,
        ),
        ComplianceRecordDataPoint(
            record_id="COMP-003",
            entity_id="BNP",
            entity_type="domain",
            domain="BNP",
            category="data_governance",
            level="non_compliant",
            findings="Data retention policies not properly documented",
            recommendations="Document and implement data retention policies",
            check_timestamp=1234567892000,
        ),
    ]

    await client.add_datapoints(compliance_records)
    print(f"✓ Added {len(compliance_records)} compliance records")

    await client.cognify_governance_data()
    print("✓ Built compliance knowledge graph")

    # Find similar compliance issues
    similar_issues = await client.find_similar_compliance_issues(
        "missing documentation for data policies", domain="BNP"
    )
    print(f"\n✓ Found {len(similar_issues)} similar compliance issues")


async def example_4_review_precedent():
    """
    Example 4: Learn from review decisions.

    Build memory of review decisions to find precedent for
    future review requests.
    """
    print("\n" + "=" * 60)
    print("Example 4: Review Decision Precedent")
    print("=" * 60)

    client = await get_cognee_client()

    # Create review DataPoints
    reviews = [
        ReviewDecisionDataPoint(
            review_id="REV-001",
            review_type="integration",
            title="BNI to PIPE Hub Integration",
            decision="approved",
            rationale="Hub pattern approved. Strong security controls and proper governance flow established.",
            reviewer="senior-architect-1",
            source_domain="BNI",
            target_domain="PIPE",
            priority="high",
            created_timestamp=1234567890000,
            decision_timestamp=1234567891000,
            integration="INT-001",
        ),
        ReviewDecisionDataPoint(
            review_id="REV-002",
            review_type="security",
            title="AXIS Authentication Security Review",
            decision="requires_changes",
            rationale="Encryption implementation needs strengthening. Request implementation of TLS 1.3 and certificate pinning.",
            reviewer="security-lead-1",
            source_domain="AXIS",
            priority="critical",
            created_timestamp=1234567892000,
            decision_timestamp=1234567893000,
        ),
        ReviewDecisionDataPoint(
            review_id="REV-003",
            review_type="compliance",
            title="BNP Data Governance Compliance",
            decision="rejected",
            rationale="Data retention policies missing. Cannot approve until documented and implemented per policy GOV-101.",
            reviewer="compliance-officer-1",
            source_domain="BNP",
            priority="high",
            created_timestamp=1234567894000,
            decision_timestamp=1234567895000,
            compliance_records=["COMP-003"],
        ),
    ]

    await client.add_datapoints(reviews)
    print(f"✓ Added {len(reviews)} review decisions to memory")

    await client.cognify_governance_data()
    print("✓ Learned from review precedents")

    # Search for similar review decisions
    similar_reviews = await client.search_integrations(
        "hub integration approvals with strong security", limit=3
    )
    print(f"\n✓ Found {len(similar_reviews)} similar review decisions")

    # Learn from a new decision
    await client.learn_from_review_decision(
        review_id="REV-004",
        decision="approved",
        rationale="Direct integration approved due to critical priority and existing security framework",
    )
    print("\n✓ Learned from new review decision")


async def example_5_integration_patterns():
    """
    Example 5: Discover and learn integration patterns.

    Track successful patterns to guide future integrations.
    """
    print("\n" + "=" * 60)
    print("Example 5: Integration Pattern Learning")
    print("=" * 60)

    client = await get_cognee_client()

    # Create pattern DataPoints
    patterns = [
        IntegrationPatternDataPoint(
            pattern_id="PAT-001",
            pattern_name="Hub-and-Spoke for Central Domains",
            pattern_description="All domains connect through PIPE hub for centralized governance and orchestration",
            source_domain_type="any",
            target_domain_type="hub",
            integration_type="hub",
            success_rate=0.95,
            success_factors=[
                "Centralized governance",
                "Single point of monitoring",
                "Easier compliance tracking",
                "Reduced integration complexity",
            ],
            failure_factors=["Single point of failure risk"],
            use_cases=["Multi-domain orchestration", "Governance enforcement"],
            examples=["INT-001", "INT-002"],
        ),
        IntegrationPatternDataPoint(
            pattern_id="PAT-002",
            pattern_name="Direct Point-to-Point for Critical Paths",
            pattern_description="Direct connections for high-priority, low-latency requirements",
            source_domain_type="identity",
            target_domain_type="verification",
            integration_type="direct",
            success_rate=0.85,
            success_factors=[
                "Low latency",
                "High availability",
                "Reduced hops",
                "Critical path optimization",
            ],
            failure_factors=[
                "Harder to govern",
                "More complex to monitor",
                "Higher coupling",
            ],
            use_cases=["Real-time verification", "Critical authentication"],
            examples=["INT-003"],
        ),
    ]

    await client.add_datapoints(patterns)
    print(f"✓ Added {len(patterns)} integration patterns")

    await client.cognify_governance_data()
    print("✓ Learned integration patterns")

    # Find patterns for a specific use case
    pattern_results = await client.find_integration_patterns(
        "low latency critical authentication", limit=5
    )
    print(f"\n✓ Found {len(pattern_results)} matching patterns")


async def example_6_domain_context():
    """
    Example 6: Get comprehensive domain context.

    Use graph traversal to gather all related information about a domain.
    """
    print("\n" + "=" * 60)
    print("Example 6: Domain Context Gathering")
    print("=" * 60)

    client = await get_cognee_client()

    # Get comprehensive context for BNI domain
    context = await client.get_domain_context("BNI")

    print(f"\n✓ Retrieved context for domain: {context['domain']}")
    print(f"✓ Total context items: {context['total_items']}")
    print("\nContext includes:")
    print("  - Domain capabilities")
    print("  - Active integrations")
    print("  - Compliance history")
    print("  - Review decisions")
    print("  - Related patterns")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PIPE + Cognee: AI Memory for Governance")
    print("=" * 60)
    print("\nThis demonstrates how Cognee builds AI memory for PIPE:")
    print("  • Semantic search across governance data")
    print("  • Knowledge graph of domain relationships")
    print("  • Learning from past decisions")
    print("  • Pattern recognition and suggestions")

    # Run examples sequentially
    await example_1_add_domains()
    await example_2_track_integrations()
    await example_3_compliance_memory()
    await example_4_review_precedent()
    await example_5_integration_patterns()
    await example_6_domain_context()

    print("\n" + "=" * 60)
    print("All Examples Completed Successfully!")
    print("=" * 60)
    print("\nCognee has built AI memory containing:")
    print("  ✓ Domain knowledge graph")
    print("  ✓ Integration patterns")
    print("  ✓ Compliance history")
    print("  ✓ Review precedents")
    print("\nThis memory can now be queried for:")
    print("  • Similar integration patterns")
    print("  • Compliance issue precedents")
    print("  • Review decision rationale")
    print("  • Domain capability matching")
    print("  • Optimal integration paths")


if __name__ == "__main__":
    # Note: Requires Cognee to be installed and configured
    # pip install cognee
    # Set environment variables: LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, etc.

    try:
        asyncio.run(main())
    except ImportError as e:
        print(f"\nError: {e}")
        print("\nPlease install Cognee:")
        print("  pip install cognee")
        print("\nAnd configure your LLM provider:")
        print("  export OPENAI_API_KEY=your_key")
        print("  export LLM_PROVIDER=openai")
        print("  export LLM_MODEL=gpt-4")
