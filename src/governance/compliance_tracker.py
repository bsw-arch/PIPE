"""Compliance tracking for PIPE AgenticAI governance.

Tracks compliance with governance standards, quality metrics,
and cross-domain integration requirements.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ComplianceLevel(Enum):
    """Compliance status levels."""

    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_EVALUATED = "not_evaluated"


class ComplianceCategory(Enum):
    """Categories of compliance requirements."""

    INTEGRATION_STANDARDS = "integration_standards"
    QUALITY_METRICS = "quality_metrics"
    SECURITY_POLICY = "security_policy"
    DATA_GOVERNANCE = "data_governance"
    REVIEW_PROCESS = "review_process"


class ComplianceTracker:
    """
    Tracks compliance with governance standards and requirements.

    Implements compliance monitoring as part of the PIPE AgenticAI
    Governance Architecture.
    """

    def __init__(self):
        """Initialize the compliance tracker."""
        self.logger = logging.getLogger("pipe.governance.compliance")
        self.compliance_records: Dict[str, Dict[str, Any]] = {}
        self.requirements: Dict[str, Dict[str, Any]] = {}
        self.evaluations: List[Dict[str, Any]] = []

        # Initialize standard requirements
        self._initialize_requirements()

    def _initialize_requirements(self) -> None:
        """Initialize standard governance requirements."""
        self.requirements = {
            "cross_domain_review": {
                "category": ComplianceCategory.REVIEW_PROCESS,
                "description": "All cross-domain integrations must undergo review",
                "mandatory": True,
                "criteria": [
                    "review_completed",
                    "approval_obtained",
                    "documentation_complete",
                ],
            },
            "quality_metrics": {
                "category": ComplianceCategory.QUALITY_METRICS,
                "description": "Quality metrics must be collected and reported",
                "mandatory": True,
                "criteria": [
                    "metrics_defined",
                    "metrics_collected",
                    "metrics_reported",
                ],
            },
            "security_validation": {
                "category": ComplianceCategory.SECURITY_POLICY,
                "description": "Security validation required for integrations",
                "mandatory": True,
                "criteria": [
                    "security_reviewed",
                    "vulnerabilities_assessed",
                    "policies_enforced",
                ],
            },
            "integration_standards": {
                "category": ComplianceCategory.INTEGRATION_STANDARDS,
                "description": "Integration must follow standard patterns",
                "mandatory": True,
                "criteria": [
                    "pattern_documented",
                    "api_standards_met",
                    "testing_complete",
                ],
            },
            "data_governance": {
                "category": ComplianceCategory.DATA_GOVERNANCE,
                "description": "Data handling must comply with governance policies",
                "mandatory": True,
                "criteria": [
                    "data_classified",
                    "retention_defined",
                    "privacy_compliant",
                ],
            },
        }

        self.logger.info(
            f"Initialized {len(self.requirements)} compliance requirements"
        )

    def create_compliance_record(
        self, entity_id: str, entity_type: str, domain: str
    ) -> str:
        """
        Create a new compliance record for an entity.

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (bot, integration, domain)
            domain: Domain the entity belongs to

        Returns:
            Compliance record ID
        """
        record_id = f"{entity_type}_{entity_id}_{domain}"

        self.compliance_records[record_id] = {
            "id": record_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "last_evaluated": None,
            "overall_level": ComplianceLevel.NOT_EVALUATED,
            "requirements": {
                req_id: {
                    "level": ComplianceLevel.NOT_EVALUATED,
                    "criteria_met": [],
                    "criteria_pending": req["criteria"].copy(),
                    "notes": [],
                }
                for req_id, req in self.requirements.items()
            },
        }

        self.logger.info(f"Created compliance record: {record_id}")
        return record_id

    def update_compliance(
        self,
        record_id: str,
        requirement_id: str,
        criteria_met: List[str],
        notes: str = None,
    ) -> bool:
        """
        Update compliance status for a specific requirement.

        Args:
            record_id: Compliance record identifier
            requirement_id: Requirement being evaluated
            criteria_met: List of criteria that have been met
            notes: Optional notes about compliance status

        Returns:
            True if update successful
        """
        if record_id not in self.compliance_records:
            self.logger.error(f"Compliance record not found: {record_id}")
            return False

        if requirement_id not in self.requirements:
            self.logger.error(f"Unknown requirement: {requirement_id}")
            return False

        record = self.compliance_records[record_id]
        requirement = record["requirements"][requirement_id]

        # Update criteria
        requirement["criteria_met"] = criteria_met
        requirement["criteria_pending"] = [
            c
            for c in self.requirements[requirement_id]["criteria"]
            if c not in criteria_met
        ]

        if notes:
            requirement["notes"].append(
                {"timestamp": datetime.now().isoformat(), "note": notes}
            )

        # Determine compliance level
        total_criteria = len(self.requirements[requirement_id]["criteria"])
        met_criteria = len(criteria_met)

        if met_criteria == total_criteria:
            requirement["level"] = ComplianceLevel.COMPLIANT
        elif met_criteria > 0:
            requirement["level"] = ComplianceLevel.PARTIAL
        else:
            requirement["level"] = ComplianceLevel.NON_COMPLIANT

        # Update overall compliance
        record["last_evaluated"] = datetime.now().isoformat()
        self._calculate_overall_compliance(record_id)

        self.logger.info(
            f"Updated compliance for {record_id}/{requirement_id}: {requirement['level'].value}"
        )
        return True

    def _calculate_overall_compliance(self, record_id: str) -> None:
        """Calculate overall compliance level for a record."""
        record = self.compliance_records[record_id]

        # Check mandatory requirements
        mandatory_reqs = [
            (req_id, req)
            for req_id, req in self.requirements.items()
            if req["mandatory"]
        ]

        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0

        for req_id, _ in mandatory_reqs:
            level = record["requirements"][req_id]["level"]
            if level == ComplianceLevel.COMPLIANT:
                compliant_count += 1
            elif level == ComplianceLevel.PARTIAL:
                partial_count += 1
            elif level == ComplianceLevel.NON_COMPLIANT:
                non_compliant_count += 1

        # Determine overall level
        if non_compliant_count > 0:
            record["overall_level"] = ComplianceLevel.NON_COMPLIANT
        elif partial_count > 0:
            record["overall_level"] = ComplianceLevel.PARTIAL
        elif compliant_count == len(mandatory_reqs):
            record["overall_level"] = ComplianceLevel.COMPLIANT
        else:
            record["overall_level"] = ComplianceLevel.NOT_EVALUATED

    def get_compliance_status(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current compliance status for a record.

        Args:
            record_id: Compliance record identifier

        Returns:
            Compliance status dictionary
        """
        if record_id not in self.compliance_records:
            return None

        record = self.compliance_records[record_id]

        return {
            "id": record_id,
            "entity": {
                "id": record["entity_id"],
                "type": record["entity_type"],
                "domain": record["domain"],
            },
            "overall_level": record["overall_level"].value,
            "last_evaluated": record["last_evaluated"],
            "requirements": {
                req_id: {
                    "level": req["level"].value,
                    "criteria_met": len(req["criteria_met"]),
                    "criteria_total": len(self.requirements[req_id]["criteria"]),
                    "criteria_pending": req["criteria_pending"],
                }
                for req_id, req in record["requirements"].items()
            },
        }

    def get_domain_compliance_summary(self, domain: str) -> Dict[str, Any]:
        """
        Get compliance summary for all entities in a domain.

        Args:
            domain: Domain code

        Returns:
            Summary of domain compliance
        """
        domain_records = [
            r for r in self.compliance_records.values() if r["domain"] == domain
        ]

        if not domain_records:
            return {
                "domain": domain,
                "total_entities": 0,
                "compliance_summary": {},
            }

        compliance_counts = {
            ComplianceLevel.COMPLIANT: 0,
            ComplianceLevel.PARTIAL: 0,
            ComplianceLevel.NON_COMPLIANT: 0,
            ComplianceLevel.NOT_EVALUATED: 0,
        }

        for record in domain_records:
            compliance_counts[record["overall_level"]] += 1

        total = len(domain_records)
        compliance_percentage = (
            (compliance_counts[ComplianceLevel.COMPLIANT] / total * 100)
            if total > 0
            else 0
        )

        return {
            "domain": domain,
            "total_entities": total,
            "compliance_percentage": round(compliance_percentage, 2),
            "compliance_summary": {
                "compliant": compliance_counts[ComplianceLevel.COMPLIANT],
                "partial": compliance_counts[ComplianceLevel.PARTIAL],
                "non_compliant": compliance_counts[ComplianceLevel.NON_COMPLIANT],
                "not_evaluated": compliance_counts[ComplianceLevel.NOT_EVALUATED],
            },
        }

    def get_ecosystem_compliance(self) -> Dict[str, Any]:
        """
        Get ecosystem-wide compliance metrics.

        Returns:
            Ecosystem compliance summary
        """
        domains = set(r["domain"] for r in self.compliance_records.values())
        domain_summaries = {
            domain: self.get_domain_compliance_summary(domain) for domain in domains
        }

        total_entities = sum(s["total_entities"] for s in domain_summaries.values())
        total_compliant = sum(
            s["compliance_summary"]["compliant"] for s in domain_summaries.values()
        )

        ecosystem_compliance = (
            (total_compliant / total_entities * 100) if total_entities > 0 else 0
        )

        return {
            "total_entities": total_entities,
            "ecosystem_compliance_percentage": round(ecosystem_compliance, 2),
            "domains": domain_summaries,
            "timestamp": datetime.now().isoformat(),
        }
