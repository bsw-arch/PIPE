"""PIPE DataPoint models for Cognee AI memory.

Custom DataPoint types that represent PIPE governance entities:
- Domains (9 domains in the BSW ecosystem)
- Integrations (cross-domain connections)
- Compliance Records (compliance tracking)
- Review Decisions (governance approvals)

Each DataPoint:
- Is atomic (one concept per point)
- Has index_fields for semantic search
- Creates graph relationships automatically
- Maintains provenance and versioning
"""

from typing import List, Optional
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel, Field

try:
    from cognee.infrastructure.databases.graph import DataPoint, Edge
    COGNEE_AVAILABLE = True
except ImportError:
    # Fallback if Cognee not installed
    COGNEE_AVAILABLE = False

    class DataPoint(BaseModel):
        """Fallback DataPoint when Cognee not available."""
        id: UUID = Field(default_factory=uuid4)
        created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
        updated_at: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
        version: int = 1
        topological_rank: Optional[int] = 0
        metadata: Optional[dict] = {"index_fields": []}
        type: str = "DataPoint"
        belongs_to_set: Optional[List["DataPoint"]] = None

    class Edge(BaseModel):
        """Fallback Edge when Cognee not available."""
        relationship_name: str
        source_node_id: UUID
        target_node_id: UUID
        attributes: Optional[dict] = {}


class DomainDataPoint(DataPoint):
    """
    Represents a domain in the BSW ecosystem.

    Domains: BNI, BNP, AXIS, IV, EcoX, THRIVE, DC, BU, PIPE

    Indexed fields:
    - name: For semantic search by domain name
    - capabilities: For finding domains with specific capabilities
    """

    code: str  # BNI, BNP, AXIS, IV, EcoX, THRIVE, DC, BU, PIPE
    name: str  # Full domain name
    capabilities: List[str]  # Domain capabilities
    status: str  # active, inactive, pending
    description: Optional[str] = ""

    # Index name and capabilities for semantic search
    metadata: dict = {"index_fields": ["name", "capabilities"]}


class IntegrationDataPoint(DataPoint):
    """
    Represents a cross-domain integration.

    Captures integration requests, approvals, and active connections
    between domains in the BSW ecosystem.

    Indexed fields:
    - description: Semantic search for similar integrations
    - integration_type: Find integrations by type
    """

    integration_id: str
    source_domain: str  # Domain code
    target_domain: str  # Domain code
    integration_type: str  # hub, direct, mesh
    description: str
    status: str  # pending, approved, rejected, connected, failed
    priority: str  # low, medium, high, critical
    created_timestamp: int
    approved_timestamp: Optional[int] = None
    approvers: List[str] = []

    # Index description and type for pattern matching
    metadata: dict = {"index_fields": ["description", "integration_type"]}


class ComplianceRecordDataPoint(DataPoint):
    """
    Represents a compliance check result.

    Tracks compliance across 5 categories:
    - Integration Standards
    - Quality Metrics
    - Security Policy
    - Data Governance
    - Review Process

    Indexed fields:
    - findings: Semantic search for similar compliance issues
    - category: Find issues by compliance category
    """

    record_id: str
    entity_id: str  # Domain or integration ID
    entity_type: str  # domain, integration, bot
    domain: str  # Which domain this applies to
    category: str  # Compliance category
    level: str  # compliant, partial, non_compliant, not_evaluated
    findings: str  # Detailed findings
    recommendations: Optional[str] = ""
    check_timestamp: int

    # Index findings and category for similarity search
    metadata: dict = {"index_fields": ["findings", "category"]}


class ReviewDecisionDataPoint(DataPoint):
    """
    Represents a governance review decision.

    Captures the reasoning and context behind approval/rejection
    decisions to enable learning from precedent.

    Review types:
    - Integration
    - Security
    - Quality
    - Architecture
    - Compliance

    Indexed fields:
    - rationale: Learn from decision reasoning
    - review_type: Find similar review types
    """

    review_id: str
    review_type: str  # integration, security, quality, architecture, compliance
    title: str
    decision: str  # approved, rejected, requires_changes, cancelled
    rationale: str  # Why this decision was made
    reviewer: str  # Who made the decision
    source_domain: Optional[str] = None
    target_domain: Optional[str] = None
    priority: str  # low, medium, high, critical
    created_timestamp: int
    decision_timestamp: Optional[int] = None

    # Related entities (creates graph edges)
    integration: Optional[str] = None  # Integration ID if applicable
    compliance_records: List[str] = []  # Related compliance record IDs

    # Index rationale and review type for precedent search
    metadata: dict = {"index_fields": ["rationale", "review_type"]}


