"""Integration tests for PIPE governance workflow.

Tests the complete governance flow from domain registration through
integration approval and message routing.
"""

import pytest
from src.governance.governance_manager import GovernanceManager
from src.governance.domain_registry import IntegrationStatus
from src.governance.compliance_tracker import ComplianceLevel
from src.governance.review_pipeline import ReviewStatus


@pytest.mark.asyncio
async def test_domain_registration_flow():
    """Test complete domain registration workflow."""
    governance = GovernanceManager()

    # Register a domain
    result = await governance.register_domain(
        domain_code="BNI", capabilities=["authentication", "user_management"]
    )

    assert result["success"] is True
    assert result["domain_code"] == "BNI"
    assert "compliance_id" in result

    # Verify domain is registered
    domain_info = governance.domain_registry.get_domain_info("BNI")
    assert domain_info is not None
    assert domain_info["status"].value == "active"
    assert "authentication" in domain_info["capabilities"]


@pytest.mark.asyncio
async def test_integration_request_workflow():
    """Test integration request and approval workflow."""
    governance = GovernanceManager()

    # Register two domains
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    # Request integration
    result = await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Connect BNI auth to BNP services",
        priority="high",
    )

    assert result["success"] is True
    assert "integration_id" in result
    assert "review_id" in result
    assert result["status"] == "pending_review"

    integration_id = result["integration_id"]
    review_id = result["review_id"]

    # Verify review was created
    review = governance.review_pipeline.get_review(review_id)
    assert review is not None
    assert review["status"] == ReviewStatus.PENDING

    # Assign reviewers
    success = governance.review_pipeline.assign_reviewers(
        review_id, ["reviewer1@example.com", "reviewer2@example.com"]
    )
    assert success is True

    # Approve review
    success = governance.review_pipeline.approve_review(
        review_id, "reviewer1@example.com", "Looks good"
    )
    assert success is True

    success = governance.review_pipeline.approve_review(
        review_id, "reviewer2@example.com", "Approved"
    )
    assert success is True

    # Verify review is approved
    review = governance.review_pipeline.get_review(review_id)
    assert review["status"] == ReviewStatus.APPROVED

    # Approve integration
    approval_result = await governance.approve_integration(
        integration_id, "admin@example.com", "Integration approved"
    )

    assert approval_result["success"] is True
    assert approval_result["status"] == "approved"

    # Verify integration status
    integration = governance.domain_registry.get_integration(integration_id)
    assert integration["status"] == IntegrationStatus.CONNECTED


@pytest.mark.asyncio
async def test_compliance_tracking():
    """Test compliance tracking for domains and integrations."""
    governance = GovernanceManager()

    # Register domain
    result = await governance.register_domain("BNI", ["auth"])
    compliance_id = result["compliance_id"]

    # Get compliance status
    compliance_status = governance.compliance_tracker.get_compliance_status(compliance_id)
    assert compliance_status is not None
    assert compliance_status["overall_level"] == "not_evaluated"

    # Update compliance
    success = governance.compliance_tracker.update_compliance(
        compliance_id,
        "cross_domain_review",
        criteria_met=["review_completed", "approval_obtained", "documentation_complete"],
        notes="All review criteria met",
    )
    assert success is True

    # Verify compliance updated
    compliance_status = governance.compliance_tracker.get_compliance_status(compliance_id)
    requirements = compliance_status["requirements"]["cross_domain_review"]
    assert requirements["level"] == "compliant"
    assert requirements["criteria_met"] == 3


@pytest.mark.asyncio
async def test_integration_path_validation():
    """Test integration path validation."""
    governance = GovernanceManager()

    # Register domains (they auto-connect to PIPE hub)
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.register_domain("AXIS", ["integration"])

    # Validate hub path exists (auto-connected to PIPE)
    path = governance.domain_registry.validate_integration_path("BNI", "BNP")
    assert path["valid"] is True
    assert path["path_type"] == "hub"
    assert path["hops"] == 2
    assert path["path"] == ["BNI", "PIPE", "BNP"]

    # Add direct connection between BNI and BNP
    governance.domain_registry.register_integration("BNI", "BNP", "direct")

    # Now should prefer direct path
    path = governance.domain_registry.validate_integration_path("BNI", "BNP")
    assert path["valid"] is True
    assert path["path_type"] == "direct"
    assert path["hops"] == 1
    assert path["path"] == ["BNI", "BNP"]


