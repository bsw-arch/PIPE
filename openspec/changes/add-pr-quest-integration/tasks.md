# Implementation Tasks: PR-QUEST Integration

This document outlines all tasks required to implement PR-QUEST integration for PIPE.

## 1. Foundation & Dependencies

### 1.1 Update Project Dependencies
- [ ] Add `aiohttp>=3.9.0` to requirements.txt (for async HTTP)
- [ ] Add `pydantic>=2.0.0` (already present, verify version)
- [ ] Add `PyGithub>=2.0.0` for GitHub API interaction
- [ ] Add `python-dotenv>=1.0.0` for local development
- [ ] Update requirements.txt with PR-QUEST specific needs
- [ ] Run `pip install -r requirements.txt` and verify no conflicts

### 1.2 Environment Configuration
- [ ] Add `GITHUB_TOKEN` to `.env.example`
- [ ] Add `PR_QUEST_URL` to `.env.example`
- [ ] Add `OPENAI_API_KEY` to `.env.example` (for PR-QUEST LLM features)
- [ ] Document required GitHub token scopes (`repo`, `read:org`)
- [ ] Create `.env.template` for local development

### 1.3 Update Configuration Schema
- [ ] Add `pr_review` section to `config/config.yaml`
- [ ] Define configuration schema for PR Review Bot
- [ ] Add PR-QUEST integration config
- [ ] Add auto-approval threshold setting
- [ ] Add gamification enable/disable flag
- [ ] Update `src/config/config_loader.py` to load new config

---

## 2. PR-QUEST Client Implementation

### 2.1 Create PR-QUEST Client Module
- [ ] Create `src/integrations/pr_quest_client.py`
- [ ] Define `PRQuestClient` class with async methods
- [ ] Implement `__init__()` with base_url and session management
- [ ] Add proper type hints for all methods
- [ ] Add comprehensive docstrings (Google style)

### 2.2 Core Client Methods
- [ ] Implement `analyze_pr(pr_url: str, include_llm_analysis: bool) -> PRAnalysisResult`
  - POST to /api/analyze
  - Handle response parsing
  - Error handling for invalid URLs
  - Timeout configuration
- [ ] Implement `get_review_steps(analysis_id: str) -> List[ReviewStep]`
  - GET /api/results/{analysis_id}/steps
  - Parse step data
- [ ] Implement `submit_review_notes(analysis_id: str, notes: List[ReviewNote]) -> bool`
  - POST notes for specific PR sections
  - Validate note structure
- [ ] Implement `export_markdown(analysis_id: str) -> str`
  - GET /api/export/{analysis_id}
  - Return formatted markdown
- [ ] Implement `get_xp_leaderboard() -> List[ReviewerXP]`
  - GET /api/leaderboard
  - Parse XP data

### 2.3 Data Models
- [ ] Create `src/integrations/pr_quest_models.py`
- [ ] Define `PRAnalysisResult` dataclass
  - analysis_id: str
  - clusters: List[CodeCluster]
  - risks: List[Risk]
  - risk_level: RiskLevel
  - suggestions: List[str]
  - xp_awarded: int
- [ ] Define `CodeCluster` dataclass
- [ ] Define `Risk` dataclass with severity levels
- [ ] Define `ReviewStep`, `ReviewNote`, `ReviewerXP` dataclasses
- [ ] Add Pydantic validation for all models

### 2.4 Client Utilities
- [ ] Implement connection pooling with aiohttp
- [ ] Add retry logic with exponential backoff
- [ ] Implement request/response logging
- [ ] Add metrics collection (request count, latency, errors)
- [ ] Create singleton factory: `get_pr_quest_client()`

---

## 3. Governance DataPoint Extension

### 3.1 Add PRReviewDataPoint
- [ ] Open `src/governance/datapoints.py`
- [ ] Add `PRReviewDataPoint` class extending `DataPoint`
- [ ] Define all required fields (see spec-changes.md)
- [ ] Add `metadata = {"index_fields": ["risks", "suggestions", "decision"]}`
- [ ] Add validation for risk_level enum
- [ ] Add validation for decision enum
- [ ] Add helper methods:
  - `is_approved() -> bool`
  - `requires_human_review() -> bool`
  - `has_critical_risks() -> bool`

