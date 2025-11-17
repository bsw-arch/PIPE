# Specification Changes: Add PR-QUEST Integration

This document shows the exact changes to be made to PIPE specifications.

## Change 1: Add PR Review Bot to Bot Specification

**File:** `openspec/specs/bots/spec.md`

**Location:** After the Integration Hub Bot section (approximately line 100)

**Add:**

```markdown
## PR Review Bot

The fifth bot type provides automated PR code review using PR-QUEST.

### Requirement: PR Review Bot Lifecycle
The PR Review Bot SHALL monitor GitHub for integration PRs and analyze them using PR-QUEST.

#### Scenario: Bot initialization
- GIVEN PR-QUEST service is available
- WHEN the bot initializes
- THEN it SHALL connect to PR-QUEST API
- AND authenticate with GitHub API
- AND subscribe to integration PR events

#### Scenario: PR detection
- GIVEN an integration request has an associated GitHub PR
- WHEN the PR is created or updated
- THEN the bot SHALL detect the PR within 5 minutes
- AND queue it for analysis

#### Scenario: PR analysis
- GIVEN a PR is queued for analysis
- WHEN the bot processes it
- THEN it SHALL:
  - Send PR URL to PR-QUEST
  - Wait for LLM-powered analysis
  - Parse clusters and risk assessments
  - Store results as PRReviewDataPoint in Cognee
  - Update governance status
  - Publish pr_review_complete event

#### Scenario: Auto-approval
- GIVEN PR analysis completed successfully
- AND no critical or moderate risks detected
- AND confidence score >= configured threshold
- WHEN determining decision
- THEN the bot SHALL automatically approve the integration
- AND notify stakeholders

#### Scenario: Risk flagging
- GIVEN PR analysis detected risks
- WHEN risk level is CRITICAL
- THEN the bot SHALL:
  - Reject the integration automatically
  - Create detailed report with specific issues
  - Notify integration owner
  - Require human override for approval

#### Scenario: Human review request
- GIVEN PR analysis detected moderate risks
- WHEN risk level is MODERATE
- THEN the bot SHALL:
  - Flag integration for human review
  - Provide LLM suggestions for fixes
  - Assign to governance reviewer
  - Track in review queue

### Requirement: PR-QUEST Integration
The bot SHALL use PR-QUEST API for all PR analysis.

#### Scenario: Send PR to PR-QUEST
- GIVEN a valid GitHub PR URL
- WHEN requesting analysis
- THEN the bot SHALL:
  - POST to /api/analyze endpoint
  - Include PR URL and analysis options
  - Receive analysis ID for tracking

#### Scenario: Retrieve analysis results
- GIVEN an analysis ID from PR-QUEST
- WHEN fetching results
- THEN the bot SHALL:
  - GET /api/results/{analysis_id}
  - Parse clusters, risks, and suggestions
  - Handle incomplete analysis gracefully

#### Scenario: Export review markdown
- GIVEN completed PR analysis
- WHEN exporting for documentation
- THEN the bot SHALL:
  - GET /api/export/{analysis_id}
  - Receive markdown-formatted review
  - Store in governance records

### Requirement: Pattern Learning
The bot SHALL store all PR reviews in Cognee for pattern recognition.

#### Scenario: Store review in Cognee
- GIVEN a completed PR analysis
- WHEN storing results
- THEN the bot SHALL:
  - Create PRReviewDataPoint with all metadata
  - Add to Cognee memory
  - Cognify to build knowledge graph
  - Enable semantic search on risks and suggestions

#### Scenario: Learn from historical reviews
- GIVEN multiple PR reviews stored in Cognee
- WHEN analyzing a new PR
- THEN the bot SHALL:
  - Search for similar past PRs
  - Identify recurring patterns
  - Suggest fixes based on precedent
  - Calculate confidence from historical data

### Requirement: Gamification Support
The bot SHALL track reviewer XP using PR-QUEST's gamification.

#### Scenario: Award XP for human reviews
- GIVEN a human reviewer completes a PR review
- WHEN recording the review
- THEN the bot SHALL:
  - Fetch XP awarded from PR-QUEST
  - Update reviewer's total XP
  - Publish xp_awarded event
  - Trigger achievement checks

#### Scenario: Leaderboard tracking
- GIVEN multiple reviewers active
- WHEN generating leaderboard
- THEN the bot SHALL:
  - Fetch XP data from PR-QUEST
  - Rank reviewers by total XP
  - Highlight top performers
  - Encourage participation
```

