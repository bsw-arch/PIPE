"""
Governance Utilities

Helper functions and utilities for PIPE governance operations including
batch operations, data export/import, validation, and report generation.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .governance_manager import GovernanceManager
from .review_pipeline import ReviewStatus


logger = logging.getLogger("pipe.governance.utils")


async def batch_register_domains(
    governance: GovernanceManager, domains_config: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Register multiple domains at once.

    Args:
        governance: GovernanceManager instance
        domains_config: Dict mapping domain codes to capability lists

    Returns:
        Results dictionary with success/failure counts

    Example:
        domains = {
            "BNI": ["authentication", "user_management"],
            "BNP": ["business_services", "data_processing"],
        }
        results = await batch_register_domains(governance, domains)
    """
    results = {"successful": [], "failed": [], "total": len(domains_config)}

    for domain_code, capabilities in domains_config.items():
        try:
            result = await governance.register_domain(domain_code, capabilities)
            if result["success"]:
                results["successful"].append(domain_code)
                logger.info(f"Registered domain: {domain_code}")
            else:
                results["failed"].append(
                    {"domain": domain_code, "error": result.get("error")}
                )
                logger.error(f"Failed to register {domain_code}: {result.get('error')}")
        except Exception as e:
            results["failed"].append({"domain": domain_code, "error": str(e)})
            logger.error(f"Exception registering {domain_code}: {str(e)}")

    results["success_count"] = len(results["successful"])
    results["failure_count"] = len(results["failed"])

    return results


