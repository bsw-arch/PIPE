#!/usr/bin/env python3
"""
PIPE Governance CLI Tool

Command-line interface for managing the PIPE AgenticAI Governance System.
Provides easy access to governance operations without writing code.

Usage:
    python scripts/governance_cli.py register-domain BNI --capabilities auth user_mgmt
    python scripts/governance_cli.py request-integration BNI BNP --type api
    python scripts/governance_cli.py dashboard
    python scripts/governance_cli.py compliance --domain BNI
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.governance.governance_manager import GovernanceManager  # noqa: E402


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


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_header(text: str):
    """Print header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")


def print_json(data: dict):
    """Print formatted JSON."""
    print(f"{Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.END}")


async def cmd_register_domain(args, governance: GovernanceManager):
    """Register a new domain."""
    print_header(f"Registering Domain: {args.domain}")

    capabilities = args.capabilities if args.capabilities else []
    result = await governance.register_domain(args.domain, capabilities)

    if result["success"]:
        print_success(f"Domain {args.domain} registered successfully")
        print_info(f"  Compliance ID: {result['compliance_id']}")
        print_info(f"  Status: {result['status']}")
        if capabilities:
            print_info(f"  Capabilities: {', '.join(capabilities)}")
    else:
        print_error(
            f"Failed to register domain: {result.get('error', 'Unknown error')}"
        )
        sys.exit(1)


async def cmd_request_integration(args, governance: GovernanceManager):
    """Request a cross-domain integration."""
    print_header(f"Requesting Integration: {args.source} → {args.target}")

    result = await governance.request_integration(
        source_domain=args.source,
        target_domain=args.target,
        integration_type=args.type,
        description=args.description or f"Integration: {args.source} → {args.target}",
        priority=args.priority,
    )

    if result["success"]:
        print_success("Integration request created")
        print_info(f"  Integration ID: {result['integration_id']}")
        print_info(f"  Review ID: {result['review_id']}")
        print_info(f"  Status: {result['status']}")
        print_info(f"  Compliance ID: {result['compliance_id']}")
    else:
        print_error(
            f"Integration request failed: {result.get('error', 'Unknown error')}"
        )
        sys.exit(1)