### 3.2 Update Existing DataPoints
- [ ] Add `pr_review_id: Optional[str]` to `IntegrationDataPoint`
- [ ] Add link from integration to its PR review
- [ ] Ensure backward compatibility

---

## 4. PR Review Bot Implementation

### 4.1 Create PR Review Bot Class
- [ ] Create `src/bots/pr_review_bot.py`
- [ ] Define `PRReviewBot` class extending `BotBase`
- [ ] Implement `__init__()` with dependencies
- [ ] Add initialization for:
  - PRQuestClient
  - CogneeClient
  - GitHub API client
  - EventBus subscriptions

### 4.2 Bot Lifecycle Methods
- [ ] Implement `async def initialize() -> bool`
  - Verify PR-QUEST connectivity
  - Authenticate with GitHub
  - Load configuration
  - Subscribe to events
- [ ] Implement `async def execute() -> None`
  - Main loop: check for pending PRs
  - Analyze each PR
  - Store results
  - Update governance
- [ ] Implement `async def cleanup() -> None`
  - Close HTTP sessions
  - Save state
  - Unsubscribe from events

### 4.3 PR Detection Logic
- [ ] Implement `_get_pending_integration_prs() -> List[PR]`
  - Query GitHub for open PRs
  - Filter by integration labels
  - Check if already analyzed
  - Return list of PRs needing review
- [ ] Implement webhook handler (optional):
  - Listen for GitHub PR events
  - Trigger immediate analysis
  - More efficient than polling

### 4.4 PR Analysis Workflow
- [ ] Implement `async def analyze_pr(pr: PR) -> PRAnalysisResult`
  - Send to PR-QUEST
  - Wait for analysis
  - Parse results
  - Handle errors gracefully
- [ ] Implement `_determine_decision(analysis: PRAnalysisResult) -> str`
  - Apply decision logic
  - Check confidence thresholds
  - Return APPROVE/REJECT/NEEDS_REVIEW
- [ ] Implement `_generate_rationale(analysis: PRAnalysisResult) -> str`
  - Format LLM suggestions
  - List detected risks
  - Provide actionable feedback

### 4.5 Cognee Integration
- [ ] Implement `async def store_review_in_cognee(review_dp: PRReviewDataPoint)`
  - Add PRReviewDataPoint to Cognee
  - Cognify to build knowledge graph
  - Link to related integration
- [ ] Implement `async def search_similar_reviews(pr: PR) -> List[PRReviewDataPoint]`
  - Semantic search in Cognee
  - Find past similar PRs
  - Extract learned patterns

### 4.6 Governance Updates
- [ ] Implement `async def update_governance_status(pr: PR, analysis: PRAnalysisResult)`
  - Get integration by PR URL
  - Update integration status
  - Add pr_review metadata
  - Publish events

### 4.7 Event Publishing
- [ ] Publish `pr_detected` event when new PR found
- [ ] Publish `pr_review_started` event when analysis begins
- [ ] Publish `pr_review_complete` event with results
- [ ] Publish `integration_approved` event for auto-approvals
- [ ] Publish `integration_flagged` event for issues

---

## 5. Governance Manager Updates

### 5.1 Add PR Review Methods
- [ ] Open `src/governance/governance_manager.py`
- [ ] Add `async def review_integration_pr(integration_id: str, pr_url: str) -> ReviewResult`
  - Get PR Review Bot instance
  - Trigger analysis
  - Update integration record
  - Return review result
- [ ] Add `async def override_pr_rejection(integration_id: str, justification: str) -> bool`
  - Validate human override
  - Log in Cognee
  - Update integration status
  - Notify stakeholders

### 5.2 Update Integration Workflow
- [ ] Modify `request_integration()` to accept optional `pr_url`
- [ ] Add PR review as step in integration approval
- [ ] Update integration status enum:
  - Add "UNDER_PR_REVIEW"
  - Add "REJECTED_CODE_ISSUES"
  - Add "APPROVED_WITH_OVERRIDE"