@pytest.mark.asyncio
async def test_governance_dashboard():
    """Test governance dashboard generation."""
    governance = GovernanceManager()

    # Set up ecosystem
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.register_domain("AXIS", ["integration"])

    await governance.request_integration(
        "BNI", "BNP", "api", "Test integration", "medium"
    )

    # Get dashboard
    dashboard = governance.get_governance_dashboard()

    assert "ecosystem" in dashboard
    assert "compliance" in dashboard
    assert "reviews" in dashboard
    assert "domains" in dashboard

    # Verify ecosystem metrics
    assert dashboard["ecosystem"]["total_domains"] >= 3
    assert dashboard["ecosystem"]["active_domains"] >= 3

    # Verify reviews
    assert dashboard["reviews"]["total"] >= 1
    assert dashboard["reviews"]["pending"] >= 0


@pytest.mark.asyncio
async def test_domain_status_report():
    """Test domain status reporting."""
    governance = GovernanceManager()

    # Register domain and integrations
    await governance.register_domain("BNI", ["auth", "users"])
    await governance.register_domain("BNP", ["services"])
    await governance.request_integration("BNI", "BNP", "api", "Test", "medium")

    # Get domain status
    status = governance.get_domain_status("BNI")

    assert status is not None
    assert status["domain"]["code"] == "BNI"
    assert status["domain"]["status"] == "active"
    assert "auth" in status["domain"]["capabilities"]
    assert "connectivity" in status
    assert "compliance" in status
    assert "reviews" in status


@pytest.mark.asyncio
async def test_review_pipeline_states():
    """Test review pipeline state transitions."""
    governance = GovernanceManager()

    # Register domains
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    # Request integration
    result = await governance.request_integration(
        "BNI", "BNP", "api", "Test integration", "high"
    )
    review_id = result["review_id"]

    # Test: Pending → In Review
    governance.review_pipeline.assign_reviewers(review_id, ["reviewer@example.com"])
    review = governance.review_pipeline.get_review(review_id)
    assert review["status"] == ReviewStatus.IN_REVIEW

    # Test: Add comment
    success = governance.review_pipeline.add_comment(
        review_id, "reviewer@example.com", "Needs security review"
    )
    assert success is True

    # Test: Request changes
    success = governance.review_pipeline.request_changes(
        review_id, "reviewer@example.com", ["Add security documentation", "Update API specs"]
    )
    assert success is True
    review = governance.review_pipeline.get_review(review_id)
    assert review["status"] == ReviewStatus.REQUIRES_CHANGES

    # Test: Rejection flow
    success = governance.review_pipeline.reject_review(
        review_id, "reviewer@example.com", "Security concerns not addressed"
    )
    assert success is True
    review = governance.review_pipeline.get_review(review_id)
    assert review["status"] == ReviewStatus.REJECTED


@pytest.mark.asyncio
async def test_ecosystem_compliance_metrics():
    """Test ecosystem-wide compliance metrics."""
    governance = GovernanceManager()

    # Register multiple domains
    domains = ["BNI", "BNP", "AXIS", "IV"]
    for domain in domains:
        await governance.register_domain(domain, ["capability1"])

    # Get ecosystem compliance
    ecosystem_compliance = governance.compliance_tracker.get_ecosystem_compliance()

    assert ecosystem_compliance["total_entities"] >= len(domains)
    assert "ecosystem_compliance_percentage" in ecosystem_compliance
    assert "domains" in ecosystem_compliance


@pytest.mark.asyncio
async def test_multi_domain_integration_flow():
    """Test complete multi-domain integration scenario."""
    governance = GovernanceManager()

    # Set up 4-domain ecosystem
    domains = {
        "BNI": ["auth", "users"],
        "BNP": ["services", "data"],
        "AXIS": ["integration", "routing"],
        "IV": ["innovation", "research"],
    }

    for code, capabilities in domains.items():
        result = await governance.register_domain(code, capabilities)
        assert result["success"] is True

    # Create multiple integrations
    integrations = [
        ("BNI", "BNP", "api", "Auth to Services"),
        ("BNP", "AXIS", "event", "Services to Integration"),
        ("AXIS", "IV", "data", "Integration to Innovation"),
    ]

    for source, target, itype, desc in integrations:
        result = await governance.request_integration(source, target, itype, desc, "medium")
        assert result["success"] is True

        # Approve each integration
        review_id = result["review_id"]
        governance.review_pipeline.assign_reviewers(review_id, ["approver@example.com"])
        governance.review_pipeline.approve_review(review_id, "approver@example.com")

        integration_id = result["integration_id"]
        await governance.approve_integration(integration_id, "admin@example.com")

    # Verify ecosystem state
    dashboard = governance.get_governance_dashboard()
    assert dashboard["ecosystem"]["active_domains"] == 5  # 4 + PIPE
    assert dashboard["reviews"]["total"] >= 3