---

## Change 2: Update Governance Specification

**File:** `openspec/specs/governance/spec.md`

**Location:** After "Integration Request Workflow" section (approximately line 45)

**Add:**

```markdown
### Requirement: PR Code Review Workflow
The system SHALL automatically review integration PRs using PR-QUEST.

#### Scenario: PR created for integration
- GIVEN an integration request is approved for implementation
- WHEN a GitHub PR is created
- THEN the system SHALL:
  - Link PR to integration request
  - Trigger PR Review Bot analysis
  - Update integration status to "UNDER_PR_REVIEW"

#### Scenario: Clean PR review
- GIVEN PR analysis completed
- AND no risks detected
- AND confidence >= auto_approve_threshold
- WHEN reviewing results
- THEN the system SHALL:
  - Auto-approve the integration
  - Update status to "APPROVED"
  - Merge PR automatically (if configured)
  - Publish integration_approved event

#### Scenario: PR with critical risks
- GIVEN PR analysis detected critical risks
- WHEN reviewing results
- THEN the system SHALL:
  - Reject the integration
  - Update status to "REJECTED_CODE_ISSUES"
  - Block PR merge
  - Create detailed issue report
  - Notify integration owner with fixes required

#### Scenario: PR requiring human review
- GIVEN PR analysis detected moderate risks
- WHEN reviewing results
- THEN the system SHALL:
  - Update status to "NEEDS_HUMAN_REVIEW"
  - Assign to governance reviewer
  - Provide LLM suggestions
  - Set review deadline
  - Track in review queue

#### Scenario: Human override approval
- GIVEN a PR was rejected by automated review
- AND a human reviewer believes it's safe
- WHEN submitting override
- THEN the system SHALL:
  - Require override justification
  - Log override decision in Cognee
  - Approve integration with human_override flag
  - Notify stakeholders

### Requirement: PR Review Quality Gates
The system SHALL enforce quality gates based on PR analysis.

#### Scenario: Security vulnerability detected
- GIVEN PR analysis found security vulnerability
- WHEN risk type is SECURITY
- THEN the system SHALL:
  - Block integration immediately
  - Require security team review
  - Prevent auto-approval
  - Escalate to security channel

#### Scenario: Breaking change detected
- GIVEN PR analysis found breaking changes
- WHEN risk type is BREAKING_CHANGE
- THEN the system SHALL:
  - Require architectural review
  - Check if breaking change is documented
  - Verify migration plan exists
  - Notify affected domains

#### Scenario: Integration anti-pattern detected
- GIVEN PR analysis found anti-patterns
- WHEN risk type is ANTI_PATTERN
- THEN the system SHALL:
  - Provide alternative approaches
  - Suggest architectural improvements
  - Allow approval with acknowledgment
  - Track technical debt

### Requirement: Review Pattern Learning
The system SHALL learn from PR reviews to improve future analysis.

#### Scenario: Store review decision in Cognee
- GIVEN a PR review completed (automated or human)
- WHEN storing the decision
- THEN the system SHALL:
  - Create PRReviewDataPoint with full context
  - Link to integration request
  - Add to Cognee memory
  - Enable semantic search

#### Scenario: Suggest similar issues
- GIVEN a new PR under review
- WHEN analyzing code patterns
- THEN the system SHALL:
  - Search Cognee for similar past issues
  - Identify recurring problems
  - Suggest fixes from historical data
  - Calculate confidence based on precedent

#### Scenario: Improve detection over time
- GIVEN accumulating PR review history
- WHEN pattern emerges across multiple PRs
- THEN the system SHALL:
  - Identify new anti-pattern category
  - Update risk detection rules
  - Apply to future reviews
  - Report improvement metrics
```

---

## Change 3: Add PR-QUEST to Integrations Specification

**File:** `openspec/specs/integrations/spec.md`

**Location:** After Cognee section (approximately line 90)

**Add:**

