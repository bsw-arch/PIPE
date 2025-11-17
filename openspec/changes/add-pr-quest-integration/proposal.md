# Change Proposal: Add PR-QUEST Integration for Governance Reviews

## Metadata
- **Proposal ID**: CHANGE-002
- **Status**: Draft
- **Proposed By**: Claude (AI Assistant)
- **Date**: 2025-01-17
- **Affects**:
  - `openspec/specs/bots/spec.md`
  - `openspec/specs/governance/spec.md`
  - `openspec/specs/integrations/spec.md`

## Summary

Integrate PR-QUEST (Fission-AI's interactive PR review platform) into PIPE's governance workflow to enable automated, gamified, and LLM-powered code review for cross-domain integration proposals. This creates a new PR Review Bot and enhances the governance review pipeline with intelligent PR analysis.

## Motivation

### Current Limitations

PIPE's governance system currently:
- Reviews integration requests at the architectural level
- Lacks automated code-level review for integration PRs
- Has no gamification or engagement features for reviewers
- Cannot automatically cluster related changes in large PRs
- Doesn't learn from PR review patterns over time

### Why PR-QUEST?

PR-QUEST provides:
1. **LLM-Powered Analysis** - Intelligent grouping of PR changes using AI SDK + OpenAI
2. **Interactive Review** - Step-by-step guided review experience
3. **Gamification** - XP system to encourage thorough reviews
4. **Smart Clustering** - Automatic grouping of related code changes
5. **Markdown Export** - Notes and review comments exportable for governance records
6. **Caching** - Efficient re-review of updated PRs

### Integration Benefits

Combining PIPE + PR-QUEST enables:
- **Automated PR Review Bot** - Continuously monitor integration PRs
- **Governance Integration** - PR analysis feeds into compliance decisions
- **Pattern Learning** - Store PR reviews in Cognee for learning
- **Quality Gates** - Block integrations with problematic code patterns
- **Reviewer Guidance** - LLM highlights potential integration issues

## Current Behavior

**Governance workflow (openspec/specs/governance/spec.md):**

```gherkin
### Requirement: Integration Request Workflow
The system SHALL implement an approval workflow for cross-domain integrations.

#### Scenario: Integration request
- GIVEN source and target domains exist
- WHEN request_integration() is called
- THEN a review SHALL be created
- AND integration SHALL be registered with PENDING status
```

**Missing:** No automated code-level review of integration PRs.

## Proposed Behavior

### New PR Review Bot

Add a fifth bot type to PIPE:

```
PIPE Bots:
1. Pipeline Bot        - Pipeline orchestration
2. Data Processor Bot  - Data transformation
3. Monitor Bot         - Health monitoring
4. Integration Hub Bot - Cross-domain governance
5. PR Review Bot ⭐ NEW - Automated PR analysis
```

### PR-QUEST Integration Architecture

```
┌─────────────────────────────────────────────────┐
│            PR Review Bot                         │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐      ┌──────────────────┐    │
│  │   Monitor    │─────▶│   PR-QUEST API   │    │
│  │  GitHub PRs  │      │  (localhost:3000)│    │
│  └──────┬───────┘      └────────┬─────────┘    │
│         │                       │               │
│         │ PR detected           │ Analysis      │
│         ▼                       ▼               │
│  ┌──────────────┐      ┌──────────────────┐    │
│  │  Fetch Diff  │      │ LLM Analysis     │    │
│  │   & Parse    │      │ • Clustering     │    │
│  └──────┬───────┘      │ • Risk Detection │    │
│         │              │ • Suggestions    │    │
│         │              └────────┬─────────┘    │
│         ▼                       ▼               │
│  ┌──────────────────────────────────────┐      │
│  │      Store in Cognee                 │      │
│  │   (ReviewDecisionDataPoint)          │      │
│  └──────────────┬───────────────────────┘      │
│                 │                               │
│                 ▼                               │
│  ┌──────────────────────────────────────┐      │
│  │   Update Governance Status           │      │
│  │   • Approve if clean                 │      │
│  │   • Flag if issues found             │      │
│  └──────────────────────────────────────┘      │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Workflow

**Phase 1: PR Detection**
1. Integration request creates GitHub PR
2. PR Review Bot detects new PR via webhook or polling
3. Bot fetches PR URL and metadata

**Phase 2: PR-QUEST Analysis**
1. Bot sends PR URL to PR-QUEST API
2. PR-QUEST fetches diff and parses changes
3. LLM clusters related changes into logical groups
4. Heuristics detect potential issues:
   - Security vulnerabilities
   - Breaking changes
   - Integration anti-patterns
   - Compliance violations

**Phase 3: Review Decision**
1. Analysis results stored as ReviewDecisionDataPoint in Cognee
2. If clean: Auto-approve integration
3. If issues: Flag for human review with specific concerns
4. XP awarded to human reviewers based on thoroughness

**Phase 4: Pattern Learning**
1. All reviews stored in Cognee memory
2. Future similar PRs get contextual suggestions
3. Common patterns recognized automatically

## Implementation Plan

### 1. PR-QUEST Client (src/integrations/pr_quest_client.py)

```python
class PRQuestClient:
    """Client for PR-QUEST interactive PR review platform."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def analyze_pr(
        self,
        pr_url: str,
        include_llm_analysis: bool = True
    ) -> PRAnalysisResult:
        """
        Analyze a GitHub PR using PR-QUEST.

        Args:
            pr_url: Full GitHub PR URL
            include_llm_analysis: Use LLM for intelligent clustering

        Returns:
            PRAnalysisResult with clustered changes and insights
        """
        # POST /api/analyze with PR URL
        # Returns: { clusters, risks, suggestions, xp_awarded }

    async def get_review_steps(self, analysis_id: str) -> List[ReviewStep]:
        """Get interactive review steps for a PR analysis."""

    async def submit_review_notes(
        self,
        analysis_id: str,
        notes: List[ReviewNote]
    ) -> bool:
        """Submit review notes for specific PR sections."""

    async def export_markdown(self, analysis_id: str) -> str:
        """Export complete review as markdown."""

    async def get_xp_leaderboard(self) -> List[ReviewerXP]:
        """Get reviewer XP leaderboard for gamification."""
```

### 2. PR Review Bot (src/bots/pr_review_bot.py)

```python
class PRReviewBot(BotBase):
    """
    Bot for automated PR review using PR-QUEST.

    Monitors GitHub for integration PRs, analyzes them with PR-QUEST,
    stores results in Cognee, and updates governance status.
    """

    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        super().__init__("PRReviewBot", event_bus)
        self.pr_quest_client = PRQuestClient(config.get("pr_quest_url"))
        self.cognee_client = get_cognee_client()
        self.github_token = config.get("github_token")
        self.check_interval = config.get("check_interval", 300)  # 5 min

    async def execute(self) -> None:
        """Main execution loop - check for new integration PRs."""
        pending_prs = await self._get_pending_integration_prs()

        for pr in pending_prs:
            try:
                # Analyze with PR-QUEST
                analysis = await self.pr_quest_client.analyze_pr(
                    pr.url,
                    include_llm_analysis=True
                )

                # Store in Cognee
                review_dp = ReviewDecisionDataPoint(
                    review_id=f"PR-{pr.number}",
                    review_type="CODE_REVIEW",
                    decision=self._determine_decision(analysis),
                    rationale=self._generate_rationale(analysis),
                    reviewer="PRReviewBot"
                )
                await self.cognee_client.add_datapoints([review_dp])

                # Update governance
                await self._update_governance_status(pr, analysis)

                # Publish event
                await self.event_bus.publish(Event(
                    "pr_review_complete",
                    {
                        "pr_url": pr.url,
                        "decision": review_dp.decision,
                        "risks": analysis.risks
                    }
                ))

            except Exception as e:
                logger.error(f"PR review failed for {pr.url}: {e}")

    def _determine_decision(self, analysis: PRAnalysisResult) -> str:
        """Decide approval status based on analysis."""
        if analysis.critical_risks:
            return "REJECT"
        elif analysis.moderate_risks:
            return "NEEDS_HUMAN_REVIEW"
        else:
            return "APPROVE"
```

### 3. Governance Integration

Update `src/governance/governance_manager.py`:

```python
async def review_integration_pr(
    self,
    integration_id: str,
    pr_url: str
) -> ReviewResult:
    """
    Review integration PR using PR-QUEST.

    This is called automatically when a PR is created for an integration.
    """
    # Get PR Review Bot
    pr_bot = self._get_pr_review_bot()

    # Trigger analysis
    analysis = await pr_bot.analyze_pr(pr_url)

    # Update integration status
    integration = self.integrations[integration_id]
    integration["pr_review"] = {
        "status": analysis.decision,
        "risks": analysis.risks,
        "reviewed_at": datetime.now().isoformat()
    }

    # Publish governance event
    await self.event_bus.publish(Event(
        "integration_pr_reviewed",
        {
            "integration_id": integration_id,
            "decision": analysis.decision
        }
    ))

    return ReviewResult(
        approved=(analysis.decision == "APPROVE"),
        feedback=analysis.suggestions
    )
```

### 4. Cognee DataPoint for PR Reviews

Add to `src/governance/datapoints.py`:

```python
class PRReviewDataPoint(DataPoint):
    """Represents a PR-QUEST code review."""

    pr_url: str
    pr_number: int
    repository: str
    analysis_id: str

    # PR-QUEST results
    clusters: List[Dict[str, Any]]  # Grouped changes
    risks: List[str]                # Detected issues
    suggestions: List[str]          # LLM recommendations
    xp_awarded: int                 # Gamification score

    # Review metadata
    reviewer: str                   # Bot or human
    reviewed_at: int                # Timestamp
    decision: str                   # APPROVE, REJECT, NEEDS_REVIEW

    # Integration context
    integration_id: Optional[str] = None
    related_domain: Optional[str] = None

    # Semantic search on risks and suggestions
    metadata: dict = {"index_fields": ["risks", "suggestions"]}
```

### 5. Configuration

Add to `config/config.yaml`:

```yaml
bots:
  pr_review:
    enabled: true
    check_interval: 300  # 5 minutes
    pr_quest_url: "http://localhost:3000"
    github_token_path: "/var/run/secrets/github/token"
    auto_approve_threshold: 0.95  # Confidence for auto-approval
    gamification:
      enabled: true
      xp_multiplier: 1.0

integrations:
  pr_quest:
    enabled: true
    base_url: "http://pr-quest-service.pipe-system.svc.cluster.local:3000"
    timeout: 30
    llm_provider: "openai"
    llm_model: "gpt-4o-mini"
```

### 6. Helm Chart Updates

Add PR-QUEST deployment to `charts/pipe-bots/templates/deployment.yaml`:

```yaml
---
# PR-QUEST Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "pipe-bots.fullname" . }}-pr-quest
  namespace: {{ .Values.namespace }}
spec:
  replicas: {{ .Values.prQuest.replicas }}
  selector:
    matchLabels:
      app: pr-quest
  template:
    metadata:
      labels:
        app: pr-quest
    spec:
      containers:
      - name: pr-quest
        image: {{ .Values.prQuest.image.repository }}:{{ .Values.prQuest.image.tag }}
        ports:
        - containerPort: 3000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: {{ include "pipe-bots.fullname" . }}-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: pr-quest-service
  namespace: {{ .Values.namespace }}
spec:
  selector:
    app: pr-quest
  ports:
  - port: 3000
    targetPort: 3000
```

## Testing Plan

### Unit Tests

**tests/integrations/test_pr_quest_client.py:**
```python
async def test_analyze_pr():
    """Test PR analysis via PR-QUEST."""
    client = PRQuestClient("http://localhost:3000")

    # Mock PR-QUEST response
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            "clusters": [{"files": ["auth.py"], "description": "Auth changes"}],
            "risks": ["SQL injection in line 42"],
            "suggestions": ["Use parameterized queries"],
            "xp_awarded": 150
        }

        result = await client.analyze_pr("https://github.com/org/repo/pull/123")

        assert len(result.clusters) == 1
        assert "SQL injection" in result.risks[0]
        assert result.xp_awarded == 150

async def test_pr_review_bot():
    """Test PR Review Bot execution."""
    bot = PRReviewBot(event_bus, config)

    # Mock GitHub PR
    with patch.object(bot, '_get_pending_integration_prs') as mock_prs:
        mock_prs.return_value = [
            PR(url="https://github.com/org/repo/pull/123", number=123)
        ]

        await bot.execute()

        # Verify event published
        events = event_bus.get_history("pr_review_complete")
        assert len(events) == 1
        assert events[0].data["pr_url"].endswith("/pull/123")
```

### Integration Tests

**tests/integration/test_pr_quest_workflow.py:**
```python
async def test_full_pr_review_workflow():
    """Test complete PR review integration."""
    # 1. Create integration request
    governance = GovernanceManager(event_bus)
    integration_id = await governance.request_integration("BNI", "PIPE", "hub")

    # 2. Simulate PR creation
    pr_url = "https://github.com/bsw-arch/PIPE/pull/999"

    # 3. Trigger PR review
    result = await governance.review_integration_pr(integration_id, pr_url)

    # 4. Verify result stored in Cognee
    cognee_client = get_cognee_client()
    reviews = await cognee_client.search_integrations(
        f"PR review for {integration_id}",
        limit=1
    )
    assert len(reviews) == 1

    # 5. Verify governance status updated
    integration = governance.get_integration(integration_id)
    assert "pr_review" in integration
    assert integration["pr_review"]["status"] in ["APPROVE", "REJECT", "NEEDS_HUMAN_REVIEW"]
```

### Manual Testing

1. **Start PR-QUEST locally:**
   ```bash
   cd PR-QUEST
   pnpm install
   pnpm dev
   ```

2. **Configure PIPE:**
   ```bash
   export PR_QUEST_URL=http://localhost:3000
   export GITHUB_TOKEN=ghp_xxx
   ```

3. **Start PR Review Bot:**
   ```bash
   python -m src.main --bot pr_review
   ```

4. **Create test PR:**
   - Create a PR in a test repository
   - Verify PR Review Bot detects it
   - Check PR-QUEST analysis appears
   - Confirm results stored in Cognee

## Documentation Updates

### New Documents

1. **docs/PR_QUEST_INTEGRATION.md** - Complete integration guide
2. **examples/pr_quest/review_integration_pr.py** - Full workflow example
3. **examples/pr_quest/manual_review.py** - Manual PR analysis

### Updated Documents

1. **README.md** - Add PR-QUEST to tech stack and features
2. **docs/GOVERNANCE.md** - Document PR review workflow
3. **docs/OPENSPEC_GUIDE.md** - Add PR-QUEST example proposal reference

## Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| PR-QUEST Phase 0-6 incomplete | High | Medium | Use feature flags, fallback to basic diff analysis |
| LLM API costs | Medium | High | Cache aggressively, use rate limits, allow LLM-free mode |
| False positives in risk detection | Medium | Medium | Human review for all REJECT decisions |
| PR-QUEST service downtime | High | Low | Queue PRs for retry, graceful degradation |
| GitHub rate limits | Medium | Medium | Implement exponential backoff, use webhooks not polling |
| Large PR performance | Medium | Medium | Set file/line limits, lazy-load diff sections |

## Alternatives Considered

### Alternative 1: GitHub CodeQL
**Pros:** Native GitHub integration, robust security scanning
**Cons:** Limited to security, no gamification, no LLM insights

### Alternative 2: Custom LLM Review
**Pros:** Full control, no external dependencies
**Cons:** Reinventing PR-QUEST, more maintenance

### Alternative 3: Manual Review Only
**Pros:** No automation complexity
**Cons:** Slow, inconsistent, doesn't scale

### Alternative 4: SonarQube
**Pros:** Mature, comprehensive code quality
**Cons:** Heavy infrastructure, no gamification, enterprise focus

**Decision:** Proceed with PR-QUEST integration for:
- Perfect alignment with OpenSpec (same team)
- Gamification encourages governance participation
- LLM insights complement PIPE's AI memory (Cognee)
- Lightweight, modern stack matches PIPE architecture

## Success Criteria

- [ ] PR Review Bot successfully deployed and monitoring GitHub
- [ ] PR-QUEST analyzes integration PRs within 30 seconds
- [ ] 90%+ accuracy in risk detection (validated against human reviews)
- [ ] All PR reviews stored in Cognee for pattern learning
- [ ] XP leaderboard increases reviewer engagement by 50%
- [ ] Integration PRs blocked automatically if critical risks detected
- [ ] Markdown exports integrate with governance documentation
- [ ] Zero false negatives on security vulnerabilities
- [ ] Performance: Handle PRs up to 10,000 lines changed

## Open Questions

1. Should we run PR-QUEST as a separate service or embed it?
2. What confidence threshold for auto-approval?
3. Should we use PR-QUEST's cache or Cognee for caching?
4. How to handle monorepo PRs with cross-domain changes?
5. What LLM model for production (GPT-4o, Claude, local)?
6. Should we contribute governance-specific features back to PR-QUEST?

## Dependencies

### External
- ✅ PR-QUEST Phases 0-6 (completed)
- ⏳ PR-QUEST Phase 9 (caching) - Optional but beneficial
- ✅ GitHub API access with webhook support
- ✅ OpenAI API key for LLM analysis (or alternative)

### Internal
- ✅ Cognee integration (already implemented)
- ✅ EventBus for bot communication (already exists)
- ✅ GovernanceManager (already exists)
- ⏳ PRReviewDataPoint (to be added)
- ⏳ PR Review Bot (to be implemented)
- ⏳ PR-QUEST client (to be implemented)

## Breaking Changes

**None.** This is an additive change:
- New bot type (PR Review Bot)
- New integration (PR-QUEST)
- New DataPoint type (PRReviewDataPoint)
- Enhanced governance workflow (optional PR review step)

Existing bots and workflows remain unchanged.

## Rollout Plan

### Phase 1: Foundation (Week 1)
- Implement PRQuestClient
- Add PRReviewDataPoint
- Create basic PR Review Bot skeleton

### Phase 2: Core Functionality (Week 2)
- Implement PR detection and analysis
- Integrate with Cognee storage
- Add unit and integration tests

### Phase 3: Governance Integration (Week 3)
- Update GovernanceManager with PR review workflow
- Add governance status updates based on analysis
- Create comprehensive examples

### Phase 4: Production Deployment (Week 4)
- Deploy PR-QUEST service to Kubernetes
- Configure Helm charts and network policies
- Set up monitoring and alerting
- Enable PR Review Bot in production

### Phase 5: Iteration (Ongoing)
- Tune auto-approval thresholds
- Add custom risk detection rules
- Enhance Cognee pattern learning
- Gamification leaderboard UI

## References

- PR-QUEST Repository: https://github.com/Fission-AI/PR-QUEST
- PR-QUEST Roadmap: https://github.com/Fission-AI/PR-QUEST/blob/main/ROADMAP.md
- OpenSpec (same team): https://github.com/Fission-AI/OpenSpec
- PIPE Governance: `docs/GOVERNANCE.md`
- PIPE OpenSpec Specs: `openspec/specs/governance/spec.md`
- Cognee Integration: `docs/COGNEE_INTEGRATION.md`