- [ ] Handle PR review results in approval workflow

### 5.3 Quality Gates Implementation
- [ ] Implement security vulnerability gate
- [ ] Implement breaking change detection gate
- [ ] Implement anti-pattern detection gate
- [ ] Add configurable gate thresholds
- [ ] Allow domain-specific gate customization

---

## 6. Infrastructure & Deployment

### 6.1 PR-QUEST Service Deployment
- [ ] Create `infrastructure/pr-quest/` directory
- [ ] Add Dockerfile for PR-QUEST (reference upstream)
- [ ] Create Kubernetes deployment manifest
- [ ] Create Kubernetes service manifest
- [ ] Add OpenBao secret for OPENAI_API_KEY
- [ ] Configure resource limits (1Gi memory, 500m CPU)

### 6.2 Helm Chart Updates
- [ ] Update `charts/pipe-bots/values.yaml`:
  - Add `prQuest` section
  - Define image repository and tag
  - Set replicas and resources
- [ ] Update `charts/pipe-bots/templates/deployment.yaml`:
  - Add PR-QUEST deployment
  - Mount secrets from OpenBao
  - Configure environment variables
- [ ] Create `charts/pipe-bots/templates/pr-quest-service.yaml`
  - Expose port 3000
  - Configure ClusterIP service
- [ ] Update `charts/pipe-bots/templates/_helpers.tpl` if needed

### 6.3 Cilium Network Policies
- [ ] Add network policy for PR-QUEST service
- [ ] Allow PR Review Bot → PR-QUEST traffic
- [ ] Allow PR-QUEST → GitHub API traffic
- [ ] Allow PR-QUEST → OpenAI API traffic
- [ ] Block all other ingress/egress

### 6.4 OpenTofu Updates
- [ ] Update `infrastructure/opentofu/main.tf`:
  - Add PR-QUEST namespace resources
  - Add RBAC for PR-QUEST service account
- [ ] Update `infrastructure/opentofu/variables.tf`:
  - Add pr_quest_image variable
  - Add openai_api_key_path variable

### 6.5 Ansible Playbooks
- [ ] Update `infrastructure/ansible/deploy-pipe.yml`:
  - Add PR-QUEST deployment task
  - Verify PR-QUEST health after deployment
- [ ] Add `infrastructure/ansible/verify-pr-quest.yml`:
  - Check PR-QUEST service accessibility
  - Verify LLM integration
  - Test sample PR analysis

---

## 7. Testing

### 7.1 Unit Tests - PRQuestClient
- [ ] Create `tests/integrations/test_pr_quest_client.py`
- [ ] Test `analyze_pr()` with mocked HTTP responses
- [ ] Test `get_review_steps()` parsing
- [ ] Test `export_markdown()` formatting
- [ ] Test error handling (404, 500, timeout)
- [ ] Test retry logic
- [ ] Achieve >80% code coverage

### 7.2 Unit Tests - PR Review Bot
- [ ] Create `tests/bots/test_pr_review_bot.py`
- [ ] Test bot initialization
- [ ] Test PR detection logic
- [ ] Test `_determine_decision()` with various analysis results
- [ ] Test Cognee storage
- [ ] Test event publishing
- [ ] Mock all external dependencies

### 7.3 Unit Tests - Governance Integration
- [ ] Create `tests/governance/test_pr_review_workflow.py`
- [ ] Test `review_integration_pr()`
- [ ] Test `override_pr_rejection()`
- [ ] Test quality gates
- [ ] Test integration status updates

### 7.4 Integration Tests
- [ ] Create `tests/integration/test_pr_quest_integration.py`
- [ ] Test full PR review workflow:
  - Create test PR
  - Trigger bot analysis
  - Verify PR-QUEST called
  - Check Cognee storage
  - Validate governance update
- [ ] Test with real PR-QUEST instance (local)
- [ ] Test fallback mode when PR-QUEST unavailable

