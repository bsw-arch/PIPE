# Change Proposal: Add Memify Support to Cognee Integration

## Metadata
- **Proposal ID**: CHANGE-001
- **Status**: Example (for demonstration)
- **Proposed By**: Example
- **Date**: 2025-01-17
- **Affects**: `openspec/specs/integrations/spec.md`

## Summary

Add support for Cognee's Memify feature to derive facts from existing governance data in AI memory. This enables higher-order reasoning about integration patterns, compliance trends, and governance decisions.

## Motivation

Currently, PIPE uses Cognee's Add → Cognify → Search workflow, which:
- Adds raw governance DataPoints
- Builds knowledge graph with entities and relationships
- Enables semantic search

Memify adds a critical capability:
- **Derive facts** from existing data (e.g., "domains with >90% compliance")
- **Generate summaries** (e.g., "integration approval trends over time")
- **Create insights** (e.g., "common rejection reasons by domain")

This would enable:
1. Automatic trend detection in governance decisions
2. Compliance pattern analysis across domains
3. Predictive suggestions based on derived facts
4. Governance intelligence reports

## Current Behavior

**Integration specification (lines 50-83):**
```gherkin
### Requirement: Cognee AI Memory
The system SHALL use Cognee for governance intelligence.

#### Scenario: Governance data ingestion
- GIVEN new governance data (domains, integrations, reviews)
- WHEN add_datapoints() is called
- THEN DataPoints SHALL be added to Cognee

#### Scenario: Knowledge graph building
- GIVEN DataPoints have been added
- WHEN cognify_governance_data() is called
- THEN Cognee SHALL build knowledge graph

#### Scenario: Semantic search
- GIVEN a natural language query
- WHEN search_integrations() is called
- THEN Cognee SHALL return contextually relevant results
```

**Missing:** No requirement for deriving facts or generating insights from existing data.

## Proposed Behavior

Add new requirement and scenarios:

```gherkin
### Requirement: Cognee Memify for Derived Facts
The system SHALL use Memify to derive facts from governance data.

#### Scenario: Derive compliance trends
- GIVEN governance data exists in Cognee
- WHEN memify_compliance_trends() is called
- THEN Cognee SHALL:
  - Analyze compliance records over time
  - Identify trending issues by domain
  - Calculate compliance improvement rates
  - Return derived facts

#### Scenario: Generate integration insights
- GIVEN integration history exists
- WHEN memify_integration_patterns() is called
- THEN Cognee SHALL:
  - Find common approval criteria
  - Identify rejection patterns
  - Calculate success rates by domain pair
  - Return actionable insights

#### Scenario: Summarize domain health
- GIVEN comprehensive domain data
- WHEN memify_domain_health() is called with domain code
- THEN Cognee SHALL:
  - Aggregate compliance status
  - Calculate integration success rate
  - Identify risk factors
  - Return health summary
```

## Implementation Plan

### 1. Update CogneeClient (src/integrations/cognee_client.py)

Add three new methods:

```python
async def memify_compliance_trends(
    self,
    time_range: Optional[tuple] = None
) -> Dict[str, Any]:
    """Derive compliance trends from historical data."""
    query = "compliance trends and patterns over time"
    derived_facts = await memify(query, time_range=time_range)
    return {
        "trends": derived_facts,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

async def memify_integration_patterns(
    self,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """Generate insights from integration approval history."""
    query = f"integration approval patterns for {domain or 'all domains'}"
    insights = await memify(query)
    return {
        "patterns": insights,
        "domain": domain,
        "confidence": self._calculate_confidence(insights)
    }

async def memify_domain_health(
    self,
    domain_code: str
) -> Dict[str, Any]:
    """Generate comprehensive domain health report."""
    query = f"overall health and status of {domain_code} domain"
    summary = await memify(query)
    return {
        "domain": domain_code,
        "health_summary": summary,
        "generated_at": int(datetime.now().timestamp() * 1000)
    }
```

### 2. Add Example (examples/cognee/memify_governance.py)

Create comprehensive example demonstrating:
- Compliance trend analysis
- Integration pattern insights
- Domain health summaries

### 3. Update Tests

Add tests to `tests/integrations/test_cognee_client.py`:
- `test_memify_compliance_trends`
- `test_memify_integration_patterns`
- `test_memify_domain_health`

## Testing Plan

### Unit Tests
- Mock Cognee's memify() responses
- Verify correct query construction
- Validate returned data structure

### Integration Tests
- Test with real Cognee instance (requires LLM provider)
- Verify derived facts match expected patterns
- Test with historical governance data

### Manual Testing
1. Add 50+ governance DataPoints spanning 3 months
2. Run `memify_compliance_trends()`
3. Verify trends match manual analysis
4. Run `memify_domain_health("BNI")`
5. Verify summary is accurate and actionable

## Documentation Updates

- [ ] Update `docs/COGNEE_INTEGRATION.md` with Memify section
- [ ] Add Memify workflow diagram
- [ ] Document when to use Memify vs Search
- [ ] Add example outputs to documentation

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM costs increase | Medium | Implement caching for Memify results |
| Derived facts may be incorrect | High | Always show confidence scores, allow verification |
| Performance impact on large datasets | Medium | Implement incremental Memify with time windows |

## Alternatives Considered

### Alternative 1: Manual Analytics
**Pros:** Full control, no LLM costs
**Cons:** Requires manual SQL/code for each analysis type

### Alternative 2: Separate Analytics Service
**Pros:** Decoupled from Cognee
**Cons:** Loses semantic understanding, duplicates data

### Alternative 3: Use only Search
**Pros:** No additional implementation
**Cons:** Cannot derive facts, only retrieves existing data

**Decision:** Proceed with Memify integration for maximum governance intelligence.

## Success Criteria

- [ ] All three Memify methods implemented
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests pass with real Cognee
- [ ] Example demonstrates all three use cases
- [ ] Documentation updated
- [ ] Performance acceptable (<5s per Memify call)

## Open Questions

1. Should Memify results be cached? For how long?
2. What confidence threshold should trigger manual review?
3. Should Memify run on schedule or on-demand?

## References

- Cognee Memify Documentation: [shared in conversation]
- OpenSpec Specification: `openspec/specs/integrations/spec.md`
- Current Cognee Client: `src/integrations/cognee_client.py`
- Existing Examples: `examples/cognee/governance_memory.py`
