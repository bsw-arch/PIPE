# PR Review Bot

**Automated code review for integration PRs using LLM-powered analysis**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [Quality Gates](#quality-gates)
- [Pattern Learning](#pattern-learning)
- [Events](#events)
- [Examples](#examples)
- [API Reference](#api-reference)

---

## 🚀 Overview

The PR Review Bot automates code review for integration PRs using [PR-QUEST](https://github.com/Fission-AI/pr-quest), an LLM-powered PR review platform. It monitors GitHub repositories, analyzes PRs using advanced clustering and risk detection, enforces quality gates, and learns from review patterns to improve over time.

### Why PR Review Bot?

- **🚀 Faster Reviews**: Automated analysis provides instant feedback
- **🔍 Deep Analysis**: LLM-powered clustering identifies logical groups of changes
- **🛡️ Security First**: Detects security vulnerabilities and breaking changes
- **📚 Pattern Learning**: Learns from historical reviews using Cognee AI memory
- **🎮 Gamification**: Rewards developers with XP for quality PRs
- **✅ Quality Gates**: Enforces consistent review standards

---

## ✨ Features

### Core Capabilities

#### 1. Automated PR Monitoring
- Monitors GitHub repositories for new PRs
- Identifies integration PRs by labels, title, or modified files
- Queues PRs for automated analysis

#### 2. LLM-Powered Analysis (PR-QUEST)
- **Code Clustering**: Groups related changes by logical functionality
- **Risk Detection**: Identifies security vulnerabilities, breaking changes, anti-patterns
- **Smart Suggestions**: Provides actionable improvement recommendations
- **Context Understanding**: Uses LLM (GPT-4o-mini or custom) to understand code semantics

#### 3. Quality Gate Enforcement
- **Auto-Approve**: Clean PRs with no/low risk → automatic approval
- **Flag for Review**: Moderate risk → human review required
- **Reject**: Critical risks → changes requested

#### 4. Pattern Learning
- Stores review decisions in Cognee for AI memory
- Learns from human overrides to improve future decisions
- Queries historical patterns to inform current reviews

#### 5. Developer Experience
- Posts detailed review comments on GitHub
- Applies labels for workflow automation
- Awards XP for gamification
- Requests human reviewers when needed

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PR Review Bot                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐       ┌────────────────┐            │
│  │   GitHub     │──────▶│  PR Monitor    │            │
│  │  Webhooks    │       │   (Polling)    │            │
│  └──────────────┘       └────────┬───────┘            │
│                                   │                     │
│                                   ▼                     │
│                         ┌─────────────────┐            │
│                         │  PR Queue       │            │
│                         └────────┬────────┘            │
│                                  │                      │
│                                  ▼                      │
│  ┌────────────────────────────────────────────────┐   │
│  │           PR-QUEST Analysis                    │   │
│  │  ┌──────────────┐  ┌───────────────────────┐  │   │
│  │  │LLM Clustering│  │Risk Detection         │  │   │
│  │  │(GPT-4o-mini) │  │- Security             │  │   │
│  │  │              │  │- Breaking changes     │  │   │
│  │  │              │  │- Anti-patterns        │  │   │
│  │  └──────────────┘  └───────────────────────┘  │   │
│  └────────────────────┬───────────────────────────┘   │
│                       │                                │
│                       ▼                                │
│            ┌──────────────────────┐                   │
│            │  Quality Gates       │                   │
│            │  - Auto-approve      │                   │
│            │  - Flag for review   │                   │
│            │  - Reject            │                   │
│            └──────────┬───────────┘                   │
│                       │                                │
│         ┌─────────────┴─────────────┐                 │
│         ▼                           ▼                  │
│  ┌──────────────┐         ┌─────────────────┐        │
│  │   Cognee     │         │  GitHub Actions │        │
│  │  AI Memory   │         │  - Post comment │        │
│  │  (Learning)  │         │  - Apply labels │        │
│  │              │         │  - Request review│       │
│  └──────────────┘         └─────────────────┘        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Data Flow

1. **PR Creation** → GitHub webhook or polling detects new PR
2. **PR Classification** → Bot identifies integration PRs
3. **Queue** → PR added to review queue
4. **Analysis** → PR-QUEST performs LLM-powered analysis
5. **Quality Gates** → Decision made based on risk level
6. **Action** → Comment posted, labels applied, reviewers requested
7. **Learning** → Review stored in Cognee for pattern learning

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export GITHUB_TOKEN="ghp_your_github_personal_access_token"

# Optional
export PR_QUEST_URL="http://pr-quest:8000"  # Default: http://pr-quest:8000
```

### Bot Configuration (config.yaml)

```yaml
bots:
  pr_review:
    enabled: true
    check_interval: 60  # Check for new PRs every 60 seconds
    log_level: "INFO"

    # GitHub configuration
    github_token: "${GITHUB_TOKEN}"
    monitored_repositories:
      - "bsw-arch/PIPE"
      - "your-org/your-repo"

    # PR-QUEST service
    pr_quest_url: "http://pr-quest:8000"
    llm_model: "gpt-4o-mini"  # or "gpt-4", "claude-3-sonnet", etc.

    # Quality gate thresholds
    auto_approve_threshold: "NONE"      # Auto-approve if risk is NONE
    flag_review_threshold: "MODERATE"   # Flag for human review if MODERATE
    reject_threshold: "CRITICAL"        # Reject if CRITICAL

    # Human reviewers to request when flagging
    human_reviewers:
      - "senior-dev"
      - "tech-lead"

    # Pattern learning
    enable_pattern_learning: true
    pattern_refresh_interval: 3600  # Refresh patterns every hour
```

---

## 📖 Usage

### Running the Bot

#### Basic Usage

```python
import asyncio
from src.bots.pr_review_bot import PRReviewBot
from src.core.event_bus import EventBus
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector

config = {
    "github_token": "your_token",
    "monitored_repositories": ["owner/repo"],
    "pr_quest_url": "http://pr-quest:8000",
    "llm_model": "gpt-4o-mini",
}

bot = PRReviewBot(
    name="pr_review_bot",
    config=config,
    event_bus=EventBus(),
    state_manager=StateManager(state_dir="./state"),
    metrics=MetricsCollector(),
)

await bot.start()
```

#### With Event Listeners

```python
async def on_review_complete(event):
    print(f"Review complete: {event.data['decision']}")
    print(f"Risk level: {event.data['risk_level']}")

event_bus.subscribe("pr_review.complete", on_review_complete)
```

### Manual PR Review

Trigger a review manually for testing:

```python
# See examples/pr_review_bot/manual_pr_review.py
python examples/pr_review_bot/manual_pr_review.py
```

---

## 🚦 Quality Gates

### Decision Flow

```
PR Analysis
    ├─ Risk: NONE
    │   ├─ Suggestions ≤ 3 → AUTO_APPROVED
    │   └─ Suggestions > 3 → APPROVED_WITH_SUGGESTIONS
    │
    ├─ Risk: LOW
    │   └─ → APPROVED_WITH_SUGGESTIONS
    │
    ├─ Risk: MODERATE
    │   └─ → FLAGGED_FOR_REVIEW (human review required)
    │
    └─ Risk: CRITICAL
        ├─ Security risk → REJECTED_SECURITY
        ├─ Breaking changes → REJECTED_BREAKING_CHANGES
        └─ Other critical → REJECTED_CRITICAL_RISK
```

### Decision Types

#### 1. AUTO_APPROVED ✅
- **Risk Level**: NONE
- **Conditions**: Clean code, no risks, few suggestions
- **Actions**:
  - Post approval comment
  - Apply `auto-approved` and `ready-to-merge` labels
  - Award XP

#### 2. APPROVED_WITH_SUGGESTIONS ✅
- **Risk Level**: NONE or LOW
- **Conditions**: Low risk but has improvement suggestions
- **Actions**:
  - Post approval with suggestions
  - Apply `approved-with-suggestions` label
  - Award XP

#### 3. FLAGGED_FOR_REVIEW ⚠️
- **Risk Level**: MODERATE
- **Conditions**: Moderate risk detected
- **Actions**:
  - Post analysis with concerns
  - Apply `needs-review` and `moderate-risk` labels
  - Request human reviewers
  - Award reduced XP

#### 4. REJECTED_SECURITY ❌
- **Risk Level**: CRITICAL
- **Conditions**: Security vulnerability detected
- **Actions**:
  - Post rejection with security details
  - Apply `changes-requested` and `critical-risk` labels
  - Block merge
  - No XP

#### 5. REJECTED_BREAKING_CHANGES ❌
- **Risk Level**: CRITICAL
- **Conditions**: Breaking API/interface changes
- **Actions**:
  - Post rejection with breaking change details
  - Apply `changes-requested` and `breaking-changes` labels
  - Block merge
  - No XP

#### 6. REJECTED_CRITICAL_RISK ❌
- **Risk Level**: CRITICAL
- **Conditions**: Other critical risks
- **Actions**:
  - Post rejection with risk details
  - Apply `changes-requested` and `critical-risk` labels
  - Block merge
  - No XP

---

## 🧠 Pattern Learning

The PR Review Bot uses Cognee AI memory to learn from review history and improve decisions over time.

### What Gets Learned?

1. **PR Review Decisions**: All automated review decisions
2. **Risk Patterns**: Common risk patterns across PRs
3. **Human Overrides**: When humans disagree with bot decisions
4. **Code Clusters**: Recurring logical groupings of changes

### How Learning Works

```python
# 1. Store review in Cognee
datapoint = create_pr_review_datapoint(
    pr_url="...",
    analysis_id="...",
    clusters=[...],
    risks=[...],
    decision="auto_approved",
    reviewer="pr_review_bot",
)
await add(datapoint)
await cognify()

# 2. Query patterns for future reviews
patterns = await search(
    "What patterns exist in PR reviews?",
    search_type="insights"
)

# 3. Learn from human overrides
if bot_decision != human_decision:
    await add({
        "type": "review_override",
        "bot_decision": bot_decision,
        "human_decision": human_decision,
        "notes": "Why human disagreed",
    })
```

### Pattern Cache

The bot maintains a pattern cache refreshed hourly:

```python
{
    "loaded_at": "2025-11-18T10:00:00",
    "patterns": [
        "Security reviews for auth changes require 2+ reviewers",
        "DB schema changes flagged 80% of time",
        "PRs with >10 files usually need manual review",
    ]
}
```

---

## 📡 Events

### Events Published

#### `pr_review.queued`
PR added to review queue.

```python
{
    "repo": "owner/repo",
    "pr_number": 123,
    "pr_url": "https://github.com/...",
    "title": "Add feature X",
    "author": "developer1",
    "status": "queued",
}
```

#### `pr_review.complete`
Review analysis completed.

```python
{
    "pr_key": "owner/repo#123",
    "pr_url": "https://github.com/...",
    "analysis_id": "abc123",
    "decision": "auto_approved",
    "risk_level": "NONE",
    "clusters": 3,
    "risks": 0,
    "xp_awarded": 150,
}
```

#### `pr_review.metrics`
Review metrics published.

```python
{
    "total_reviews": 42,
    "pending_reviews": 2,
    "decisions": {
        "auto_approved": 30,
        "flagged_for_review": 8,
        "rejected_security": 2,
    },
}
```

### Events Subscribed

#### `integration.pr_created`
New integration PR detected.

```python
{
    "repository": "owner/repo",
    "pr_number": 123,
}
```

#### `integration.pr_updated`
PR updated (triggers re-review).

```python
{
    "repository": "owner/repo",
    "pr_number": 123,
}
```

#### `pr_review.human_decision`
Human override of bot decision.

```python
{
    "pr_key": "owner/repo#123",
    "decision": "approved",  # Human decision
    "notes": "Looks good despite moderate risk",
}
```

---

## 📚 Examples

### Example 1: Run PR Review Bot

See `examples/pr_review_bot/run_pr_review_bot.py`:

```bash
export GITHUB_TOKEN="your_token"
python examples/pr_review_bot/run_pr_review_bot.py
```

### Example 2: Manual PR Review

See `examples/pr_review_bot/manual_pr_review.py`:

```bash
python examples/pr_review_bot/manual_pr_review.py
```

Choose from:
1. Trigger manual PR review
2. Simulate PR workflow
3. Demonstrate quality gates

### Example 3: Integration with Cognee

See `examples/pr_quest/review_integration_pr.py` for complete workflow:

```python
# Review PR and store in Cognee
result = await pr_quest.analyze_pr(pr_url)
datapoint = create_pr_review_datapoint(...)
await add(datapoint)
await cognify()

# Query for similar reviews
similar = await search("PRs with authentication changes")
```

---

## 🔧 API Reference

### PRReviewBot

```python
class PRReviewBot(BotBase):
    """
    Bot for automated PR code review using PR-QUEST.

    Monitors GitHub repositories for integration PRs, analyzes them using
    PR-QUEST's LLM-powered clustering and risk detection, enforces quality
    gates, and learns from historical review decisions.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector,
    ):
        """Initialize the PR review bot."""

    async def initialize() -> bool:
        """Initialize the PR review bot."""

    async def execute() -> None:
        """Main execution loop."""

    async def cleanup() -> None:
        """Clean up resources."""
```

### ReviewDecision

```python
class ReviewDecision(str, Enum):
    """PR review decision outcomes."""

    AUTO_APPROVED = "auto_approved"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    REJECTED_CRITICAL_RISK = "rejected_critical_risk"
    REJECTED_SECURITY = "rejected_security"
    REJECTED_BREAKING_CHANGES = "rejected_breaking_changes"
    APPROVED_WITH_SUGGESTIONS = "approved_with_suggestions"
    PENDING_HUMAN_REVIEW = "pending_human_review"
```

### Key Methods

#### `_is_integration_pr(pr: PullRequest) -> bool`
Determine if a PR is an integration PR by checking:
- Labels (e.g., "integration", "external-integration")
- Title keywords (e.g., "integration", "integrate", "connect")
- Modified files (e.g., `src/integrations/`, `connectors/`)

#### `_apply_quality_gates(pr_info, analysis) -> ReviewDecision`
Apply quality gates based on risk level and analysis results.

#### `_format_review_comment(analysis, decision) -> str`
Format a GitHub comment with analysis results in markdown.

#### `_store_review_in_cognee(pr_info, analysis, decision) -> None`
Store PR review in Cognee for pattern learning.

---

## 🎯 Best Practices

### 1. Configure Quality Gates Appropriately
Adjust thresholds based on your team's risk tolerance:

```yaml
# Strict (security-critical projects)
auto_approve_threshold: "NONE"
flag_review_threshold: "LOW"
reject_threshold: "MODERATE"

# Balanced (most projects)
auto_approve_threshold: "NONE"
flag_review_threshold: "MODERATE"
reject_threshold: "CRITICAL"

# Relaxed (internal tools)
auto_approve_threshold: "LOW"
flag_review_threshold: "CRITICAL"
reject_threshold: "CRITICAL"
```

### 2. Monitor Bot Performance
Track metrics to ensure the bot is helping:

```python
metrics = {
    "auto_approval_rate": "60%",  # Target: 50-70%
    "false_positive_rate": "5%",  # Target: <10%
    "human_override_rate": "8%",  # Target: <15%
}
```

### 3. Provide Feedback
Use human decision events to teach the bot:

```python
await event_bus.publish(Event(
    event_type="pr_review.human_decision",
    data={
        "pr_key": "owner/repo#123",
        "decision": "approved",
        "notes": "Test coverage looks good despite complexity",
    }
))
```

### 4. Review Bot Comments
Periodically review the bot's GitHub comments to ensure:
- Comments are helpful and actionable
- Risk detection is accurate
- Suggestions are relevant

---

## 🐛 Troubleshooting

### Bot Not Finding PRs

**Symptoms**: Bot runs but doesn't queue any PRs

**Solutions**:
1. Check `monitored_repositories` configuration
2. Verify GitHub token has repo access
3. Check PR meets integration criteria (labels, title, files)
4. Enable DEBUG logging to see PR detection logic

### PR-QUEST Connection Errors

**Symptoms**: "PR-QUEST is not healthy" warnings

**Solutions**:
1. Verify PR-QUEST service is running: `curl http://pr-quest:8000/health`
2. Check `pr_quest_url` configuration
3. Ensure PR-QUEST API key is set (if required)

### Cognee Storage Errors

**Symptoms**: "Error storing review in Cognee"

**Solutions**:
1. Verify Cognee is initialized: `cognee.config()`
2. Check Cognee backend connectivity (LanceDB, NetworkX)
3. Review Cognee logs for detailed errors

### Human Review Not Requested

**Symptoms**: PRs not requesting human reviewers when flagged

**Solutions**:
1. Check `human_reviewers` list contains valid GitHub usernames
2. Verify bot token has permission to request reviewers
3. Check if reviewers have repo access

---

## 📈 Metrics

The bot tracks the following metrics:

```python
# Reviews
pr_review.queued              # PRs queued for review
pr_review.requeued            # PRs re-queued after update
pr_review.errors              # Review processing errors

# Decisions
pr_review.decision.auto_approved
pr_review.decision.flagged_for_review
pr_review.decision.rejected_security
pr_review.decision.rejected_breaking_changes
pr_review.decision.rejected_critical_risk
pr_review.decision.approved_with_suggestions

# Risk Levels
pr_review.risk_level.NONE
pr_review.risk_level.LOW
pr_review.risk_level.MODERATE
pr_review.risk_level.CRITICAL

# Learning
pr_review.cognee_stored       # Reviews stored in Cognee
pr_review.cognee_errors       # Cognee storage errors
pr_review.human_override      # Human overrides of bot decisions

# GitHub
pr_review.github_errors       # GitHub API errors

# Gauges
pr_review.pending_count       # Current pending reviews
pr_review.total_reviews       # Total reviews completed
```

---

## 🔗 Related Documentation

- [OpenSpec Specifications](../openspec/specs/)
- [PR-QUEST Integration](../examples/pr_quest/)
- [Cognee AI Memory](COGNEE.md)
- [Governance Architecture](GOVERNANCE.md)
- [Change Proposal: PR-QUEST Integration](../openspec/changes/add-pr-quest-integration/proposal.md)

---

## 📝 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Questions?** See the [examples](../examples/pr_review_bot/) or check the [OpenSpec specifications](../openspec/specs/bots/spec.md).