async def cmd_approve_integration(args, governance: GovernanceManager):
    """Approve an integration request."""
    print_header(f"Approving Integration: {args.integration_id}")

    result = await governance.approve_integration(
        integration_id=args.integration_id,
        reviewer=args.reviewer or "cli.user@example.com",
        notes=args.notes,
    )

    if result["success"]:
        print_success(f"Integration {args.integration_id} approved")
        print_info(f"  Status: {result['status']}")
        if result.get("review_id"):
            print_info(f"  Review ID: {result['review_id']}")
    else:
        print_error(f"Approval failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


async def cmd_dashboard(args, governance: GovernanceManager):
    """Display governance dashboard."""
    print_header("PIPE Governance Dashboard")

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

    if dashboard["compliance"]["by_domain"]:
        print_info("\n  By Domain:")
        for domain, data in dashboard["compliance"]["by_domain"].items():
            print(
                f"    {domain}: {data['percentage']:.1f}% "
                f"({data['compliant']}/{data['total']} compliant)"
            )

    print_info("\nReview Statistics:")
    print(f"  Total Reviews: {dashboard['reviews']['total']}")
    print(f"  Pending: {dashboard['reviews']['pending']}")
    print(f"  In Review: {dashboard['reviews']['in_review']}")
    print(f"  Approved: {dashboard['reviews']['approved']}")

    if dashboard["domains"]:
        print_info("\nActive Domains:")
        for domain_code, domain_info in dashboard["domains"].items():
            print(
                f"  {domain_code}: {domain_info['name']} "
                f"({domain_info['status']}, {domain_info['connections']} connections)"
            )

    if args.json:
        print("\n")
        print_json(dashboard)


async def cmd_compliance(args, governance: GovernanceManager):
    """Show compliance status."""
    if args.domain:
        print_header(f"Compliance Status: {args.domain}")
        summary = governance.compliance_tracker.get_domain_compliance_summary(
            args.domain
        )

        print_success(f"Domain: {args.domain}")
        print(f"  Total Entities: {summary['total_entities']}")
        print(f"  Compliance Percentage: {summary['compliance_percentage']:.1f}%")
        print("\n  Status Summary:")
        print(f"    Compliant: {summary['compliance_summary']['compliant']}")
        print(f"    Partial: {summary['compliance_summary']['partial']}")
        print(f"    Non-Compliant: {summary['compliance_summary']['non_compliant']}")
        print(f"    Not Evaluated: {summary['compliance_summary']['not_evaluated']}")

        if args.json:
            print("\n")
            print_json(summary)
    else:
        print_header("Ecosystem Compliance")
        ecosystem = governance.compliance_tracker.get_ecosystem_compliance()

        print_success("Ecosystem-Wide Compliance")
        print(f"  Total Entities: {ecosystem['total_entities']}")
        print(
            f"  Overall Compliance: {ecosystem['ecosystem_compliance_percentage']:.1f}%"
        )

        if ecosystem["domains"]:
            print_info("\n  By Domain:")
            for domain, data in ecosystem["domains"].items():
                print(
                    f"    {domain}: {data['compliance_percentage']:.1f}% "
                    f"({data['total_entities']} entities)"
                )

        if args.json:
            print("\n")
            print_json(ecosystem)


async def cmd_status(args, governance: GovernanceManager):
    """Show domain status."""
    print_header(f"Domain Status: {args.domain}")

    status = governance.get_domain_status(args.domain)

    if not status:
        print_error(f"Domain not found: {args.domain}")
        sys.exit(1)

    print_success("Domain Information:")
    print(f"  Code: {status['domain']['code']}")
    print(f"  Name: {status['domain']['name']}")
    print(f"  Status: {status['domain']['status']}")
    print(f"  Capabilities: {', '.join(status['domain']['capabilities'])}")

    print_info("\nConnectivity:")
    print(f"  Connected Domains: {status['connectivity']['connected_domains']}")
    print(f"  Connections: {', '.join(status['connectivity']['connections'])}")
    print(f"  Total Integrations: {status['connectivity']['integrations']}")

    print_info("\nCompliance:")
    print(f"  Total Entities: {status['compliance']['total_entities']}")
    print(f"  Compliance: {status['compliance']['compliance_percentage']:.1f}%")

    print_info("\nReviews:")
    print(f"  Total: {status['reviews']['total']}")
    print(f"  Pending: {status['reviews']['pending']}")
    print(f"  Approved: {status['reviews']['approved']}")

    if args.json:
        print("\n")
        print_json(status)


async def cmd_list_reviews(args, governance: GovernanceManager):
    """List reviews."""
    print_header("Review List")

    from src.governance.review_pipeline import ReviewStatus, ReviewType

    status_filter = None
    if args.status:
        try:
            status_filter = ReviewStatus[args.status.upper()]
        except KeyError:
            print_error(f"Invalid status: {args.status}")
            print_info(f"Valid statuses: {', '.join([s.value for s in ReviewStatus])}")
            sys.exit(1)

    type_filter = None
    if args.type:
        try:
            type_filter = ReviewType[args.type.upper()]
        except KeyError:
            print_error(f"Invalid type: {args.type}")
            print_info(f"Valid types: {', '.join([t.value for t in ReviewType])}")
            sys.exit(1)

    reviews = governance.review_pipeline.list_reviews(
        status=status_filter, review_type=type_filter, domain=args.domain
    )

    if not reviews:
        print_info("No reviews found")
        return

    print_success(f"Found {len(reviews)} review(s)")
    for review in reviews:
        print(f"\n  {review['id']}: {review['title']}")
        print(f"    Status: {review['status'].value}")
        print(f"    Type: {review['type'].value}")
        print(f"    Priority: {review['priority'].value}")
        print(f"    {review['source_domain']} → {review['target_domain']}")
        print(f"    Reviewers: {len(review['reviewers'])}")
        print(f"    Approvals: {len(review['approvals'])}/{len(review['reviewers'])}")

    if args.json:
        # Convert enums to values for JSON serialization
        json_reviews = []
        for review in reviews:
            json_review = dict(review)
            json_review["status"] = review["status"].value
            json_review["type"] = review["type"].value
            json_review["priority"] = review["priority"].value
            json_reviews.append(json_review)
        print("\n")
        print_json(json_reviews)


async def cmd_list_integrations(args, governance: GovernanceManager):
    """List integrations."""
    print_header("Integration List")

    integrations = governance.domain_registry.list_integrations(
        domain_code=args.domain, status=args.status
    )

    if not integrations:
        print_info("No integrations found")
        return

    print_success(f"Found {len(integrations)} integration(s)")
    for integration in integrations:
        print(f"\n  {integration['id']}")
        print(f"    {integration['source']} → {integration['target']}")
        print(f"    Type: {integration['type']}")
        print(f"    Status: {integration['status'].value}")
        print(f"    Created: {integration['created_at']}")

    if args.json:
        # Convert enums to values for JSON serialization
        json_integrations = []
        for integration in integrations:
            json_int = dict(integration)
            json_int["status"] = integration["status"].value
            json_integrations.append(json_int)
        print("\n")
        print_json(json_integrations)


async def cmd_list_domains(args, governance: GovernanceManager):
    """List registered domains."""
    print_header("Registered Domains")

    domains = governance.domain_registry.list_domains()

    if not domains:
        print_info("No domains registered")
        return

    print_success(f"Found {len(domains)} domain(s)")
    for domain in domains:
        print(f"\n  {domain['code']}: {domain['name']}")
        print(f"    Status: {domain['status'].value}")
        print(f"    Capabilities: {', '.join(domain['capabilities'])}")
        print(f"    Registered: {domain['registered_at']}")

    if args.json:
        # Convert enums to values for JSON serialization
        json_domains = []
        for domain in domains:
            json_dom = dict(domain)
            json_dom["status"] = domain["status"].value
            json_domains.append(json_dom)
        print("\n")
        print_json(json_domains)


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="PIPE Governance CLI - Manage AgenticAI Governance System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register domain
    register_parser = subparsers.add_parser(
        "register-domain", help="Register a new domain"
    )
    register_parser.add_argument("domain", help="Domain code (e.g., BNI, BNP)")
    register_parser.add_argument(
        "--capabilities",
        nargs="+",
        help="Domain capabilities (space-separated)",
        default=[],
    )

    # Request integration
    integration_parser = subparsers.add_parser(
        "request-integration", help="Request cross-domain integration"
    )
    integration_parser.add_argument("source", help="Source domain code")
    integration_parser.add_argument("target", help="Target domain code")
    integration_parser.add_argument(
        "--type", default="api", help="Integration type (default: api)"
    )
    integration_parser.add_argument(
        "--description", help="Integration description (optional)"
    )
    integration_parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        default="medium",
        help="Priority level (default: medium)",
    )

    # Approve integration
    approve_parser = subparsers.add_parser(
        "approve", help="Approve an integration request"
    )
    approve_parser.add_argument("integration_id", help="Integration ID to approve")
    approve_parser.add_argument(
        "--reviewer", help="Reviewer identifier (default: cli.user@example.com)"
    )
    approve_parser.add_argument("--notes", help="Approval notes (optional)")

    # Dashboard
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Display governance dashboard"
    )
    dashboard_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Compliance
    compliance_parser = subparsers.add_parser(
        "compliance", help="Show compliance status"
    )
    compliance_parser.add_argument(
        "--domain", help="Show compliance for specific domain (optional)"
    )
    compliance_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Status
    status_parser = subparsers.add_parser("status", help="Show domain status")
    status_parser.add_argument("domain", help="Domain code")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List reviews
    reviews_parser = subparsers.add_parser("list-reviews", help="List reviews")
    reviews_parser.add_argument(
        "--status",
        help="Filter by status (pending, in_review, approved, rejected, etc.)",
    )
    reviews_parser.add_argument(
        "--type",
        help="Filter by type (integration, security, quality, architecture, compliance)",
    )
    reviews_parser.add_argument("--domain", help="Filter by domain")
    reviews_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List integrations
    integrations_parser = subparsers.add_parser(
        "list-integrations", help="List integrations"
    )
    integrations_parser.add_argument("--domain", help="Filter by domain")
    integrations_parser.add_argument(
        "--status", help="Filter by status (pending, connected, degraded, disconnected)"
    )
    integrations_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # List domains
    domains_parser = subparsers.add_parser(
        "list-domains", help="List registered domains"
    )
    domains_parser.add_argument("--json", action="store_true", help="Output as JSON")

    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize governance manager
    governance = GovernanceManager()

    # Command dispatch
    commands = {
        "register-domain": cmd_register_domain,
        "request-integration": cmd_request_integration,
        "approve": cmd_approve_integration,
        "dashboard": cmd_dashboard,
        "compliance": cmd_compliance,
        "status": cmd_status,
        "list-reviews": cmd_list_reviews,
        "list-integrations": cmd_list_integrations,
        "list-domains": cmd_list_domains,
    }

    handler = commands.get(args.command)
    if handler:
        await handler(args, governance)
    else:
        print_error(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
