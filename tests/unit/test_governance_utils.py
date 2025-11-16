"""Unit tests for governance utilities."""

import pytest
import json
from pathlib import Path
from src.governance.utils import (
    batch_register_domains,
    batch_request_integrations,
    export_governance_state,
    generate_compliance_report,
    generate_integration_topology_diagram,
    validate_integration_readiness,
    get_integration_health_status,
    quick_setup_demo_environment,
    _serialize_for_json,
)
from src.governance.governance_manager import GovernanceManager
from src.governance.review_pipeline import ReviewStatus
from enum import Enum


class SerializationTestEnum(Enum):
    """Test enum for serialization tests."""

    VALUE_ONE = "one"
    VALUE_TWO = "two"


@pytest.mark.asyncio
async def test_batch_register_domains_success():
    """Test successful batch domain registration."""
    governance = GovernanceManager()

    domains_config = {
        "BNI": ["authentication", "user_management"],
        "BNP": ["business_services", "data_processing"],
        "AXIS": ["architecture", "compliance"],
    }

    results = await batch_register_domains(governance, domains_config)

    assert results["success_count"] == 3
    assert results["failure_count"] == 0
    assert results["total"] == 3
    assert len(results["successful"]) == 3
    assert "BNI" in results["successful"]
    assert "BNP" in results["successful"]
    assert "AXIS" in results["successful"]


@pytest.mark.asyncio
async def test_batch_register_domains_all_succeed():
    """Test batch registration where all succeed."""
    governance = GovernanceManager()

    # Register BNI first
    await governance.register_domain("BNI", ["auth"])

    # Register more domains (all should succeed)
    domains_config = {
        "BNP": ["business_services"],  # New
        "AXIS": ["compliance"],  # New
    }

    results = await batch_register_domains(governance, domains_config)

    # Both should succeed
    assert results["success_count"] == 2
    assert results["failure_count"] == 0
    assert "BNP" in results["successful"]
    assert "AXIS" in results["successful"]


@pytest.mark.asyncio
async def test_batch_register_domains_empty():
    """Test batch registration with empty config."""
    governance = GovernanceManager()

    results = await batch_register_domains(governance, {})

    assert results["success_count"] == 0
    assert results["failure_count"] == 0
    assert results["total"] == 0


@pytest.mark.asyncio
async def test_batch_request_integrations_success():
    """Test successful batch integration requests."""
    governance = GovernanceManager()

    # Setup domains first
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.register_domain("AXIS", ["compliance"])

    integrations = [
        {
            "source": "BNI",
            "target": "BNP",
            "type": "api",
            "description": "Auth to services",
            "priority": "high",
        },
        {
            "source": "BNP",
            "target": "AXIS",
            "type": "event",
            "description": "Event sync",
            "priority": "medium",
        },
    ]

    results = await batch_request_integrations(governance, integrations)

    assert results["success_count"] == 2
    assert results["failure_count"] == 0
    assert results["total"] == 2
    assert len(results["successful"]) == 2


@pytest.mark.asyncio
async def test_batch_request_integrations_with_failures():
    """Test batch integration requests with failures."""
    governance = GovernanceManager()

    # Only register one domain
    await governance.register_domain("BNI", ["auth"])

    integrations = [
        {
            "source": "BNI",
            "target": "NONEXISTENT",  # Doesn't exist
            "type": "api",
        }
    ]

    results = await batch_request_integrations(governance, integrations)

    # Should fail because target domain doesn't exist
    assert results["success_count"] == 0
    assert results["failure_count"] == 1


@pytest.mark.asyncio
async def test_batch_request_integrations_default_values():
    """Test batch integration requests with default values."""
    governance = GovernanceManager()

    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    # Minimal integration config (uses defaults)
    integrations = [{"source": "BNI", "target": "BNP"}]

    results = await batch_request_integrations(governance, integrations)

    assert results["success_count"] == 1
    integration_data = results["successful"][0]
    assert integration_data["source"] == "BNI"
    assert integration_data["target"] == "BNP"
    assert "integration_id" in integration_data
    assert "review_id" in integration_data


def test_export_governance_state_success(tmp_path):
    """Test successful governance state export."""
    governance = GovernanceManager()

    output_file = tmp_path / "governance_export.json"
    result = export_governance_state(governance, output_file)

    assert result["success"] is True
    assert Path(result["path"]) == output_file
    assert output_file.exists()

    # Verify file content
    with open(output_file) as f:
        data = json.load(f)

    assert "exported_at" in data
    assert "domains" in data
    assert "integrations" in data
    assert "reviews" in data
    assert "compliance_records" in data
    assert "dashboard" in data


