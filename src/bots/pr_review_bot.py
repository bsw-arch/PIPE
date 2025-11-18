"""PR Review Bot for automated code review using PR-QUEST.

Implements automated code review for integration PRs using PR-QUEST's
LLM-powered clustering, risk detection, and pattern learning capabilities.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from github import Github, PullRequest
from github.GithubException import GithubException

from ..core.bot_base import BotBase
from ..core.event_bus import Event, EventBus
from ..core.state_manager import StateManager
from ..utils.metrics import MetricsCollector
from ..integrations.pr_quest_client import PRQuestClient
from ..integrations.pr_quest_models import RiskLevel, PRAnalysisResult
from ..governance.datapoints import create_pr_review_datapoint
from cognee import add, cognify, search


class ReviewDecision(str, Enum):
    """PR review decision outcomes."""

    AUTO_APPROVED = "auto_approved"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    REJECTED_CRITICAL_RISK = "rejected_critical_risk"
    REJECTED_SECURITY = "rejected_security"
    REJECTED_BREAKING_CHANGES = "rejected_breaking_changes"
    APPROVED_WITH_SUGGESTIONS = "approved_with_suggestions"
    PENDING_HUMAN_REVIEW = "pending_human_review"


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
        """
        Initialize the PR review bot.

        Args:
            name: Bot name
            config: Configuration dictionary
            event_bus: Event bus for communication
            state_manager: State manager for persistence
            metrics: Metrics collector
        """
        super().__init__(name, config)
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics

        # Initialize GitHub client
        github_token = config.get("github_token")
        if not github_token:
            raise ValueError("GitHub token is required for PR Review Bot")
        self.github = Github(github_token)

        # Initialize PR-QUEST client
        pr_quest_url = config.get("pr_quest_url", "http://pr-quest:8000")
        self.pr_quest = PRQuestClient(base_url=pr_quest_url)

        # PR tracking
        self.pending_reviews: Dict[str, Dict[str, Any]] = {}
        self.review_history: List[Dict[str, Any]] = []
        self.pattern_cache: Optional[Dict[str, Any]] = None

        # Quality gate thresholds
        self.auto_approve_threshold = config.get("auto_approve_threshold", RiskLevel.NONE)
        self.flag_review_threshold = config.get("flag_review_threshold", RiskLevel.MODERATE)
        self.reject_threshold = config.get("reject_threshold", RiskLevel.CRITICAL)

    async def initialize(self) -> bool:
        """Initialize the PR review bot."""
        try:
            self.logger.info("Initializing PRReviewBot")

            # Load saved state
            state = await self.state_manager.load_state(self.name)
            self.pending_reviews = state.get("pending_reviews", {})
            self.review_history = state.get("review_history", [])

            # Verify PR-QUEST connectivity
            health = await self.pr_quest.health_check()
            if not health.get("healthy"):
                self.logger.warning("PR-QUEST is not healthy, bot will run in degraded mode")

            # Subscribe to integration PR events
            self.event_bus.subscribe("integration.pr_created", self._on_pr_created)
            self.event_bus.subscribe("integration.pr_updated", self._on_pr_updated)
            self.event_bus.subscribe("pr_review.human_decision", self._on_human_decision)

            # Load historical patterns from Cognee
            await self._load_review_patterns()

            self.logger.info("PRReviewBot initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize PRReviewBot: {str(e)}")
            return False

    async def execute(self) -> None:
        """Main execution loop."""
        self.logger.info("PRReviewBot execution started")

        while self.status.value == "running":
            try:
                # Process pending reviews
                await self._process_pending_reviews()

                # Monitor GitHub for new PRs
                await self._monitor_github_prs()

                # Update pattern cache from Cognee
                await self._refresh_pattern_cache()

                # Publish review metrics
                await self._publish_review_metrics()

                # Sleep interval
                await asyncio.sleep(self.config.get("check_interval", 60))

            except Exception as e:
                self.logger.error(f"Error in execution loop: {str(e)}", exc_info=True)
                self.error_count += 1
                await asyncio.sleep(5)

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up PRReviewBot")

        # Save state
        await self.state_manager.save_state(
            self.name,
            {
                "pending_reviews": self.pending_reviews,
                "review_history": self.review_history[-100:],  # Keep last 100
            },
        )

        # Close PR-QUEST client
        await self.pr_quest.close()

        self.logger.info("PRReviewBot cleanup complete")

    async def _monitor_github_prs(self) -> None:
        """Monitor GitHub repositories for new integration PRs."""
        try:
            repos = self.config.get("monitored_repositories", [])

            for repo_name in repos:
                try:
                    repo = self.github.get_repo(repo_name)
                    pulls = repo.get_pulls(state="open", sort="created", direction="desc")

                    for pr in pulls[:10]:  # Process up to 10 most recent
                        pr_key = f"{repo_name}#{pr.number}"

                        # Skip if already being reviewed
                        if pr_key in self.pending_reviews:
                            continue

                        # Check if PR is an integration PR
                        if self._is_integration_pr(pr):
                            await self._queue_pr_for_review(repo_name, pr)

                except GithubException as e:
                    self.logger.error(f"GitHub API error for {repo_name}: {str(e)}")
                    self.metrics.increment("pr_review.github_errors")

        except Exception as e:
            self.logger.error(f"Error monitoring GitHub PRs: {str(e)}")
            self.error_count += 1

    def _is_integration_pr(self, pr: PullRequest.PullRequest) -> bool:
        """
        Determine if a PR is an integration PR.

        Args:
            pr: GitHub pull request object

        Returns:
            True if this is an integration PR
        """
        # Check labels
        labels = [label.name.lower() for label in pr.labels]
        if "integration" in labels or "external-integration" in labels:
            return True

        # Check title patterns
        title_lower = pr.title.lower()
        integration_keywords = ["integration", "integrate", "connect", "add domain"]
        if any(keyword in title_lower for keyword in integration_keywords):
            return True

        # Check if PR modifies integration files
        files = [f.filename for f in pr.get_files()]
        integration_paths = ["src/integrations/", "integrations/", "connectors/"]
        if any(any(path in f for path in integration_paths) for f in files):
            return True

        return False

    async def _queue_pr_for_review(
        self, repo_name: str, pr: PullRequest.PullRequest
    ) -> None:
        """
        Queue a PR for automated review.

        Args:
            repo_name: Repository name
            pr: Pull request object
        """
        pr_key = f"{repo_name}#{pr.number}"

        self.logger.info(f"Queueing PR for review: {pr_key} - {pr.title}")

        self.pending_reviews[pr_key] = {
            "repo": repo_name,
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "title": pr.title,
            "author": pr.user.login,
            "created_at": pr.created_at.isoformat(),
            "queued_at": datetime.now().isoformat(),
            "status": "queued",
        }

        # Publish event
        await self.event_bus.publish(
            Event(
                event_type="pr_review.queued",
                source=self.name,
                data=self.pending_reviews[pr_key],
            )
        )

        self.metrics.increment("pr_review.queued")

    async def _process_pending_reviews(self) -> None:
        """Process PRs in the review queue."""
        if not self.pending_reviews:
            return

        # Process up to 5 PRs per cycle
        pending_keys = [
            k for k, v in self.pending_reviews.items() if v["status"] == "queued"
        ][:5]

        for pr_key in pending_keys:
            try:
                await self._review_pr(pr_key)
                self.task_count += 1

            except Exception as e:
                self.logger.error(f"Error reviewing PR {pr_key}: {str(e)}", exc_info=True)
                self.pending_reviews[pr_key]["status"] = "error"
                self.pending_reviews[pr_key]["error"] = str(e)
                self.error_count += 1
                self.metrics.increment("pr_review.errors")

    async def _review_pr(self, pr_key: str) -> None:
        """
        Perform automated review of a PR using PR-QUEST.

        Args:
            pr_key: PR identifier (repo#number)
        """
        pr_info = self.pending_reviews[pr_key]
        pr_url = pr_info["pr_url"]

        self.logger.info(f"Reviewing PR: {pr_key}")

        # Update status
        pr_info["status"] = "analyzing"
        pr_info["analysis_started_at"] = datetime.now().isoformat()

        # Call PR-QUEST for analysis
        analysis = await self.pr_quest.analyze_pr(
            pr_url=pr_url,
            include_llm_analysis=True,
            llm_model=self.config.get("llm_model", "gpt-4o-mini"),
        )

        self.logger.info(
            f"PR-QUEST analysis complete: {len(analysis.clusters)} clusters, "
            f"risk level: {analysis.overall_risk_level.value}"
        )

        # Apply quality gates
        decision = await self._apply_quality_gates(pr_info, analysis)

        # Store review in Cognee for pattern learning
        await self._store_review_in_cognee(pr_info, analysis, decision)

        # Update PR info with analysis results
        pr_info["status"] = "reviewed"
        pr_info["analysis_id"] = analysis.analysis_id
        pr_info["risk_level"] = analysis.overall_risk_level.value
        pr_info["decision"] = decision.value
        pr_info["reviewed_at"] = datetime.now().isoformat()
        pr_info["xp_awarded"] = analysis.xp_awarded

        # Add to history
        self.review_history.append({
            "pr_key": pr_key,
            "pr_url": pr_url,
            "analysis_id": analysis.analysis_id,
            "risk_level": analysis.overall_risk_level.value,
            "decision": decision.value,
            "reviewed_at": datetime.now().isoformat(),
        })

        # Publish completion event
        await self.event_bus.publish(
            Event(
                event_type="pr_review.complete",
                source=self.name,
                data={
                    "pr_key": pr_key,
                    "pr_url": pr_url,
                    "analysis_id": analysis.analysis_id,
                    "decision": decision.value,
                    "risk_level": analysis.overall_risk_level.value,
                    "clusters": len(analysis.clusters),
                    "risks": len(analysis.risks),
                    "xp_awarded": analysis.xp_awarded,
                },
            )
        )

        # Update metrics
        self.metrics.increment(f"pr_review.decision.{decision.value}")
        self.metrics.increment(f"pr_review.risk_level.{analysis.overall_risk_level.value}")

        # Take action based on decision
        await self._execute_decision(pr_info, analysis, decision)

    async def _apply_quality_gates(
        self, pr_info: Dict[str, Any], analysis: PRAnalysisResult
    ) -> ReviewDecision:
        """
        Apply quality gates to determine review decision.

        Args:
            pr_info: PR information
            analysis: PR-QUEST analysis result

        Returns:
            Review decision
        """
        risk_level = analysis.overall_risk_level

        # Check for critical risks
        if risk_level == RiskLevel.CRITICAL:
            critical_risks = [r for r in analysis.risks if r.severity == "critical"]

            # Check for security vulnerabilities
            security_risks = [
                r for r in critical_risks
                if any(kw in r.description.lower() for kw in ["security", "vulnerability", "exploit"])
            ]
            if security_risks:
                return ReviewDecision.REJECTED_SECURITY

            # Check for breaking changes
            breaking_risks = [
                r for r in critical_risks
                if any(kw in r.description.lower() for kw in ["breaking", "incompatible", "deprecated"])
            ]
            if breaking_risks:
                return ReviewDecision.REJECTED_BREAKING_CHANGES

            return ReviewDecision.REJECTED_CRITICAL_RISK

        # Check for moderate risks
        if risk_level == RiskLevel.MODERATE:
            # Flag for human review if moderate risk
            return ReviewDecision.FLAGGED_FOR_REVIEW

        # Low or no risk
        if len(analysis.suggestions) > 3:
            # Has suggestions but low risk
            return ReviewDecision.APPROVED_WITH_SUGGESTIONS

        # Clean PR with no/low risk
        return ReviewDecision.AUTO_APPROVED

    async def _execute_decision(
        self,
        pr_info: Dict[str, Any],
        analysis: PRAnalysisResult,
        decision: ReviewDecision,
    ) -> None:
        """
        Execute actions based on review decision.

        Args:
            pr_info: PR information
            analysis: PR-QUEST analysis result
            decision: Review decision
        """
        repo_name = pr_info["repo"]
        pr_number = pr_info["pr_number"]

        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Post review comment with analysis
            comment_body = self._format_review_comment(analysis, decision)
            pr.create_issue_comment(comment_body)

            # Apply labels
            if decision == ReviewDecision.AUTO_APPROVED:
                pr.add_to_labels("auto-approved", "ready-to-merge")
                self.logger.info(f"Auto-approved PR: {pr_info['pr_key']}")

            elif decision == ReviewDecision.APPROVED_WITH_SUGGESTIONS:
                pr.add_to_labels("approved-with-suggestions")
                self.logger.info(f"Approved with suggestions: {pr_info['pr_key']}")

            elif decision == ReviewDecision.FLAGGED_FOR_REVIEW:
                pr.add_to_labels("needs-review", "moderate-risk")
                pr.request_reviewers(self.config.get("human_reviewers", []))
                self.logger.info(f"Flagged for human review: {pr_info['pr_key']}")

            elif decision in [
                ReviewDecision.REJECTED_CRITICAL_RISK,
                ReviewDecision.REJECTED_SECURITY,
                ReviewDecision.REJECTED_BREAKING_CHANGES,
            ]:
                pr.add_to_labels("changes-requested", "critical-risk")
                self.logger.warning(f"Rejected PR: {pr_info['pr_key']} - {decision.value}")

        except GithubException as e:
            self.logger.error(f"Error executing decision for {pr_info['pr_key']}: {str(e)}")
            self.metrics.increment("pr_review.github_errors")

    def _format_review_comment(
        self, analysis: PRAnalysisResult, decision: ReviewDecision
    ) -> str:
        """
        Format PR review comment with analysis results.

        Args:
            analysis: PR-QUEST analysis result
            decision: Review decision

        Returns:
            Formatted markdown comment
        """
        lines = [
            "## 🤖 Automated PR Review (PR-QUEST)",
            "",
            f"**Decision:** {decision.value.replace('_', ' ').title()}",
            f"**Risk Level:** {analysis.overall_risk_level.value}",
            f"**XP Awarded:** {analysis.xp_awarded} 🎮",
            "",
        ]

        # Add clusters
        if analysis.clusters:
            lines.extend([
                "### 📦 Code Clusters",
                "",
            ])
            for i, cluster in enumerate(analysis.clusters[:5], 1):
                lines.append(f"{i}. **{cluster.cluster_name}**")
                lines.append(f"   - Files: {len(cluster.files)}")
                lines.append(f"   - {cluster.description}")
                lines.append("")

        # Add risks
        if analysis.risks:
            lines.extend([
                "### ⚠️ Detected Risks",
                "",
            ])
            for risk in analysis.risks[:10]:
                icon = "🔴" if risk.severity == "critical" else "🟡" if risk.severity == "moderate" else "🔵"
                lines.append(f"{icon} **{risk.title}** ({risk.severity})")
                lines.append(f"   - {risk.description}")
                if risk.mitigation:
                    lines.append(f"   - *Mitigation:* {risk.mitigation}")
                lines.append("")

        # Add suggestions
        if analysis.suggestions:
            lines.extend([
                "### 💡 Suggestions",
                "",
            ])
            for suggestion in analysis.suggestions[:10]:
                lines.append(f"- {suggestion}")
            lines.append("")

        lines.extend([
            "---",
            f"*Analysis ID: {analysis.analysis_id}*",
            "*Powered by [PR-QUEST](https://github.com/Fission-AI/pr-quest) and PIPE Governance*",
        ])

        return "\n".join(lines)

    async def _store_review_in_cognee(
        self,
        pr_info: Dict[str, Any],
        analysis: PRAnalysisResult,
        decision: ReviewDecision,
    ) -> None:
        """
        Store PR review in Cognee for pattern learning.

        Args:
            pr_info: PR information
            analysis: PR-QUEST analysis result
            decision: Review decision
        """
        try:
            # Create PRReviewDataPoint
            datapoint = create_pr_review_datapoint(
                pr_url=pr_info["pr_url"],
                pr_number=pr_info["pr_number"],
                repository=pr_info["repo"],
                analysis_id=analysis.analysis_id,
                clusters=[
                    {
                        "name": c.cluster_name,
                        "files": c.files,
                        "description": c.description,
                    }
                    for c in analysis.clusters
                ],
                risks=[
                    f"{r.severity}: {r.title} - {r.description}"
                    for r in analysis.risks
                ],
                risk_level=analysis.overall_risk_level.value,
                suggestions=analysis.suggestions,
                xp_awarded=analysis.xp_awarded,
                decision=decision.value,
                reviewer=self.name,
            )

            # Add to Cognee
            await add(datapoint)
            await cognify()

            self.logger.debug(f"Stored review in Cognee: {analysis.analysis_id}")
            self.metrics.increment("pr_review.cognee_stored")

        except Exception as e:
            self.logger.error(f"Error storing review in Cognee: {str(e)}")
            self.metrics.increment("pr_review.cognee_errors")

    async def _load_review_patterns(self) -> None:
        """Load historical review patterns from Cognee."""
        try:
            # Query Cognee for similar past reviews
            results = await search(
                "What patterns exist in PR reviews?",
                search_type="insights",
            )

            if results:
                self.pattern_cache = {
                    "loaded_at": datetime.now().isoformat(),
                    "patterns": results,
                }
                self.logger.info(f"Loaded {len(results)} review patterns from Cognee")

        except Exception as e:
            self.logger.warning(f"Could not load review patterns: {str(e)}")

    async def _refresh_pattern_cache(self) -> None:
        """Refresh pattern cache from Cognee periodically."""
        # Refresh every hour
        if not self.pattern_cache:
            return

        loaded_at = datetime.fromisoformat(self.pattern_cache["loaded_at"])
        if (datetime.now() - loaded_at).total_seconds() < 3600:
            return

        await self._load_review_patterns()

    async def _publish_review_metrics(self) -> None:
        """Publish PR review metrics to event bus."""
        total_reviews = len(self.review_history)
        pending_count = sum(1 for r in self.pending_reviews.values() if r["status"] in ["queued", "analyzing"])

        # Count decisions
        decisions = {}
        for review in self.review_history[-100:]:
            decision = review.get("decision", "unknown")
            decisions[decision] = decisions.get(decision, 0) + 1

        metrics_data = {
            "total_reviews": total_reviews,
            "pending_reviews": pending_count,
            "decisions": decisions,
            "review_history_size": len(self.review_history),
        }

        await self.event_bus.publish(
            Event(
                event_type="pr_review.metrics",
                source=self.name,
                data=metrics_data,
            )
        )

        # Update metrics collector
        self.metrics.gauge("pr_review.pending_count", pending_count)
        self.metrics.gauge("pr_review.total_reviews", total_reviews)

    async def _on_pr_created(self, event: Event) -> None:
        """Handle PR created events."""
        repo_name = event.data.get("repository")
        pr_number = event.data.get("pr_number")

        if not repo_name or not pr_number:
            return

        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            if self._is_integration_pr(pr):
                await self._queue_pr_for_review(repo_name, pr)

        except GithubException as e:
            self.logger.error(f"Error handling PR created event: {str(e)}")

    async def _on_pr_updated(self, event: Event) -> None:
        """Handle PR updated events."""
        repo_name = event.data.get("repository")
        pr_number = event.data.get("pr_number")
        pr_key = f"{repo_name}#{pr_number}"

        # Re-review if PR was updated after initial review
        if pr_key in self.pending_reviews:
            pr_info = self.pending_reviews[pr_key]
            if pr_info["status"] == "reviewed":
                self.logger.info(f"PR updated, re-queueing for review: {pr_key}")
                pr_info["status"] = "queued"
                self.metrics.increment("pr_review.requeued")

    async def _on_human_decision(self, event: Event) -> None:
        """
        Handle human review decision events for learning.

        Args:
            event: Human decision event
        """
        pr_key = event.data.get("pr_key")
        human_decision = event.data.get("decision")
        notes = event.data.get("notes", "")

        if not pr_key or pr_key not in self.pending_reviews:
            return

        pr_info = self.pending_reviews[pr_key]
        bot_decision = pr_info.get("decision")

        # Log disagreement for pattern learning
        if bot_decision != human_decision:
            self.logger.info(
                f"Human override: PR {pr_key} - Bot: {bot_decision}, Human: {human_decision}"
            )

            # Store override in Cognee for learning
            await add({
                "type": "review_override",
                "pr_key": pr_key,
                "bot_decision": bot_decision,
                "human_decision": human_decision,
                "notes": notes,
                "timestamp": datetime.now().isoformat(),
            })
            await cognify()

            self.metrics.increment("pr_review.human_override")
