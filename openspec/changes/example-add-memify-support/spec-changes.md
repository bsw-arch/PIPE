# Specification Changes: Add Memify Support

This document shows the exact changes to be made to `openspec/specs/integrations/spec.md`.

## Change 1: Add Memify Requirement

**Location:** After line 83 (after "Pattern learning" scenario)

**Add:**

```gherkin
### Requirement: Cognee Memify for Derived Facts
The system SHALL use Memify to derive facts and insights from governance data.

#### Scenario: Derive compliance trends
- GIVEN governance data exists in Cognee
- WHEN memify_compliance_trends() is called
- THEN Cognee SHALL:
  - Analyze compliance records over time
  - Identify trending issues by domain
  - Calculate compliance improvement rates
  - Return derived facts with confidence scores

#### Scenario: Generate integration insights
- GIVEN integration approval history exists
- WHEN memify_integration_patterns() is called
- THEN Cognee SHALL:
  - Find common approval criteria across reviews
  - Identify rejection patterns by domain
  - Calculate success rates by domain pairs
  - Suggest improvements based on patterns
  - Return actionable insights

#### Scenario: Summarize domain health
- GIVEN comprehensive domain data exists
- WHEN memify_domain_health() is called with domain code
- THEN Cognee SHALL:
  - Aggregate compliance status across categories
  - Calculate integration success rate
  - Identify risk factors and trends
  - Generate health score (0-100)
  - Return comprehensive health summary

#### Scenario: Cache management
- GIVEN Memify results have been generated
- WHEN cache_memify_results() is called
- THEN results SHALL be cached for configurable TTL
- AND subsequent queries SHALL use cached results
- AND cache SHALL invalidate when underlying data changes
```

## Change 2: Update Implementation Notes

**Location:** Line 142 (Implementation Notes section)

**Current:**
```markdown
## Implementation Notes

- All integration clients are in `src/integrations/`
- Clients provide async Python interfaces
- Fallback implementations for when dependencies unavailable
- Comprehensive error handling and logging
- Singleton pattern for client instances
```

**Change to:**
```markdown
## Implementation Notes

- All integration clients are in `src/integrations/`
- Clients provide async Python interfaces
- Fallback implementations for when dependencies unavailable
- Comprehensive error handling and logging
- Singleton pattern for client instances
- Cognee workflow: Add → Cognify → Search/Memify
  - **Add**: Ingest raw DataPoints
  - **Cognify**: Build knowledge graph and embeddings
  - **Search**: Retrieve existing data semantically
  - **Memify**: Derive new facts and insights from existing data
```

## Change 3: Add Memify Methods to Implementation

**Location:** New section before "Forbidden Technologies" (line 124)

**Add:**

```markdown
## Cognee Memify Methods

The CogneeClient SHALL implement these Memify methods:

### memify_compliance_trends()
```python
async def memify_compliance_trends(
    time_range: Optional[tuple] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Derive compliance trends from historical data.

    Args:
        time_range: Optional (start_ts, end_ts) tuple
        domain: Optional domain code to filter by

    Returns:
        Dict containing:
        - trends: List of derived trend facts
        - top_issues: Most common compliance issues
        - improvement_rate: Percentage improvement over time
        - at_risk_domains: Domains with declining compliance
        - timestamp: When analysis was performed
    """
```

### memify_integration_patterns()
```python
async def memify_integration_patterns(
    integration_type: Optional[str] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate insights from integration approval history.

    Args:
        integration_type: Optional filter (hub, direct, mesh)
        domain: Optional domain code to filter by

    Returns:
        Dict containing:
        - approval_criteria: Common factors in approvals
        - rejection_patterns: Common reasons for rejection
        - success_rates: Success rate by domain pair
        - recommendations: Suggested improvements
        - confidence: Confidence score (0.0 to 1.0)
    """
```

### memify_domain_health()
```python
async def memify_domain_health(
    domain_code: str
) -> Dict[str, Any]:
    """
    Generate comprehensive domain health report.

    Args:
        domain_code: Domain to analyze (BNI, BNP, etc.)

    Returns:
        Dict containing:
        - domain: Domain code
        - health_score: Overall score (0-100)
        - compliance_status: Aggregated compliance
        - integration_health: Integration success metrics
        - risk_factors: Identified risks
        - recommendations: Actionable recommendations
        - generated_at: Timestamp
    """
```
```

## Testing Requirements

**Add to specification:**

```gherkin
### Requirement: Memify Testing
Memify functionality SHALL be thoroughly tested.

#### Scenario: Verify derived facts accuracy
- GIVEN known patterns exist in historical data
- WHEN Memify derives facts
- THEN derived facts SHALL match expected patterns
- AND confidence scores SHALL reflect accuracy

#### Scenario: Cache behavior
- GIVEN Memify results are cached
- WHEN data changes
- THEN cache SHALL invalidate
- AND fresh Memify SHALL be triggered on next request

#### Scenario: Performance requirements
- GIVEN a Memify request
- WHEN processing completes
- THEN response time SHALL be under 5 seconds
- AND shall scale to datasets of 10,000+ DataPoints
```

## Diff Summary

| Section | Type | Lines |
|---------|------|-------|
| Add Memify Requirement | Addition | +40 |
| Update Implementation Notes | Modification | ~8 |
| Add Memify Methods | Addition | +60 |
| Add Testing Requirements | Addition | +20 |
| **Total Changes** | | **+128 lines** |

## Validation

After applying these changes:

1. ✅ All scenarios use proper Given-When-Then format
2. ✅ Requirements use SHALL/SHALL NOT keywords
3. ✅ Methods have complete type hints and docstrings
4. ✅ Testing requirements are specific and measurable
5. ✅ Changes maintain consistency with existing spec style

## Dependencies

These specification changes depend on:

- ✅ Cognee 0.1.20+ (Memify support)
- ✅ Existing Add/Cognify/Search implementation
- ✅ DataPoint models in `src/governance/datapoints.py`
- ⏳ Memify implementation in `src/integrations/cognee_client.py` (to be added)

## Breaking Changes

**None.** This is an additive change. All existing Add/Cognify/Search functionality remains unchanged.

## Rollout Plan

1. **Phase 1:** Add methods to CogneeClient with basic implementation
2. **Phase 2:** Add comprehensive unit tests
3. **Phase 3:** Create example demonstrating all three Memify methods
4. **Phase 4:** Deploy to staging and validate with real data
5. **Phase 5:** Update documentation with Memify workflows
6. **Phase 6:** Production deployment with monitoring