def test_export_governance_state_creates_directories(tmp_path):
    """Test that export creates necessary directories."""
    governance = GovernanceManager()

    output_file = tmp_path / "subdir" / "nested" / "export.json"
    result = export_governance_state(governance, output_file)

    assert result["success"] is True
    assert output_file.exists()
    assert output_file.parent.exists()


@pytest.mark.asyncio
async def test_export_governance_state_with_data(tmp_path):
    """Test export with actual governance data."""
    governance = GovernanceManager()

    # Add some data
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    output_file = tmp_path / "export.json"
    result = export_governance_state(governance, output_file)

    assert result["success"] is True
    # Note: DomainRegistry may auto-activate domains during initialization
    # Just check that we have at least the 2 domains we registered
    assert result["domains"] >= 2


def test_generate_compliance_report_basic():
    """Test basic compliance report generation."""
    governance = GovernanceManager()

    report = generate_compliance_report(governance)

    assert "PIPE Governance Compliance Report" in report
    assert "Executive Summary" in report
    assert "Domain Compliance" in report
    assert "Review Statistics" in report
    assert "Recommendations" in report


def test_generate_compliance_report_save_to_file(tmp_path):
    """Test saving compliance report to file."""
    governance = GovernanceManager()

    output_file = tmp_path / "compliance_report.md"
    report = generate_compliance_report(governance, output_file)

    assert output_file.exists()
    assert "PIPE Governance Compliance Report" in report

    # Verify file content matches returned report
    with open(output_file) as f:
        file_content = f.read()

    assert file_content == report


@pytest.mark.asyncio
async def test_generate_compliance_report_with_data():
    """Test compliance report with actual governance data."""
    governance = GovernanceManager()

    # Add domains
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    report = generate_compliance_report(governance)

    assert "BNI" in report or "Total Domains: 2" in report
    assert "Total Entities:" in report


def test_generate_integration_topology_diagram_empty():
    """Test topology diagram with no integrations."""
    governance = GovernanceManager()

    diagram = generate_integration_topology_diagram(governance)

    assert "PIPE Governance - Integration Topology" in diagram
    assert "Total Integrations:" in diagram
    assert "Connection Matrix:" in diagram
    assert "Domains:" in diagram


@pytest.mark.asyncio
async def test_generate_integration_topology_diagram_with_data():
    """Test topology diagram with actual data."""
    governance = GovernanceManager()

    # Setup domains and integration
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Test integration",
    )

    diagram = generate_integration_topology_diagram(governance)

    assert "BNI" in diagram
    assert "BNP" in diagram
    assert "→" in diagram  # Connection arrow


@pytest.mark.asyncio
async def test_validate_integration_readiness_both_domains_exist():
    """Test validation when both domains exist."""
    governance = GovernanceManager()

    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    result = validate_integration_readiness(governance, "BNI", "BNP")

    assert result["ready"] is True
    assert result["checks"]["source_exists"] is True
    assert result["checks"]["target_exists"] is True
    assert result["source_domain"] == "BNI"
    assert result["target_domain"] == "BNP"


@pytest.mark.asyncio
async def test_validate_integration_readiness_source_missing():
    """Test validation when source domain doesn't exist."""
    governance = GovernanceManager()

    # Register only target
    await governance.register_domain("BNP", ["services"])

    result = validate_integration_readiness(governance, "NONEXISTENT", "BNP")

    assert result["ready"] is False
    assert result["checks"]["source_exists"] is False
    assert len(result["issues"]) > 0


@pytest.mark.asyncio
async def test_validate_integration_readiness_target_missing():
    """Test validation when target domain doesn't exist."""
    governance = GovernanceManager()

    await governance.register_domain("BNI", ["auth"])

    result = validate_integration_readiness(governance, "BNI", "NONEXISTENT")

    assert result["ready"] is False
    assert result["checks"]["target_exists"] is False
    assert len(result["issues"]) > 0


@pytest.mark.asyncio
async def test_validate_integration_readiness_existing_integration():
    """Test validation with existing integration."""
    governance = GovernanceManager()

    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])

    # Create integration
    await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Test integration",
    )

    # Validate again
    result = validate_integration_readiness(governance, "BNI", "BNP")

    # Should have warning about existing integration
    assert len(result["warnings"]) > 0
    assert "already exists" in result["warnings"][0]