```markdown
### Requirement: PR-QUEST Interactive PR Review
The system SHALL use PR-QUEST for automated code review of integration PRs.

#### Scenario: PR analysis request
- GIVEN a valid GitHub PR URL
- WHEN requesting analysis
- THEN the system SHALL:
  - POST to PR-QUEST /api/analyze endpoint
  - Include PR URL and configuration
  - Receive analysis ID
  - Poll for results until complete

#### Scenario: LLM-powered clustering
- GIVEN PR-QUEST is analyzing a PR
- WHEN using LLM mode
- THEN PR-QUEST SHALL:
  - Fetch PR diff from GitHub
  - Parse unified diff format
  - Use LLM (GPT-4o-mini or configured model) to cluster related changes
  - Group by logical functionality
  - Return clustered changes with descriptions

#### Scenario: Risk detection
- GIVEN PR-QUEST completed clustering
- WHEN analyzing for risks
- THEN PR-QUEST SHALL:
  - Apply heuristic rules for common issues
  - Use LLM to identify security vulnerabilities
  - Detect breaking changes
  - Find integration anti-patterns
  - Return risk level (NONE, LOW, MODERATE, CRITICAL)

#### Scenario: Suggestion generation
- GIVEN risks detected in PR
- WHEN generating suggestions
- THEN PR-QUEST SHALL:
  - Use LLM to provide actionable fixes
  - Include code examples where applicable
  - Prioritize by impact
  - Link to relevant documentation

#### Scenario: Review step rendering
- GIVEN PR analysis completed
- WHEN human reviewer requests steps
- THEN PR-QUEST SHALL:
  - Return interactive review steps
  - Show diff sections with react-diff-view
  - Allow per-step notes
  - Track review progress

#### Scenario: Markdown export
- GIVEN completed PR review (automated or human)
- WHEN requesting export
- THEN PR-QUEST SHALL:
  - Generate markdown document
  - Include all clusters and analysis
  - Add reviewer notes
  - Format for governance records

#### Scenario: XP gamification
- GIVEN a reviewer completes thorough review
- WHEN awarding XP
- THEN PR-QUEST SHALL:
  - Calculate XP based on:
    - PR complexity (lines changed)
    - Review thoroughness (notes added)
    - Time to complete
  - Award XP to reviewer
  - Update leaderboard
  - Trigger achievements if applicable

#### Scenario: Result caching
- GIVEN a PR was analyzed previously
- AND PR content hasn't changed
- WHEN requesting re-analysis
- THEN PR-QUEST SHALL:
  - Check cache by PR SHA
  - Return cached results if valid
  - Skip LLM processing
  - Save API costs and time

### Requirement: PR-QUEST Deployment
PR-QUEST SHALL be deployed as a service in the PIPE infrastructure.

#### Scenario: Kubernetes deployment
- GIVEN Kubernetes cluster is available
- WHEN deploying PR-QUEST
- THEN the system SHALL:
  - Create pr-quest-service in pipe-system namespace
  - Expose on port 3000
  - Mount OPENAI_API_KEY from OpenBao
  - Set resource limits (1Gi memory, 500m CPU)
  - Configure health checks

#### Scenario: Service discovery
- GIVEN PR-QUEST service deployed
- WHEN PR Review Bot needs to connect
- THEN it SHALL:
  - Resolve pr-quest-service.pipe-system.svc.cluster.local
  - Connect over cluster network
  - Use Cilium network policies for security

#### Scenario: Fallback mode
- GIVEN PR-QUEST service is unavailable
- WHEN PR Review Bot attempts analysis
- THEN it SHALL:
  - Log service unavailable error
  - Fall back to basic diff parsing (no LLM)
  - Queue PR for retry
  - Notify administrators
  - Continue with degraded functionality
```

---

## Change 4: Add PRReviewDataPoint

**File:** `src/governance/datapoints.py` (implementation file, not spec)

This is referenced in the governance spec but implementation detail:

```python
class PRReviewDataPoint(DataPoint):
    """Represents a PR-QUEST code review for governance tracking."""

    # PR Metadata
    pr_url: str
    pr_number: int
    repository: str
    analysis_id: str

    # PR-QUEST Analysis Results
    clusters: List[Dict[str, Any]]  # Grouped changes from LLM
    risks: List[str]                # Detected issues
    risk_level: str                 # NONE, LOW, MODERATE, CRITICAL
    suggestions: List[str]          # LLM recommendations
    xp_awarded: int                 # Gamification score

    # Review Decision
    decision: str                   # APPROVE, REJECT, NEEDS_REVIEW
    reviewer: str                   # Bot or human username
    reviewed_at: int                # Unix timestamp
    review_duration_seconds: int    # Time to complete

    # Integration Context
    integration_id: Optional[str] = None
    source_domain: Optional[str] = None
    target_domain: Optional[str] = None

    # Override Info
    human_override: bool = False
    override_justification: Optional[str] = None

    # Semantic search on risks and suggestions
    metadata: dict = {"index_fields": ["risks", "suggestions", "decision"]}
```