### 7.5 E2E Tests
- [ ] Create `tests/e2e/test_pr_review_e2e.py`
- [ ] Test scenario: Clean PR → Auto-approval
- [ ] Test scenario: Risky PR → Human review
- [ ] Test scenario: Critical risks → Auto-reject
- [ ] Test scenario: Human override
- [ ] Run against full stack (Kubernetes + PR-QUEST + PIPE)

### 7.6 Performance Tests
- [ ] Test PR analysis time (<30s target)
- [ ] Test concurrent PR reviews (10 PRs simultaneously)
- [ ] Test large PR handling (10,000+ lines changed)
- [ ] Measure LLM API costs
- [ ] Test cache effectiveness

---

## 8. Documentation

### 8.1 Integration Guide
- [ ] Create `docs/PR_QUEST_INTEGRATION.md`
- [ ] Document architecture and workflow
- [ ] Explain PR Review Bot configuration
- [ ] Document quality gates
- [ ] Add troubleshooting section
- [ ] Include cost estimation guide

### 8.2 API Documentation
- [ ] Document PRQuestClient methods
- [ ] Add API reference to main docs
- [ ] Include code examples
- [ ] Document error codes
- [ ] Add retry logic explanation

### 8.3 Examples
- [ ] Create `examples/pr_quest/review_integration_pr.py`
  - Full workflow example
  - Show manual trigger
  - Display results
- [ ] Create `examples/pr_quest/manual_review.py`
  - Direct PR-QUEST usage
  - Export markdown example
- [ ] Create `examples/pr_quest/pattern_learning.py`
  - Show Cognee integration
  - Demonstrate historical search

### 8.4 README Updates
- [ ] Add PR-QUEST to technology stack
- [ ] Add PR Review Bot to bot types section
- [ ] Update architecture diagram
- [ ] Add PR-QUEST integration example
- [ ] Link to full documentation

### 8.5 OpenSpec Documentation
- [ ] Update `docs/OPENSPEC_GUIDE.md` with PR-QUEST example
- [ ] Reference this change proposal as best practice
- [ ] Add to examples list

---

## 9. Configuration & Secrets

### 9.1 OpenBao Secrets
- [ ] Store GitHub token in OpenBao
  - Path: `secret/data/pipe/github-token`
  - Scopes: `repo`, `read:org`
- [ ] Store OpenAI API key in OpenBao
  - Path: `secret/data/pipe/openai-api-key`
  - For PR-QUEST LLM features
- [ ] Update deployment to mount secrets
- [ ] Test secret rotation

### 9.2 Zitadel Configuration
- [ ] Create service account for PR Review Bot
- [ ] Grant GitHub API permissions
- [ ] Grant PR-QUEST API permissions
- [ ] Configure OAuth2 flow if needed

### 9.3 Configuration Templates
- [ ] Create `config/pr_review.example.yaml`
- [ ] Document all configuration options
- [ ] Provide production-ready defaults
- [ ] Add development overrides

---

## 10. Monitoring & Observability

### 10.1 Metrics
- [ ] Add Prometheus metrics for PR Review Bot:
  - `pr_reviews_total` (counter)
  - `pr_review_duration_seconds` (histogram)
  - `pr_review_decisions` (counter by decision type)
  - `pr_quest_api_errors` (counter)
  - `pr_review_xp_awarded` (counter)
- [ ] Expose metrics endpoint on PR Review Bot

### 10.2 Logging
- [ ] Add structured logging to PR Review Bot
- [ ] Log PR analysis start/complete
- [ ] Log decision rationale
- [ ] Log errors with context
- [ ] Use correlation IDs for tracing

### 10.3 Alerting
- [ ] Create alert: PR-QUEST service down
- [ ] Create alert: PR review taking >5 minutes
- [ ] Create alert: High false positive rate
- [ ] Create alert: LLM API quota exceeded
- [ ] Configure PagerDuty/Slack integration

### 10.4 Dashboards
- [ ] Create Grafana dashboard for PR reviews
- [ ] Show PR review pipeline metrics
- [ ] Display XP leaderboard
- [ ] Graph decision distribution
- [ ] Track cost (LLM API usage)

---

## 11. Security & Compliance

