# PIPE Governance - Quick Start Guide

Get up and running with the PIPE AgenticAI Governance System in minutes.

## What You'll Learn

- How to register domains
- How to request and approve integrations
- How to monitor compliance
- How to use the governance dashboard

## Prerequisites

- Python 3.9+
- PIPE repository cloned
- Dependencies installed: `pip install -r requirements.txt`

## 5-Minute Quick Start

### 1. Run the Interactive Demo

The fastest way to see governance in action:

```bash
python examples/governance_demo.py
```

This will demonstrate:
- Domain registration (BNI, BNP, AXIS)
- Integration request workflow
- Review and approval process
- Compliance tracking
- Governance dashboard

### 2. Try the CLI Tool

Register your first domain:

```bash
python scripts/governance_cli.py register-domain MyDomain \
  --capabilities data_processing api_gateway
```

View the governance dashboard:

```bash
python scripts/governance_cli.py dashboard
```

### 3. Request an Integration

Request an integration between two domains:

```bash
# First, ensure both domains are registered
python scripts/governance_cli.py register-domain SourceDomain
python scripts/governance_cli.py register-domain TargetDomain

# Request the integration
python scripts/governance_cli.py request-integration SourceDomain TargetDomain \
  --type api \
  --description "Connect source to target for data sync" \
  --priority high
```

This will output an integration ID like `INT-000001` and review ID like `REV-000001`.

### 4. Approve the Integration

```bash
python scripts/governance_cli.py approve INT-000001 \
  --reviewer your.name@example.com \
  --notes "Integration approved after security review"
```

### 5. Check Compliance

View ecosystem-wide compliance:

```bash
python scripts/governance_cli.py compliance
```

View compliance for a specific domain:

```bash
python scripts/governance_cli.py compliance --domain SourceDomain
```

## Common Workflows

### Workflow 1: Complete Integration Lifecycle

```bash
# Step 1: Register domains
python scripts/governance_cli.py register-domain BNI \
  --capabilities authentication user_management

python scripts/governance_cli.py register-domain BNP \
  --capabilities business_services data_processing

# Step 2: Request integration
python scripts/governance_cli.py request-integration BNI BNP \
  --type api \
  --description "Connect BNI auth to BNP services" \
  --priority high

# Output: Integration ID: INT-000001, Review ID: REV-000001

# Step 3: List pending reviews
python scripts/governance_cli.py list-reviews --status pending

# Step 4: Approve integration
python scripts/governance_cli.py approve INT-000001 \
  --reviewer security.team@example.com

# Step 5: Verify status
python scripts/governance_cli.py status BNI
python scripts/governance_cli.py list-integrations --domain BNI
```

### Workflow 2: Monitoring and Compliance

```bash
# View governance dashboard
python scripts/governance_cli.py dashboard

# Export dashboard as JSON
python scripts/governance_cli.py dashboard --json > dashboard.json

# Check domain status
python scripts/governance_cli.py status BNI
python scripts/governance_cli.py status BNP

# View compliance metrics
python scripts/governance_cli.py compliance
python scripts/governance_cli.py compliance --domain BNI --json

# List all integrations
python scripts/governance_cli.py list-integrations

# List integrations for specific domain
python scripts/governance_cli.py list-integrations --domain BNI
```

### Workflow 3: Review Management

```bash
# List all reviews
python scripts/governance_cli.py list-reviews

# List pending reviews
python scripts/governance_cli.py list-reviews --status pending

# List integration reviews
python scripts/governance_cli.py list-reviews --type integration

# List reviews for specific domain
python scripts/governance_cli.py list-reviews --domain BNI

# Export reviews as JSON
python scripts/governance_cli.py list-reviews --json > reviews.json
```

## Using the Python API

If you prefer to use Python code directly:

```python
import asyncio
from src.governance.governance_manager import GovernanceManager

async def main():
    # Initialize governance
    governance = GovernanceManager()

    # Register domain
    result = await governance.register_domain(
        "MyDomain",
        capabilities=["data_processing", "api_gateway"]
    )
    print(f"Domain registered: {result['compliance_id']}")

    # Request integration
    result = await governance.request_integration(
        source_domain="MyDomain",
        target_domain="PIPE",
        integration_type="api",
        description="Connect to PIPE hub",
        priority="high"
    )
    print(f"Integration ID: {result['integration_id']}")
    print(f"Review ID: {result['review_id']}")

    # Approve integration
    result = await governance.approve_integration(
        integration_id=result['integration_id'],
        reviewer="admin@example.com",
        notes="Approved"
    )
    print(f"Status: {result['status']}")

    # View dashboard
    dashboard = governance.get_governance_dashboard()
    print(f"Total domains: {dashboard['ecosystem']['total_domains']}")
    print(f"Total integrations: {dashboard['ecosystem']['total_integrations']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Running Tests

Verify the governance system with integration tests:

```bash
# Run all governance tests
pytest tests/integration/test_governance_workflow.py -v

