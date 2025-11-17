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


class PRReviewDataPoint(DataPoint):
    """
    Represents a PR-QUEST code review for governance tracking.

    Captures automated and human PR reviews with LLM-powered analysis,
    risk detection, and gamification metrics. Enables learning from
    code review patterns over time.

    Indexed fields:
    - risks: Semantic search for similar PR issues
    - suggestions: Find similar fix recommendations
    - decision: Search by review outcome
    """

    # PR Metadata
    pr_url: str  # Full GitHub PR URL
    pr_number: int  # PR number
    repository: str  # owner/repo
    analysis_id: str  # PR-QUEST analysis ID

    # PR-QUEST Analysis Results
    clusters: List[dict]  # Grouped changes from LLM clustering
    risks: List[str]  # Detected issues (simplified for Cognee indexing)
    risk_level: str  # NONE, LOW, MODERATE, CRITICAL
    suggestions: List[str]  # LLM recommendations
    xp_awarded: int  # Gamification score

    # Review Decision
    decision: str  # APPROVE, REJECT, NEEDS_REVIEW
    reviewer: str  # Bot or human username
    reviewed_at: int  # Unix timestamp
    review_duration_seconds: int  # Time to complete review

    # Integration Context
    integration_id: Optional[str] = None  # Related integration request
    source_domain: Optional[str] = None  # Source domain code
    target_domain: Optional[str] = None  # Target domain code

    # Override Information
    human_override: bool = False  # Was bot decision overridden?
    override_justification: Optional[str] = None  # Why override was needed

    # LLM Information
    llm_used: bool = True  # Whether LLM analysis was used
    llm_model: Optional[str] = None  # Model used (e.g., gpt-4o-mini)

    # Semantic search on risks, suggestions, and decision
    metadata: dict = {"index_fields": ["risks", "suggestions", "decision"]}


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


def pr_review_to_datapoint(
    pr_analysis: "PRAnalysisResult",  # Forward reference to avoid circular import
    decision: str,
    reviewer: str,
    review_duration: int,
    integration_id: Optional[str] = None,
    source_domain: Optional[str] = None,
    target_domain: Optional[str] = None,
    human_override: bool = False,
    override_justification: Optional[str] = None,
) -> PRReviewDataPoint:
    """
    Convert PR-QUEST analysis result to DataPoint.

    Args:
        pr_analysis: PRAnalysisResult from PR-QUEST
        decision: Review decision (APPROVE, REJECT, NEEDS_REVIEW)
        reviewer: Bot or human reviewer name
        review_duration: Seconds taken for review
        integration_id: Optional related integration ID
        source_domain: Optional source domain code
        target_domain: Optional target domain code
        human_override: Whether decision was overridden
        override_justification: Reason for override

    Returns:
        PRReviewDataPoint for storing in Cognee
    """
    # Convert pr_analysis.pr_url to string if it's a Pydantic HttpUrl
    pr_url_str = str(pr_analysis.pr_url)

    # Simplify clusters to dicts for Cognee storage
    cluster_dicts = [
        {
            "id": cluster.id,
            "description": cluster.description,
            "files": cluster.files,
            "line_count": cluster.line_count,
            "category": cluster.category,
        }
        for cluster in pr_analysis.clusters
    ]

    # Simplify risks to strings for easier Cognee indexing
    risk_strings = [
        f"{risk.type.value}: {risk.description} (severity: {risk.severity.value})"
        for risk in pr_analysis.risks
    ]

    return PRReviewDataPoint(
        pr_url=pr_url_str,
        pr_number=pr_analysis.pr_number,
        repository=pr_analysis.repository,
        analysis_id=pr_analysis.analysis_id,
        clusters=cluster_dicts,
        risks=risk_strings,
        risk_level=pr_analysis.overall_risk_level.value,
        suggestions=pr_analysis.suggestions,
        xp_awarded=pr_analysis.xp_awarded,
        decision=decision,
        reviewer=reviewer,
        reviewed_at=pr_analysis.analyzed_at,
        review_duration_seconds=review_duration,
        integration_id=integration_id,
        source_domain=source_domain,
        target_domain=target_domain,
        human_override=human_override,
        override_justification=override_justification,
        llm_used=pr_analysis.llm_used,
        llm_model=pr_analysis.llm_model,
    )