### 11.1 Security Review
- [ ] Review GitHub token permissions (least privilege)
- [ ] Audit PR-QUEST access to OpenAI API
- [ ] Validate no sensitive data sent to LLM
- [ ] Implement rate limiting on PR-QUEST API
- [ ] Add input validation for PR URLs

### 11.2 Compliance
- [ ] Document data retention for PR reviews
- [ ] Add GDPR compliance notes (if applicable)
- [ ] Review PII handling in code diffs
- [ ] Add data export capability
- [ ] Document third-party data sharing (OpenAI)

---

## 12. Rollout & Migration

### 12.1 Feature Flags
- [ ] Add `feature.pr_review_bot.enabled` flag
- [ ] Add `feature.pr_review_auto_approve.enabled` flag
- [ ] Add `feature.pr_review_llm.enabled` flag
- [ ] Add per-domain override flags
- [ ] Implement graceful degradation

### 12.2 Gradual Rollout
- [ ] Phase 1: Deploy PR-QUEST (no bot)
  - Verify service works
  - Test manual API calls
- [ ] Phase 2: Enable bot in monitoring mode
  - Analyze PRs but don't take action
  - Collect metrics
  - Tune thresholds
- [ ] Phase 3: Enable auto-flagging
  - Block risky PRs
  - Still require human approval for all
- [ ] Phase 4: Enable auto-approval
  - Auto-approve clean PRs
  - Monitor for false negatives
- [ ] Phase 5: Full production
  - All features enabled
  - Continuous improvement

### 12.3 Rollback Plan
- [ ] Document rollback procedure
- [ ] Disable PR Review Bot via config
- [ ] Revert to manual PR review
- [ ] Keep PR-QUEST data for analysis
- [ ] No data loss on rollback

---

## 13. Final Validation

### 13.1 Acceptance Criteria
- [ ] All unit tests pass (>80% coverage)
- [ ] All integration tests pass
- [ ] E2E tests demonstrate full workflow
- [ ] Documentation complete and reviewed
- [ ] Security review approved
- [ ] Performance benchmarks met
- [ ] Stakeholder demo successful

### 13.2 Production Readiness
- [ ] PR-QUEST service healthy in production
- [ ] PR Review Bot running and processing PRs
- [ ] Monitoring dashboards live
- [ ] Alerts configured and tested
- [ ] Runbook created for on-call
- [ ] Team training completed

### 13.3 Post-Deployment
- [ ] Monitor for 1 week
- [ ] Collect user feedback
- [ ] Tune auto-approval threshold
- [ ] Analyze LLM costs
- [ ] Plan improvements for next iteration

---

## Task Summary

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| 1. Foundation | 6 tasks | 4 hours |
| 2. PR-QUEST Client | 12 tasks | 16 hours |
| 3. DataPoint Extension | 4 tasks | 4 hours |
| 4. PR Review Bot | 20 tasks | 24 hours |
| 5. Governance Updates | 9 tasks | 12 hours |
| 6. Infrastructure | 15 tasks | 16 hours |
| 7. Testing | 18 tasks | 20 hours |
| 8. Documentation | 13 tasks | 12 hours |
| 9. Configuration | 9 tasks | 6 hours |
| 10. Monitoring | 12 tasks | 8 hours |
| 11. Security | 7 tasks | 8 hours |
| 12. Rollout | 11 tasks | 12 hours |
| 13. Validation | 10 tasks | 8 hours |
| **Total** | **146 tasks** | **~150 hours** |

---

**Estimated Timeline:** 4-5 weeks for full implementation with 1 engineer

**Critical Path:**
1. PR-QUEST Client (blocks everything)
2. PR Review Bot (core functionality)
3. Governance Integration (connects to existing workflow)
4. Testing (ensures quality)
5. Deployment (enables production use)

**Parallel Workstreams:**
- Documentation can be written alongside implementation
- Infrastructure can be prepared while code is being developed
- Monitoring setup can happen in parallel with testing

---

**Last Updated:** 2025-01-17
**Status:** Ready for implementation
**Related Files:**
- `proposal.md` - Full proposal document
- `spec-changes.md` - Specification updates