# Run specific test
pytest tests/integration/test_governance_workflow.py::test_domain_registration_flow -v

# Run with coverage
pytest tests/integration/test_governance_workflow.py --cov=src.governance
```

## Understanding the Output

### Domain Registration

```
✓ Domain BNI registered successfully
ℹ   Compliance ID: domain_BNI_BNI
ℹ   Status: registered
ℹ   Capabilities: authentication, user_management
```

### Integration Request

```
✓ Integration request created
ℹ   Integration ID: INT-000001
ℹ   Review ID: REV-000001
ℹ   Status: pending_review
ℹ   Compliance ID: integration_INT-000001_PIPE
```

### Dashboard

```
Ecosystem Overview:
  Total Domains: 3
  Active Domains: 3
  Total Integrations: 2
  Active Integrations: 1

Compliance Metrics:
  Ecosystem Compliance: 33.3%
  Total Entities: 6

  By Domain:
    BNI: 33.3% (1/3 compliant)
    BNP: 33.3% (1/3 compliant)
    PIPE: 33.3% (1/3 compliant)

Review Statistics:
  Total Reviews: 2
  Pending: 1
  In Review: 0
  Approved: 1
```

## Supported Domains

The PIPE governance system supports these predefined domains:

- **BNI** - Business Network Infrastructure
- **BNP** - Business Network Platform
- **AXIS** - Architecture eXchange Integration System
- **IV** - Innovation Ventures
- **EcoX** - Ecosystem Exchange
- **THRIVE** - Technology Hub for Research & Innovation Ventures Ecosystem
- **DC** - Disconnect Collective
- **BU** - Business Unit
- **PIPE** - Platform Interface for Pipeline & Environment (hub)

You can also register custom domains with any code.

## CLI Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `register-domain` | Register a new domain | `governance_cli.py register-domain BNI --capabilities auth` |
| `request-integration` | Request integration | `governance_cli.py request-integration BNI BNP --type api` |
| `approve` | Approve integration | `governance_cli.py approve INT-000001` |
| `dashboard` | View dashboard | `governance_cli.py dashboard` |
| `compliance` | View compliance | `governance_cli.py compliance --domain BNI` |
| `status` | View domain status | `governance_cli.py status BNI` |
| `list-reviews` | List reviews | `governance_cli.py list-reviews --status pending` |
| `list-integrations` | List integrations | `governance_cli.py list-integrations --domain BNI` |
| `list-domains` | List domains | `governance_cli.py list-domains` |

## Next Steps

1. **Read the Full Documentation**: See [GOVERNANCE.md](GOVERNANCE.md) for complete architecture details
2. **Explore the Code**: Check out `src/governance/` for implementation details
3. **Customize**: Modify compliance requirements in `compliance_tracker.py`
4. **Integrate**: Add governance to your bots using `IntegrationHubBot`
5. **Extend**: Create custom review types and compliance categories

## Troubleshooting

### Issue: "Domain not found"

**Solution**: Register the domain first:
```bash
python scripts/governance_cli.py register-domain YourDomain
```

### Issue: "Invalid integration path"

**Solution**: Check that both domains are registered:
```bash
python scripts/governance_cli.py list-domains
```

### Issue: Integration request fails

**Solution**: Ensure both source and target domains exist. PIPE acts as the hub, so direct domain-to-domain connections (not through PIPE) may not be allowed depending on configuration.

### Issue: Compliance shows 0%

**Solution**: Compliance tracking requires explicit updates. Use the Python API to update compliance criteria:

```python
governance.compliance_tracker.update_compliance(
    record_id="domain_BNI_BNI",
    requirement_id="cross_domain_review",
    criteria_met=["review_completed", "approval_obtained"],
    notes="Initial setup"
)
```

## Getting Help

- **Documentation**: `docs/GOVERNANCE.md`
- **Examples**: `examples/governance_demo.py`
- **Tests**: `tests/integration/test_governance_workflow.py`
- **CLI Help**: `python scripts/governance_cli.py --help`
- **Command Help**: `python scripts/governance_cli.py <command> --help`

## Examples Directory

The `examples/` directory contains ready-to-run demonstrations:

- `governance_demo.py` - Full governance workflow demonstration
- More examples coming soon...

## Tips and Best Practices

1. **Always Register Domains First**: Before requesting integrations, ensure both domains are registered
2. **Use Descriptive Capabilities**: When registering domains, provide meaningful capability names
3. **Set Appropriate Priorities**: Use priority levels to manage review workflows effectively
4. **Monitor Compliance Regularly**: Check compliance metrics to ensure governance standards are met
5. **Export Data as JSON**: Use `--json` flag to export data for external processing
6. **Review Before Approving**: List pending reviews regularly and process them promptly
7. **Use Hub-and-Spoke Model**: Route integrations through PIPE for better governance
8. **Track Review IDs**: Keep track of review IDs for audit trails

---

**Ready to dive deeper?** Check out the [full governance documentation](GOVERNANCE.md) for advanced topics including custom compliance requirements, integration patterns, and API reference.
