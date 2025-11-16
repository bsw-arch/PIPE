# PIPE Integration Patterns Guide

Complete guide to integration patterns, best practices, and real-world examples for the PIPE ecosystem.

## Table of Contents

- [Overview](#overview)
- [Integration Patterns](#integration-patterns)
- [Real-World Examples](#real-world-examples)
- [Best Practices](#best-practices)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)

---

## Overview

The PIPE ecosystem supports cross-domain integration through a hub-and-spoke architecture with enterprise governance. This guide provides patterns and examples for common integration scenarios.

### Core Principles

1. **Hub-and-Spoke**: All domains connect through PIPE hub
2. **Event-Driven**: Asynchronous communication via event bus
3. **Governance-First**: All integrations require governance approval
4. **Compliance-Tracked**: Automatic compliance monitoring
5. **Loosely Coupled**: Domains remain independent

---

## Integration Patterns

### Pattern 1: Request-Response

**Use Case**: Synchronous-style service calls across domains

**Flow**:
1. Source domain publishes request event
2. Target domain processes request
3. Target domain publishes response event
4. Source domain receives response

**Example**:
```python
# Source domain (IV) requests analytics from BNP
await event_bus.publish(
    Event(
        event_type="service.request",
        source="IV",
        data={
            "service": "analytics",
            "request_id": "REQ-001",
            "parameters": {"period": "quarterly"}
        }
    )
)

# BNP responds with analytics data
await event_bus.publish(
    Event(
        event_type="service.response",
        source="BNP",
        data={
            "request_id": "REQ-001",
            "status": "success",
            "data": analytics_data
        }
    )
)
```

**When to Use**:
- Service consumption (APIs, data requests)
- Immediate response needed
- Simple request/response workflows

---

### Pattern 2: Publish-Subscribe

**Use Case**: Broadcasting events to multiple subscribers

**Flow**:
1. Publisher domain emits event
2. Multiple subscriber domains receive event
3. Each subscriber processes independently
4. No response expected

**Example**:
```python
# BNI publishes user authentication event
await event_bus.publish(
    Event(
        event_type="user.authenticated",
        source="BNI",
        data={
            "username": "user@domain.com",
            "token": "token_xyz",
            "permissions": ["read", "write"]
        }
    )
)

# Multiple domains subscribe
event_bus.subscribe("user.authenticated", bnp_handler)
event_bus.subscribe("user.authenticated", axis_handler)
event_bus.subscribe("user.authenticated", iv_handler)
```

**When to Use**:
- Notifications and alerts
- State change broadcasts
- Multi-domain coordination
- Audit logging

---

### Pattern 3: Workflow Orchestration

**Use Case**: Multi-step processes spanning multiple domains

**Flow**:
1. Orchestrator initiates workflow
2. Each step involves different domain
3. Progress tracked through workflow state
4. Each step completion triggers next step

**Example**:
```python
# Innovation project approval workflow
# Step 1: BNI authentication
# Step 2: IV project creation
# Step 3: BNP budget check
# Step 4: AXIS architecture validation
# Step 5: BNP resource allocation
# Step 6: Final approval

# See examples/workflow_multi_domain.py for complete implementation
```

**When to Use**:
- Complex business processes
- Multi-domain approvals
- Long-running workflows
- State tracking required

---

### Pattern 4: Data Synchronization

**Use Case**: Keeping data consistent across domains

**Flow**:
1. Source domain detects data change
2. Publishes change event
3. Target domains receive and apply changes
4. Acknowledge successful sync

**Example**:
```python
# BNP customer data updated
await event_bus.publish(
    Event(
        event_type="data.updated",
        source="BNP",
        data={
            "entity_type": "customer",
            "entity_id": "CUST-12345",
            "changes": {
                "tier": "Enterprise",
                "health_score": 85
            }
        }
    )
)

# Other domains sync their copies
async def sync_customer_data(event):
    entity_id = event.data["entity_id"]
    changes = event.data["changes"]
    # Apply changes locally
    await update_local_copy(entity_id, changes)
```

**When to Use**:
- Shared data entities
- Real-time data consistency
- Event sourcing patterns
- Cache invalidation

---

### Pattern 5: Aggregation

**Use Case**: Combining data from multiple domains

**Flow**:
1. Requester sends requests to multiple domains
2. Collects responses asynchronously
3. Aggregates results
4. Returns combined data

**Example**:
```python
# Aggregate customer 360 view
async def get_customer_360(customer_id):
    # Request data from multiple domains
    responses = await asyncio.gather(
        request_crm_data("BNP", customer_id),
        request_transactions("BNP", customer_id),
        request_support_tickets("AXIS", customer_id),
        request_innovation_projects("IV", customer_id)
    )

    # Combine results
    return {
        "crm": responses[0],
        "transactions": responses[1],
        "support": responses[2],
        "innovation": responses[3]
    }
```

**When to Use**:
- Dashboard aggregation
- Reporting and analytics
- Search across domains
- Unified views

---

## Real-World Examples

### Example 1: Single Sign-On (SSO)

**Scenario**: User authenticates once via BNI, uses credentials across all domains

**Domains Involved**: BNI (Auth), BNP, AXIS, IV

**Implementation**:
```bash
# Run the example
python examples/integration_bni_auth.py
```

**Key Features**:
- Centralized authentication
- Token-based access
- Permission management
- Automatic session expiry

**See**: `examples/integration_bni_auth.py`

---

### Example 2: Business Service Integration

**Scenario**: Domains consume business services (CRM, analytics, invoicing) from BNP

**Domains Involved**: BNP (Provider), IV, AXIS (Consumers)

**Implementation**:
```bash
# Run the example
python examples/integration_bnp_services.py
```

**Key Features**:
- Multiple service types
- Request/response pattern
- Data export capabilities
- Service metrics tracking

**See**: `examples/integration_bnp_services.py`

---

### Example 3: Innovation Project Workflow

**Scenario**: Complete project approval workflow across 4 domains

**Domains Involved**: BNI → IV → BNP → AXIS

**Implementation**:
```bash
# Run the example
python examples/workflow_multi_domain.py
```

**Key Features**:
- 6-step workflow
- Multi-domain collaboration
- Budget and compliance checks
- Complete audit trail

**See**: `examples/workflow_multi_domain.py`

---

## Best Practices

### 1. Event Naming Conventions

Use a consistent naming pattern:

```
<domain>.<entity>.<action>

Examples:
- user.authentication.request
- service.analytics.response
- data.customer.updated
- workflow.step.completed
```

### 2. Include Request IDs

Always include a request/correlation ID for tracing:

```python
await event_bus.publish(
    Event(
        event_type="service.request",
        source="IV",
        data={
            "request_id": "REQ-001",  # ← Include this
            "service": "analytics"
        }
    )
)
```

### 3. Handle Timeouts

Set timeouts for async operations:

```python
try:
    response = await asyncio.wait_for(
        wait_for_response(request_id),
        timeout=30.0  # 30 seconds
    )
except asyncio.TimeoutError:
    print(f"Request {request_id} timed out")
```

### 4. Implement Retries

Use retry logic for transient failures:

```python
from src.utils.retry import retry_async

@retry_async(max_attempts=3, delay=1.0)
async def send_request(data):
    await event_bus.publish(Event(...))
```

### 5. Track Metrics

Monitor integration health:

```python
# Track request counts
metrics.increment(f"{domain}.requests.{service_type}")

# Track response times
with metrics.timer(f"{domain}.response_time"):
    result = await process_request(data)

# Track errors
metrics.increment(f"{domain}.errors")
```

### 6. Validate Governance

Always check governance approval:

```python
# Check integration exists and is approved
integration = governance.domain_registry.get_integration(integration_id)
if not integration or integration["status"] != "connected":
    raise ValueError("Integration not approved")
```

---

## Common Scenarios

### Scenario 1: Adding a New Domain

**Steps**:

1. **Register Domain**:
```python
result = await governance.register_domain(
    "NEW_DOMAIN",
    capabilities=["capability_1", "capability_2"]
)
```

2. **Request Integrations**:
```python
for target in ["PIPE", "BNP", "AXIS"]:
    await governance.request_integration(
        source_domain="NEW_DOMAIN",
        target_domain=target,
        integration_type="api",
        description=f"Integration with {target}"
    )
```

3. **Get Approvals**:
```python
# Review → Approve → Activate
```

4. **Implement Service**:
```python
# Use integration_template.py as starting point
```

---

### Scenario 2: Cross-Domain Data Query

**Use Case**: IV needs customer data from BNP

**Implementation**:

```python
# IV requests customer data
request_id = generate_request_id()

await event_bus.publish(
    Event(
        event_type="data.request",
        source="IV",
        data={
            "request_id": request_id,
            "entity_type": "customer",
            "entity_id": "CUST-12345",
            "fields": ["name", "tier", "health_score"]
        }
    )
)

# Wait for response
response = await wait_for_event(
    event_type="data.response",
    filter_fn=lambda e: e.data.get("request_id") == request_id,
    timeout=10.0
)

customer_data = response.data["entity"]
```

---

### Scenario 3: Broadcasting Notifications

**Use Case**: BNI broadcasts authentication failure to all domains

**Implementation**:

```python
# BNI detects suspicious activity
await event_bus.publish(
    Event(
        event_type="security.alert",
        source="BNI",
        data={
            "alert_type": "authentication_failure",
            "username": "suspicious@domain.com",
            "attempts": 5,
            "severity": "high",
            "timestamp": datetime.now().isoformat()
        }
    )
)

# All domains receive and log
for domain in ["BNP", "AXIS", "IV"]:
    event_bus.subscribe("security.alert", domain_alert_handler)
```

---

### Scenario 4: Long-Running Workflows

**Use Case**: Project approval takes hours/days

**Implementation**:

```python
# Use state management for persistence
workflow_id = str(uuid.uuid4())

# Save workflow state
await state_manager.set_value(
    "PIPE",
    f"workflow_{workflow_id}",
    {
        "status": "in_progress",
        "current_step": "budget_approval",
        "steps_completed": ["authentication", "project_creation"],
        "created_at": datetime.now().isoformat()
    }
)

# Resume workflow later
workflow_state = await state_manager.get_value(
    "PIPE",
    f"workflow_{workflow_id}"
)

# Continue from current_step
```

---

## Troubleshooting

### Issue 1: Integration Not Working

**Symptoms**: Events not received, no responses

**Checklist**:
- [ ] Integration approved in governance?
- [ ] Both domains registered?
- [ ] Event subscriptions set up?
- [ ] Correct event type names?
- [ ] Network connectivity OK?

**Debug**:
```python
# Check integration status
integration = governance.domain_registry.get_integration(integration_id)
print(f"Status: {integration['status']}")

# Check event history
events = event_bus.get_history("your.event.type")
print(f"Events: {len(events)}")
```

---

### Issue 2: Timeout Errors

**Symptoms**: Requests timing out

**Solutions**:

1. **Increase Timeout**:
```python
response = await asyncio.wait_for(request, timeout=60.0)  # Increase
```

2. **Check Service Health**:
```python
# Use health checks
health = health_checker.detailed_health_check()
print(health["components"])
```

3. **Add Retries**:
```python
@retry_async(max_attempts=3)
async def send_request():
    ...
```

---

### Issue 3: Compliance Failures

**Symptoms**: Governance blocking integrations

**Solutions**:

1. **Check Compliance**:
```python
compliance = governance.compliance_tracker.get_domain_compliance_summary(domain)
print(f"Compliance: {compliance['compliance_percentage']}%")
```

2. **Update Compliance**:
```python
governance.compliance_tracker.update_compliance(
    record_id=compliance_id,
    requirement_id="cross_domain_review",
    criteria_met=["review_completed", "approval_obtained"]
)
```

---

## Summary

### Quick Reference

| Pattern | Use Case | Example |
|---------|----------|---------|
| Request-Response | API calls, service requests | BNP analytics service |
| Pub-Sub | Notifications, broadcasts | BNI auth events |
| Workflow | Multi-step processes | Project approval |
| Data Sync | Consistency across domains | Customer data updates |
| Aggregation | Combine from multiple sources | Customer 360 view |

### Getting Started

1. **Start with examples**: Run `examples/integration_*.py`
2. **Use template**: Copy `examples/templates/integration_template.py`
3. **Follow patterns**: Use proven patterns from this guide
4. **Test thoroughly**: Run integration tests
5. **Monitor**: Use metrics and health checks

### Resources

- **Examples**: `examples/` directory
- **Templates**: `examples/templates/`
- **Governance**: `docs/GOVERNANCE.md`
- **Quick Start**: `docs/QUICK_START.md`
- **Monitoring**: `docs/MONITORING.md`

---

**Built with ❤️ for the BSW Architecture PIPE Domain**