def test_get_integration_health_status_empty():
    """Test health status with no integrations."""
    governance = GovernanceManager()

    health = get_integration_health_status(governance)

    assert health["health_score"] == 100  # Perfect when empty
    assert health["total_integrations"] == 0
    assert health["health_status"] == "healthy"


@pytest.mark.asyncio
async def test_get_integration_health_status_with_integrations():
    """Test health status with active integrations."""
    governance = GovernanceManager()

    # Setup
    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Test integration",
    )

    health = get_integration_health_status(governance)

    assert health["total_integrations"] >= 1
    assert "status_breakdown" in health
    assert "health_score" in health
    assert "health_status" in health


@pytest.mark.asyncio
async def test_get_integration_health_status_review_backlog():
    """Test health status includes review backlog."""
    governance = GovernanceManager()

    await governance.register_domain("BNI", ["auth"])
    await governance.register_domain("BNP", ["services"])
    await governance.request_integration(
        source_domain="BNI",
        target_domain="BNP",
        integration_type="api",
        description="Test integration",
    )

    health = get_integration_health_status(governance)

    assert "review_backlog" in health
    assert "pending" in health["review_backlog"]
    assert "in_review" in health["review_backlog"]


def test_serialize_for_json_enum():
    """Test JSON serialization of enums."""
    obj = {"status": ReviewStatus.PENDING, "name": "test"}

    result = _serialize_for_json(obj)

    assert result["status"] == "pending"
    assert result["name"] == "test"


def test_serialize_for_json_nested_dict():
    """Test JSON serialization of nested dicts."""
    obj = {
        "level1": {
            "level2": {"status": SerializationTestEnum.VALUE_ONE, "count": 5},
            "items": [SerializationTestEnum.VALUE_TWO, "string"],
        }
    }

    result = _serialize_for_json(obj)

    assert result["level1"]["level2"]["status"] == "one"
    assert result["level1"]["level2"]["count"] == 5
    assert result["level1"]["items"][0] == "two"
    assert result["level1"]["items"][1] == "string"


def test_serialize_for_json_list():
    """Test JSON serialization of lists."""
    obj = [
        SerializationTestEnum.VALUE_ONE,
        SerializationTestEnum.VALUE_TWO,
        "regular_string",
    ]

    result = _serialize_for_json(obj)

    assert result[0] == "one"
    assert result[1] == "two"
    assert result[2] == "regular_string"


def test_serialize_for_json_set():
    """Test JSON serialization of sets."""
    obj = {1, 2, 3}

    result = _serialize_for_json(obj)

    assert isinstance(result, list)
    assert set(result) == {1, 2, 3}


def test_serialize_for_json_primitives():
    """Test JSON serialization preserves primitives."""
    obj = {"string": "value", "int": 42, "float": 3.14, "bool": True, "none": None}

    result = _serialize_for_json(obj)

    assert result == obj


@pytest.mark.asyncio
async def test_quick_setup_demo_environment():
    """Test quick demo environment setup."""
    governance = GovernanceManager()

    results = await quick_setup_demo_environment(governance)

    assert results["domains_created"] == 3  # BNI, BNP, AXIS
    assert results["integrations_created"] == 2
    assert "domain_details" in results
    assert "integration_details" in results


@pytest.mark.asyncio
async def test_quick_setup_demo_environment_creates_expected_domains():
    """Test demo environment creates specific domains."""
    governance = GovernanceManager()

    results = await quick_setup_demo_environment(governance)

    # Verify domains were created (list_active_domains returns List[str])
    domain_codes = governance.domain_registry.list_active_domains()

    assert "BNI" in domain_codes
    assert "BNP" in domain_codes
    assert "AXIS" in domain_codes


@pytest.mark.asyncio
async def test_quick_setup_demo_environment_creates_integrations():
    """Test demo environment creates integrations."""
    governance = GovernanceManager()

    results = await quick_setup_demo_environment(governance)

    # Verify integrations were created
    integrations = governance.domain_registry.list_integrations()

    assert len(integrations) >= 2

    # Check for expected integration pairs
    pairs = [(i["source"], i["target"]) for i in integrations]
    assert ("BNI", "BNP") in pairs
    assert ("BNP", "AXIS") in pairs