---

## Summary of Changes

| File | Section | Type | Lines Added |
|------|---------|------|-------------|
| `openspec/specs/bots/spec.md` | PR Review Bot | Added | ~120 |
| `openspec/specs/governance/spec.md` | PR Code Review Workflow | Added | ~100 |
| `openspec/specs/governance/spec.md` | PR Review Quality Gates | Added | ~60 |
| `openspec/specs/governance/spec.md` | Review Pattern Learning | Added | ~40 |
| `openspec/specs/integrations/spec.md` | PR-QUEST Integration | Added | ~90 |
| `openspec/specs/integrations/spec.md` | PR-QUEST Deployment | Added | ~40 |
| `src/governance/datapoints.py` | PRReviewDataPoint | Added | ~30 |
| **Total** | | | **~480 lines** |

---

## Validation Checklist

After applying these changes, verify:

- [ ] All scenarios use proper Given-When-Then format
- [ ] All requirements use SHALL/SHALL NOT keywords
- [ ] PR Review Bot lifecycle matches BotBase pattern
- [ ] Governance workflow integrates seamlessly
- [ ] PRReviewDataPoint has proper index_fields
- [ ] PR-QUEST deployment follows infrastructure standards
- [ ] All risk levels are enumerated clearly
- [ ] XP gamification is optional (can be disabled)
- [ ] Fallback mode handles PR-QUEST unavailability
- [ ] Human override workflow is documented
- [ ] Pattern learning leverages Cognee properly

---

## Testing Requirements

These spec changes require corresponding tests:

### Unit Tests
- `tests/bots/test_pr_review_bot.py` - PR Review Bot lifecycle
- `tests/integrations/test_pr_quest_client.py` - PR-QUEST API client
- `tests/governance/test_pr_review_workflow.py` - Governance integration

### Integration Tests
- `tests/integration/test_full_pr_review.py` - End-to-end PR review
- `tests/integration/test_pr_quest_fallback.py` - Degraded mode
- `tests/integration/test_cognee_pr_learning.py` - Pattern learning

### E2E Tests
- Create test PR → Auto-analysis → Auto-approval (clean)
- Create test PR → Risk detection → Human review (moderate risks)
- Create test PR → Critical risks → Auto-reject

---

## Dependencies

| Dependency | Version | Status |
|------------|---------|--------|
| PR-QUEST | Phases 0-6 | ✅ Available |
| GitHub API | v3 | ✅ Available |
| OpenAI API | GPT-4o-mini | ✅ Available |
| Cognee | 0.1.20+ | ✅ Installed |
| aiohttp | 3.8+ | ✅ Installed |

---

## Breaking Changes

**None.** All changes are additive:
- New bot type (doesn't affect existing bots)
- New integration (optional)
- New DataPoint type (extends existing)
- Enhanced governance workflow (backward compatible)

---

## Rollout Sequence

1. **Update Specifications** (this document)
2. **Implement PRQuestClient** (`src/integrations/pr_quest_client.py`)
3. **Add PRReviewDataPoint** (`src/governance/datapoints.py`)
4. **Implement PR Review Bot** (`src/bots/pr_review_bot.py`)
5. **Update GovernanceManager** (add PR review methods)
6. **Write Tests** (unit, integration, E2E)
7. **Deploy PR-QUEST Service** (Kubernetes + Helm)
8. **Enable PR Review Bot** (configuration)
9. **Monitor and Tune** (thresholds, performance)

---

## Migration Notes

For existing PIPE installations:

1. **No data migration required** - All changes are new features
2. **Configuration update needed** - Add `pr_review` section to config.yaml
3. **PR-QUEST deployment** - New service to deploy
4. **OpenAI API key** - Required for LLM features (or use LLM-free mode)
5. **GitHub token** - Needs PR read permissions

---

## Success Metrics

After implementation, measure:

- **PR Analysis Time** - Target: <30 seconds per PR
- **Auto-Approval Rate** - Target: 70% of clean PRs
- **False Positive Rate** - Target: <5% of flagged risks are incorrect
- **Reviewer XP Growth** - Track engagement via gamification
- **Pattern Learning** - Improvement in suggestion accuracy over time
- **Cost** - LLM API costs per PR (optimize with caching)

---

**Last Updated:** 2025-01-17
**Status:** Draft - Ready for review
**Related Proposal:** `openspec/changes/add-pr-quest-integration/proposal.md`