async def batch_request_integrations(
    governance: GovernanceManager, integrations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Request multiple integrations at once.

    Args:
        governance: GovernanceManager instance
        integrations: List of integration configurations

    Returns:
        Results dictionary with success/failure counts

    Example:
        integrations = [
            {
                "source": "BNI",
                "target": "BNP",
                "type": "api",
                "description": "Auth to services",
                "priority": "high"
            },
            {
                "source": "BNP",
                "target": "AXIS",
                "type": "event",
                "description": "Event sync",
                "priority": "medium"
            }
        ]
        results = await batch_request_integrations(governance, integrations)
    """
    results = {"successful": [], "failed": [], "total": len(integrations)}

    for integration in integrations:
        try:
            result = await governance.request_integration(
                source_domain=integration["source"],
                target_domain=integration["target"],
                integration_type=integration.get("type", "api"),
                description=integration.get("description", ""),
                priority=integration.get("priority", "medium"),
            )

            if result["success"]:
                results["successful"].append(
                    {
                        "source": integration["source"],
                        "target": integration["target"],
                        "integration_id": result["integration_id"],
                        "review_id": result["review_id"],
                    }
                )
                logger.info(
                    f"Integration requested: {integration['source']} → {integration['target']}"
                )
            else:
                results["failed"].append(
                    {
                        "source": integration["source"],
                        "target": integration["target"],
                        "error": result.get("error"),
                    }
                )
                logger.error(
                    f"Failed integration: {integration['source']} → {integration['target']}"
                )

        except Exception as e:
            results["failed"].append(
                {
                    "source": integration.get("source"),
                    "target": integration.get("target"),
                    "error": str(e),
                }
            )
            logger.error(f"Exception requesting integration: {str(e)}")

    results["success_count"] = len(results["successful"])
    results["failure_count"] = len(results["failed"])

    return results


def export_governance_state(
    governance: GovernanceManager, output_path: Path
) -> Dict[str, Any]:
    """
    Export complete governance state to JSON file.

    Args:
        governance: GovernanceManager instance
        output_path: Path to output JSON file

    Returns:
        Export summary

    Example:
        export_governance_state(governance, Path("governance_backup.json"))
    """
    try:
        # Collect all governance data
        active_domains = governance.domain_registry.list_active_domains()
        domain_details = [
            {
                "domain_code": code,
                **governance.domain_registry.get_domain_info(code),
            }
            for code in active_domains
        ]

        state = {
            "exported_at": datetime.now().isoformat(),
            "domains": domain_details,
            "integrations": governance.domain_registry.list_integrations(),
            "reviews": [
                {
                    "review_id": rid,
                    "status": review["status"].value,
                    "reviewers": review["reviewers"],
                    "created_at": review["created_at"],
                }
                for rid, review in governance.review_pipeline.reviews.items()
            ],
            "compliance_records": list(
                governance.compliance_tracker.compliance_records.values()
            ),
            "dashboard": governance.get_governance_dashboard(),
        }

        # Convert enums to values for JSON serialization
        state = _serialize_for_json(state)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Exported governance state to {output_path}")

        return {
            "success": True,
            "path": str(output_path),
            "domains": len(state["domains"]),
            "integrations": len(state["integrations"]),
            "reviews": len(state["reviews"]),
        }

    except Exception as e:
        logger.error(f"Failed to export governance state: {str(e)}")
        return {"success": False, "error": str(e)}


def generate_compliance_report(
    governance: GovernanceManager, output_path: Optional[Path] = None
) -> str:
    """
    Generate comprehensive compliance report.

    Args:
        governance: GovernanceManager instance
        output_path: Optional path to save report (if None, returns string)

    Returns:
        Report as markdown string

    Example:
        report = generate_compliance_report(governance)
        print(report)

        # Or save to file
        generate_compliance_report(governance, Path("compliance_report.md"))
    """
    ecosystem = governance.compliance_tracker.get_ecosystem_compliance()
    dashboard = governance.get_governance_dashboard()

    report_lines = [
        "# PIPE Governance Compliance Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## Executive Summary",
        f"\n- **Total Entities:** {ecosystem['total_entities']}",
        f"- **Ecosystem Compliance:** {ecosystem['ecosystem_compliance_percentage']:.1f}%",
        f"- **Total Domains:** {dashboard['ecosystem']['total_domains']}",
        f"- **Active Integrations:** {dashboard['ecosystem']['active_integrations']}",
        "\n## Domain Compliance",
    ]

    for domain, data in ecosystem["domains"].items():
        report_lines.extend(
            [
                f"\n### {domain}",
                f"\n- **Total Entities:** {data['total_entities']}",
                f"- **Compliance Percentage:** {data['compliance_percentage']:.1f}%",
                f"- **Compliant:** {data['compliance_summary']['compliant']}",
                f"- **Partial:** {data['compliance_summary']['partial']}",
                f"- **Non-Compliant:** {data['compliance_summary']['non_compliant']}",
                f"- **Not Evaluated:** {data['compliance_summary']['not_evaluated']}",
            ]
        )

    report_lines.extend(
        [
            "\n## Review Statistics",
            f"\n- **Total Reviews:** {dashboard['reviews']['total']}",
            f"- **Pending:** {dashboard['reviews']['pending']}",
            f"- **In Review:** {dashboard['reviews']['in_review']}",
            f"- **Approved:** {dashboard['reviews']['approved']}",
            f"- **Requires Changes:** {dashboard['reviews']['requires_changes']}",
            "\n## Recommendations",
        ]
    )

    # Add recommendations based on data
    if ecosystem["ecosystem_compliance_percentage"] < 50:
        report_lines.append("\n- ⚠️ **CRITICAL**: Ecosystem compliance is below 50%")
    elif ecosystem["ecosystem_compliance_percentage"] < 75:
        report_lines.append("\n- ⚠️ **WARNING**: Ecosystem compliance is below 75%")
    else:
        report_lines.append("\n- ✓ Ecosystem compliance is healthy")

    if dashboard["reviews"]["pending"] > 5:
        report_lines.append(
            f"\n- ⚠️ High number of pending reviews ({dashboard['reviews']['pending']})"
        )

    if dashboard["reviews"]["requires_changes"] > 0:
        report_lines.append(
            f"\n- ⚠️ {dashboard['reviews']['requires_changes']} reviews require changes"
        )

    report = "\n".join(report_lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        logger.info(f"Compliance report saved to {output_path}")

    return report


def generate_integration_topology_diagram(governance: GovernanceManager) -> str:
    """
    Generate ASCII diagram of integration topology.

    Args:
        governance: GovernanceManager instance

    Returns:
        ASCII diagram as string

    Example:
        diagram = generate_integration_topology_diagram(governance)
        print(diagram)
    """
    topology = governance.domain_registry.get_ecosystem_topology()

    lines = [
        "PIPE Governance - Integration Topology",
        "=" * 50,
        f"\nTotal Integrations: {topology['total_integrations']}",
        f"Active Integrations: {topology['active_integrations']}\n",
        "\nConnection Matrix:",
        "-" * 50,
    ]

    # Create connection matrix
    for source, targets in topology["connection_matrix"].items():
        if targets:
            for target in targets:
                lines.append(f"  {source:10} → {target}")
        else:
            lines.append(f"  {source:10} → (no connections)")

    lines.extend(["\nDomains:", "-" * 50])

    # List domains
    for domain_code, domain_info in topology["domains"].items():
        lines.append(
            f"  {domain_code:10} | {domain_info['status']:10} | "
            f"{domain_info['connections']} connections"
        )

    return "\n".join(lines)


def validate_integration_readiness(
    governance: GovernanceManager, source_domain: str, target_domain: str
) -> Dict[str, Any]:
    """
    Validate if an integration can be created between domains.

    Args:
        governance: GovernanceManager instance
        source_domain: Source domain code
        target_domain: Target domain code

    Returns:
        Validation result with checks and recommendations

    Example:
        result = validate_integration_readiness(governance, "BNI", "BNP")
        if result["ready"]:
            print("Integration can proceed")
        else:
            print(f"Issues: {result['issues']}")
    """
    result = {
        "ready": True,
        "source_domain": source_domain,
        "target_domain": target_domain,
        "checks": {},
        "issues": [],
        "warnings": [],
    }

    # Check 1: Source domain exists
    source_info = governance.domain_registry.get_domain_info(source_domain)
    result["checks"]["source_exists"] = source_info is not None
    if not source_info:
        result["ready"] = False
        result["issues"].append(f"Source domain '{source_domain}' not registered")

    # Check 2: Target domain exists
    target_info = governance.domain_registry.get_domain_info(target_domain)
    result["checks"]["target_exists"] = target_info is not None
    if not target_info:
        result["ready"] = False
        result["issues"].append(f"Target domain '{target_domain}' not registered")

    # Check 3: Valid integration path
    if source_info and target_info:
        path_validation = governance.domain_registry.validate_integration_path(
            source_domain, target_domain
        )
        result["checks"]["valid_path"] = path_validation["valid"]
        result["checks"]["path_type"] = path_validation.get("path_type")
        result["checks"]["hops"] = path_validation.get("hops")

        if not path_validation["valid"]:
            result["ready"] = False
            result["issues"].append(
                f"Invalid integration path: {path_validation['reason']}"
            )

    # Check 4: No existing integration
    existing_integrations = governance.domain_registry.list_integrations(
        domain_code=source_domain
    )
    for integration in existing_integrations:
        if (
            integration["source"] == source_domain
            and integration["target"] == target_domain
        ):
            status = integration["status"].value
            result["warnings"].append(
                f"Integration already exists: {integration['id']} (status: {status})"
            )

    # Check 5: Source domain compliance
    if source_info:
        source_compliance = governance.compliance_tracker.get_domain_compliance_summary(
            source_domain
        )
        result["checks"]["source_compliance"] = source_compliance[
            "compliance_percentage"
        ]
        if source_compliance["compliance_percentage"] < 50:
            pct = source_compliance["compliance_percentage"]
            result["warnings"].append(f"Source domain compliance is low: {pct:.1f}%")

    # Check 6: Target domain compliance
    if target_info:
        target_compliance = governance.compliance_tracker.get_domain_compliance_summary(
            target_domain
        )
        result["checks"]["target_compliance"] = target_compliance[
            "compliance_percentage"
        ]
        if target_compliance["compliance_percentage"] < 50:
            pct = target_compliance["compliance_percentage"]
            result["warnings"].append(f"Target domain compliance is low: {pct:.1f}%")

    return result


def get_integration_health_status(governance: GovernanceManager) -> Dict[str, Any]:
    """
    Get overall health status of all integrations.

    Args:
        governance: GovernanceManager instance

    Returns:
        Health status with metrics and degraded integrations

    Example:
        health = get_integration_health_status(governance)
        print(f"Health Score: {health['health_score']}/100")
    """
    integrations = governance.domain_registry.list_integrations()
    reviews = list(governance.review_pipeline.reviews.values())

    status_counts = {"connected": 0, "pending": 0, "degraded": 0, "disconnected": 0}

    degraded_integrations = []

    for integration in integrations:
        status = integration["status"].value
        status_counts[status] = status_counts.get(status, 0) + 1

        if status == "degraded":
            degraded_integrations.append(
                {
                    "id": integration["id"],
                    "source": integration["source"],
                    "target": integration["target"],
                    "type": integration["type"],
                }
            )

    # Calculate health score (0-100)
    total = len(integrations)
    if total == 0:
        health_score = 100
    else:
        health_score = (
            status_counts["connected"] * 100 + status_counts["pending"] * 50
        ) / total

    # Get review backlog
    pending_reviews = len([r for r in reviews if r["status"] == ReviewStatus.PENDING])
    in_review = len([r for r in reviews if r["status"] == ReviewStatus.IN_REVIEW])

    return {
        "health_score": round(health_score, 1),
        "total_integrations": total,
        "status_breakdown": status_counts,
        "degraded_integrations": degraded_integrations,
        "review_backlog": {"pending": pending_reviews, "in_review": in_review},
        "health_status": (
            "healthy"
            if health_score >= 80
            else "degraded" if health_score >= 50 else "critical"
        ),
    }


def _serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert enum values and other non-serializable objects for JSON.

    Args:
        obj: Object to serialize

    Returns:
        JSON-serializable version of object
    """
    if hasattr(obj, "value"):  # Enum
        return obj.value
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj


# Quick access functions for common operations


async def quick_setup_demo_environment(governance: GovernanceManager) -> Dict[str, Any]:
    """
    Quickly set up a demo environment with sample domains and integrations.

    Args:
        governance: GovernanceManager instance

    Returns:
        Setup results

    Example:
        results = await quick_setup_demo_environment(governance)
        print(f"Created {results['domains_created']} domains")
    """
    logger.info("Setting up demo environment")

    # Define demo domains
    demo_domains = {
        "BNI": ["authentication", "user_management", "access_control"],
        "BNP": ["business_services", "data_processing", "api_gateway"],
        "AXIS": ["architecture_governance", "integration_patterns", "service_mesh"],
    }

    # Register domains
    domain_results = await batch_register_domains(governance, demo_domains)

    # Define demo integrations
    demo_integrations = [
        {
            "source": "BNI",
            "target": "BNP",
            "type": "api",
            "description": "Connect BNI authentication to BNP services",
            "priority": "high",
        },
        {
            "source": "BNP",
            "target": "AXIS",
            "type": "event",
            "description": "Event-driven architecture sync",
            "priority": "medium",
        },
    ]

    # Request integrations
    integration_results = await batch_request_integrations(
        governance, demo_integrations
    )

    return {
        "domains_created": domain_results["success_count"],
        "integrations_created": integration_results["success_count"],
        "domain_details": domain_results,
        "integration_details": integration_results,
    }
