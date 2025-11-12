"""
PIPE AgenticAI Governance System - Interactive Demo

This demo showcases the complete governance workflow including:
- Domain registration
- Integration requests and approvals
- Cross-domain message routing
- Compliance tracking
- Governance dashboard

Run with: python examples/governance_demo.py
"""

import asyncio
import json
from src.governance.governance_manager import GovernanceManager


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}\n")


def print_step(number: int, text: str):
    """Print formatted step."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Step {number}: {text}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * 70}{Colors.END}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_result(data: dict):
    """Print formatted JSON result."""
    print(f"{Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.END}")


async def demo_domain_registration(governance: GovernanceManager):
    """Demonstrate domain registration."""
    print_step(1, "Domain Registration")

    domains = {
        "BNI": ["authentication", "user_management", "access_control"],
        "BNP": ["business_services", "data_processing", "api_gateway"],
        "AXIS": ["architecture_governance", "integration_patterns", "service_mesh"],
    }

    for domain_code, capabilities in domains.items():
        print_info(f"Registering domain: {domain_code}")
        result = await governance.register_domain(domain_code, capabilities)

        if result["success"]:
            print_success(f"Domain {domain_code} registered successfully")
            print_info(f"  Capabilities: {', '.join(capabilities)}")
            print_info(f"  Compliance ID: {result['compliance_id']}")
        else:
            print(f"{Colors.RED}✗ Failed to register {domain_code}{Colors.END}")


async def demo_integration_request(governance: GovernanceManager):
    """Demonstrate integration request workflow."""
    print_step(2, "Integration Request")

    print_info("Requesting integration: BNI → BNP")
    result = await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Connect BNI authentication service to BNP business services",
        priority="high",
    )

    if result["success"]:
        print_success("Integration request created")
        print_info(f"  Integration ID: {result['integration_id']}")
        print_info(f"  Review ID: {result['review_id']}")
        print_info(f"  Status: {result['status']}")
        return result
    else:
        print(
            f"{Colors.RED}✗ Integration request failed: {result.get('error')}{Colors.END}"
        )
        return None


async def demo_review_process(governance: GovernanceManager, review_id: str):
    """Demonstrate review process."""
    print_step(3, "Review Process")

    # Assign reviewers
    print_info("Assigning reviewers to the integration request")
    reviewers = ["security.team@example.com", "architecture.team@example.com"]
    governance.review_pipeline.assign_reviewers(review_id, reviewers)
    print_success(f"Assigned {len(reviewers)} reviewers")

    # Add comments
    print_info("Reviewers adding comments...")
    governance.review_pipeline.add_comment(
        review_id,
        reviewers[0],
        "Security review: Authentication flow looks good. LGTM.",
    )
    governance.review_pipeline.add_comment(
        review_id,
        reviewers[1],
        "Architecture review: Integration pattern follows standards. Approved.",
    )
    print_success("Comments added by reviewers")

    # Approve from each reviewer
    print_info("Processing approvals...")
    for reviewer in reviewers:
        governance.review_pipeline.approve_review(
            review_id, reviewer, f"Approved by {reviewer}"
        )
        print_success(f"Approval received from {reviewer}")

    # Check review status
    review = governance.review_pipeline.get_review(review_id)
    print_success(f"Review status: {review['status'].value.upper()}")


async def demo_integration_approval(governance: GovernanceManager, integration_id: str):
    """Demonstrate integration approval."""
    print_step(4, "Integration Approval")

    print_info("Approving integration...")
    result = await governance.approve_integration(
        integration_id, "admin@example.com", "All reviews passed. Integration approved."
    )

    if result["success"]:
        print_success(f"Integration {integration_id} approved")
        print_info(f"  Status: {result['status']}")
    else:
        print(f"{Colors.RED}✗ Approval failed{Colors.END}")


async def demo_compliance_tracking(governance: GovernanceManager):
    """Demonstrate compliance tracking."""
    print_step(5, "Compliance Tracking")

    # Get domain compliance
    print_info("Checking compliance for BNI domain...")
    compliance_summary = governance.compliance_tracker.get_domain_compliance_summary(
        "BNI"
    )

    print_success("BNI Domain Compliance Summary:")
    print(f"  Total Entities: {compliance_summary['total_entities']}")
    print(
        f"  Compliance Percentage: {compliance_summary['compliance_percentage']:.1f}%"
    )
    print(f"  Compliant: {compliance_summary['compliance_summary']['compliant']}")
    print(f"  Partial: {compliance_summary['compliance_summary']['partial']}")
    print(
        f"  Non-Compliant: {compliance_summary['compliance_summary']['non_compliant']}"
    )

    # Ecosystem compliance
    print_info("\nChecking ecosystem-wide compliance...")
    ecosystem = governance.compliance_tracker.get_ecosystem_compliance()
    print_success("Ecosystem Compliance:")
    print(f"  Total Entities: {ecosystem['total_entities']}")
    print(f"  Overall Compliance: {ecosystem['ecosystem_compliance_percentage']:.1f}%")


async def demo_governance_dashboard(governance: GovernanceManager):
    """Demonstrate governance dashboard."""
    print_step(6, "Governance Dashboard")

    dashboard = governance.get_governance_dashboard()

    print_success("Ecosystem Overview:")
    print(f"  Total Domains: {dashboard['ecosystem']['total_domains']}")
    print(f"  Active Domains: {dashboard['ecosystem']['active_domains']}")
    print(f"  Total Integrations: {dashboard['ecosystem']['total_integrations']}")
    print(f"  Active Integrations: {dashboard['ecosystem']['active_integrations']}")

    print_info("\nCompliance Metrics:")
    print(
        f"  Ecosystem Compliance: {dashboard['compliance']['ecosystem_percentage']:.1f}%"
    )
    print(f"  Total Entities: {dashboard['compliance']['total_entities']}")

    print_info("\nReview Statistics:")
    print(f"  Total Reviews: {dashboard['reviews']['total']}")
    print(f"  Pending: {dashboard['reviews']['pending']}")
    print(f"  In Review: {dashboard['reviews']['in_review']}")
    print(f"  Approved: {dashboard['reviews']['approved']}")

    print_info("\nActive Domains:")
    for domain_code, domain_info in dashboard["domains"].items():
        print(
            f"  {domain_code}: {domain_info['name']} "
            f"({domain_info['status']}, {domain_info['connections']} connections)"
        )


async def demo_domain_status(governance: GovernanceManager):
    """Demonstrate domain status reporting."""
    print_step(7, "Domain Status Report")

    for domain_code in ["BNI", "BNP", "AXIS"]:
        print_info(f"\nStatus for domain: {domain_code}")
        status = governance.get_domain_status(domain_code)

        if status:
            print(f"  Name: {status['domain']['name']}")
            print(f"  Status: {status['domain']['status']}")
            print(f"  Capabilities: {', '.join(status['domain']['capabilities'])}")
            print(f"  Connected Domains: {status['connectivity']['connected_domains']}")
            print(f"  Total Integrations: {status['connectivity']['integrations']}")
            print(f"  Compliance: {status['compliance']['compliance_percentage']:.1f}%")
        else:
            print(f"{Colors.RED}  Domain not found{Colors.END}")


async def demo_additional_integrations(governance: GovernanceManager):
    """Demonstrate multiple integrations."""
    print_step(8, "Additional Integrations")

    integrations = [
        ("BNP", "AXIS", "event", "Event-driven integration for architecture sync"),
        (
            "AXIS",
            "BNI",
            "data",
            "Architecture patterns shared with authentication layer",
        ),
    ]

    for source, target, itype, description in integrations:
        print_info(f"Creating integration: {source} → {target}")

        result = await governance.request_integration(
            source, target, itype, description, "medium"
        )

        if result["success"]:
            # Quick approve for demo
            review_id = result["review_id"]
            governance.review_pipeline.assign_reviewers(
                review_id, ["auto.approver@example.com"]
            )
            governance.review_pipeline.approve_review(
                review_id, "auto.approver@example.com"
            )
            await governance.approve_integration(
                result["integration_id"], "admin@example.com"
            )

            print_success(f"Integration {source} → {target} created and approved")


async def demo_ecosystem_topology(governance: GovernanceManager):
    """Demonstrate ecosystem topology."""
    print_step(9, "Ecosystem Topology")

    topology = governance.domain_registry.get_ecosystem_topology()

    print_success("Ecosystem Topology:")
    print(f"  Total Integrations: {topology['total_integrations']}")
    print(f"  Active Integrations: {topology['active_integrations']}")

    print_info("\nConnection Matrix:")
    for domain, connections in topology["connection_matrix"].items():
        if connections:
            print(f"  {domain} → {', '.join(connections)}")


async def main():
    """Run the complete governance demo."""
    print_header("PIPE AgenticAI Governance System - Interactive Demo")

    print(f"{Colors.BOLD}This demo will showcase:{Colors.END}")
    print("  1. Domain registration across the ecosystem")
    print("  2. Integration request workflow")
    print("  3. Review and approval process")
    print("  4. Compliance tracking and monitoring")
    print("  5. Governance dashboard and reporting")
    print("\nStarting demo...\n")

    # Initialize governance manager
    governance = GovernanceManager()

    # Run demo steps
    await demo_domain_registration(governance)

    integration_result = await demo_integration_request(governance)
    if integration_result:
        await demo_review_process(governance, integration_result["review_id"])
        await demo_integration_approval(
            governance, integration_result["integration_id"]
        )

    await demo_additional_integrations(governance)
    await demo_compliance_tracking(governance)
    await demo_governance_dashboard(governance)
    await demo_domain_status(governance)
    await demo_ecosystem_topology(governance)

    # Final summary
    print_header("Demo Complete!")
    print(f"{Colors.GREEN}✓ Successfully demonstrated:")
    print("  • Domain registration (3 domains)")
    print("  • Integration workflows (3 integrations)")
    print("  • Review and approval process")
    print("  • Compliance tracking")
    print("  • Governance dashboard")
    print(f"  • Ecosystem topology{Colors.END}\n")

    print(f"{Colors.BOLD}Next Steps:{Colors.END}")
    print("  1. Try the CLI tool: python scripts/governance_cli.py --help")
    print("  2. Run tests: pytest tests/integration/test_governance_workflow.py")
    print("  3. Read documentation: docs/GOVERNANCE.md")
    print("  4. Explore the code: src/governance/\n")


if __name__ == "__main__":
    asyncio.run(main())