class IntegrationPatternDataPoint(DataPoint):
    """
    Represents a learned integration pattern.

    Captures successful (or failed) integration patterns to enable
    AI-driven suggestions for future integrations.

    Indexed fields:
    - pattern_description: Semantic search for similar patterns
    - success_factors: Learn what makes patterns successful
    """

    pattern_id: str
    pattern_name: str
    pattern_description: str
    source_domain_type: str  # e.g., "financial", "energy", "identity"
    target_domain_type: str
    integration_type: str
    success_rate: float  # 0.0 to 1.0
    success_factors: List[str]
    failure_factors: List[str] = []
    use_cases: List[str] = []
    examples: List[str] = []  # Integration IDs that used this pattern

    # Index description and success factors
    metadata: dict = {"index_fields": ["pattern_description", "success_factors"]}


class DomainCapabilityDataPoint(DataPoint):
    """
    Represents a specific capability of a domain.

    Enables fine-grained capability matching and discovery.

    Indexed fields:
    - capability_name: Search for specific capabilities
    - description: Semantic understanding of capabilities
    """

    capability_id: str
    capability_name: str
    description: str
    domain_code: str
    category: str  # technical, business, governance
    maturity_level: str  # basic, intermediate, advanced, expert

    # Related domains that also have this capability
    similar_capabilities: List[str] = []

    # Index name and description
    metadata: dict = {"index_fields": ["capability_name", "description"]}


class GovernancePolicyDataPoint(DataPoint):
    """
    Represents a governance policy or requirement.

    Policies that guide integration approvals, compliance checks,
    and governance decisions.

    Indexed fields:
    - policy_text: Semantic search for applicable policies
    - requirements: Find policies by requirements
    """

    policy_id: str
    policy_name: str
    policy_text: str
    requirements: List[str]
    applies_to: List[str]  # Which domains/integration types
    severity: str  # mandatory, recommended, optional
    enforcement_level: str  # strict, moderate, advisory

    # Related policies
    supersedes: Optional[str] = None  # Policy ID this replaces
    related_policies: List[str] = []

    # Index policy text and requirements
    metadata: dict = {"index_fields": ["policy_text", "requirements"]}


# Helper functions to create DataPoints from existing PIPE objects

def domain_to_datapoint(domain_info: dict) -> DomainDataPoint:
    """
    Convert domain registry info to DataPoint.

    Args:
        domain_info: Domain information from DomainRegistry

    Returns:
        DomainDataPoint
    """
    return DomainDataPoint(
        code=domain_info["code"],
        name=domain_info["name"],
        capabilities=list(domain_info.get("capabilities", [])),
        status=domain_info.get("status", "active"),
        description=domain_info.get("description", ""),
    )


def integration_to_datapoint(integration: dict) -> IntegrationDataPoint:
    """
    Convert integration to DataPoint.

    Args:
        integration: Integration information

    Returns:
        IntegrationDataPoint
    """
    return IntegrationDataPoint(
        integration_id=integration["id"],
        source_domain=integration["source_domain"],
        target_domain=integration["target_domain"],
        integration_type=integration.get("integration_type", "hub"),
        description=integration.get("description", ""),
        status=integration["status"],
        priority=integration.get("priority", "medium"),
        created_timestamp=int(datetime.now().timestamp() * 1000),
        approved_timestamp=integration.get("approved_timestamp"),
        approvers=integration.get("approvers", []),
    )


def compliance_to_datapoint(compliance: dict) -> ComplianceRecordDataPoint:
    """
    Convert compliance record to DataPoint.

    Args:
        compliance: Compliance record information

    Returns:
        ComplianceRecordDataPoint
    """
    return ComplianceRecordDataPoint(
        record_id=compliance["id"],
        entity_id=compliance["entity_id"],
        entity_type=compliance["entity_type"],
        domain=compliance["domain"],
        category=compliance["category"],
        level=compliance["level"],
        findings=compliance.get("findings", ""),
        recommendations=compliance.get("recommendations", ""),
        check_timestamp=int(datetime.now().timestamp() * 1000),
    )


def review_to_datapoint(review: dict) -> ReviewDecisionDataPoint:
    """
    Convert review decision to DataPoint.

    Args:
        review: Review information

    Returns:
        ReviewDecisionDataPoint
    """
    return ReviewDecisionDataPoint(
        review_id=review["id"],
        review_type=review["review_type"],
        title=review.get("title", ""),
        decision=review["status"],
        rationale=review.get("rationale", ""),
        reviewer=review.get("reviewer", "system"),
        source_domain=review.get("source_domain"),
        target_domain=review.get("target_domain"),
        priority=review.get("priority", "medium"),
        created_timestamp=int(datetime.now().timestamp() * 1000),
        decision_timestamp=review.get("decision_timestamp"),
        integration=review.get("integration_id"),
        compliance_records=review.get("compliance_records", []),
    )
