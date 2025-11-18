"""Tests for PR Review Bot."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.bots.pr_review_bot import PRReviewBot, ReviewDecision
from src.core.event_bus import EventBus, Event
from src.core.state_manager import StateManager
from src.utils.metrics import MetricsCollector
from src.integrations.pr_quest_models import (
    PRAnalysisResult,
    RiskLevel,
    Risk,
    CodeCluster,
)


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "github_token": "test_token_12345",
        "monitored_repositories": ["test-org/test-repo"],
        "pr_quest_url": "http://mock-pr-quest:8000",
        "llm_model": "gpt-4o-mini",
        "check_interval": 60,
        "log_level": "DEBUG",
        "auto_approve_threshold": "NONE",
        "flag_review_threshold": "MODERATE",
        "reject_threshold": "CRITICAL",
        "human_reviewers": ["reviewer1", "reviewer2"],
    }


@pytest.fixture
def event_bus():
    """Create event bus for testing."""
    return EventBus()


@pytest.fixture
def state_manager():
    """Create state manager for testing."""
    manager = StateManager(state_dir="./test_state")
    return manager


@pytest.fixture
def metrics():
    """Create metrics collector for testing."""
    return MetricsCollector()


@pytest.fixture
def mock_pr_quest_client():
    """Mock PR-QUEST client."""
    client = AsyncMock()
    client.health_check.return_value = {"healthy": True}
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_github():
    """Mock GitHub client."""
    github = Mock()
    return github


@pytest.mark.asyncio
class TestPRReviewBot:
    """Test suite for PR Review Bot."""

    async def test_bot_initialization(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test bot initializes correctly."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.health_check = AsyncMock(
                    return_value={"healthy": True}
                )
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_pr_review_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                success = await bot.initialize()
                assert success is True
                assert bot.name == "test_pr_review_bot"
                assert bot.pending_reviews == {}

                await bot.cleanup()

    async def test_is_integration_pr_by_label(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test identifying integration PR by label."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                # Mock PR with integration label
                mock_pr = Mock()
                mock_pr.labels = [Mock(name="integration"), Mock(name="feature")]

                assert bot._is_integration_pr(mock_pr) is True

                await bot.cleanup()

    async def test_is_integration_pr_by_title(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test identifying integration PR by title."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                # Mock PR with integration in title
                mock_pr = Mock()
                mock_pr.labels = []
                mock_pr.title = "Add Cognee integration for AI memory"
                mock_pr.get_files = Mock(return_value=[])

                assert bot._is_integration_pr(mock_pr) is True

                await bot.cleanup()

    async def test_is_integration_pr_by_files(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test identifying integration PR by modified files."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                # Mock PR with integration files
                mock_pr = Mock()
                mock_pr.labels = []
                mock_pr.title = "Update client code"
                mock_file = Mock()
                mock_file.filename = "src/integrations/cognee_client.py"
                mock_pr.get_files = Mock(return_value=[mock_file])

                assert bot._is_integration_pr(mock_pr) is True

                await bot.cleanup()

    async def test_apply_quality_gates_auto_approve(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test quality gates auto-approve clean PR."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                pr_info = {"pr_url": "https://github.com/test/repo/pull/1"}
                analysis = PRAnalysisResult(
                    analysis_id="test123",
                    pr_url="https://github.com/test/repo/pull/1",
                    clusters=[],
                    risks=[],
                    overall_risk_level=RiskLevel.NONE,
                    suggestions=[],
                    xp_awarded=100,
                )

                decision = await bot._apply_quality_gates(pr_info, analysis)
                assert decision == ReviewDecision.AUTO_APPROVED

                await bot.cleanup()

    async def test_apply_quality_gates_reject_security(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test quality gates reject PR with security risk."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                pr_info = {"pr_url": "https://github.com/test/repo/pull/1"}
                analysis = PRAnalysisResult(
                    analysis_id="test123",
                    pr_url="https://github.com/test/repo/pull/1",
                    clusters=[],
                    risks=[
                        Risk(
                            title="SQL Injection Vulnerability",
                            description="Potential security vulnerability in database query",
                            severity="critical",
                            file_path="src/db.py",
                            line_number=42,
                            mitigation="Use parameterized queries",
                        )
                    ],
                    overall_risk_level=RiskLevel.CRITICAL,
                    suggestions=[],
                    xp_awarded=0,
                )

                decision = await bot._apply_quality_gates(pr_info, analysis)
                assert decision == ReviewDecision.REJECTED_SECURITY

                await bot.cleanup()

    async def test_apply_quality_gates_flag_for_review(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test quality gates flag moderate risk for review."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                pr_info = {"pr_url": "https://github.com/test/repo/pull/1"}
                analysis = PRAnalysisResult(
                    analysis_id="test123",
                    pr_url="https://github.com/test/repo/pull/1",
                    clusters=[],
                    risks=[
                        Risk(
                            title="Code Duplication",
                            description="Similar code found in multiple places",
                            severity="moderate",
                            file_path="src/utils.py",
                            line_number=10,
                        )
                    ],
                    overall_risk_level=RiskLevel.MODERATE,
                    suggestions=["Consider extracting common code"],
                    xp_awarded=50,
                )

                decision = await bot._apply_quality_gates(pr_info, analysis)
                assert decision == ReviewDecision.FLAGGED_FOR_REVIEW

                await bot.cleanup()

    async def test_format_review_comment(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test formatting of review comment."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                analysis = PRAnalysisResult(
                    analysis_id="test123",
                    pr_url="https://github.com/test/repo/pull/1",
                    clusters=[
                        CodeCluster(
                            cluster_id="cluster1",
                            cluster_name="Authentication",
                            files=["auth.py", "login.py"],
                            description="Authentication related changes",
                        )
                    ],
                    risks=[],
                    overall_risk_level=RiskLevel.NONE,
                    suggestions=["Add tests for edge cases"],
                    xp_awarded=150,
                )

                comment = bot._format_review_comment(
                    analysis, ReviewDecision.AUTO_APPROVED
                )

                assert "Automated PR Review" in comment
                assert "Auto Approved" in comment
                assert "NONE" in comment
                assert "150" in comment
                assert "Authentication" in comment
                assert "Add tests" in comment

                await bot.cleanup()

    async def test_queue_pr_for_review(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test queuing a PR for review."""
        with patch("src.bots.pr_review_bot.Github"):
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.close = AsyncMock()

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                await bot.initialize()

                # Mock PR
                mock_pr = Mock()
                mock_pr.number = 42
                mock_pr.html_url = "https://github.com/test/repo/pull/42"
                mock_pr.title = "Test PR"
                mock_pr.user.login = "testuser"
                mock_pr.created_at = datetime.now()

                await bot._queue_pr_for_review("test/repo", mock_pr)

                pr_key = "test/repo#42"
                assert pr_key in bot.pending_reviews
                assert bot.pending_reviews[pr_key]["status"] == "queued"
                assert bot.pending_reviews[pr_key]["pr_number"] == 42

                await bot.cleanup()

    async def test_on_pr_created_event(
        self, mock_config, event_bus, state_manager, metrics
    ):
        """Test handling PR created event."""
        with patch("src.bots.pr_review_bot.Github") as mock_github_class:
            with patch("src.bots.pr_review_bot.PRQuestClient") as mock_pr_quest:
                mock_pr_quest.return_value.health_check = AsyncMock(
                    return_value={"healthy": True}
                )
                mock_pr_quest.return_value.close = AsyncMock()

                # Setup mock GitHub
                mock_github = Mock()
                mock_repo = Mock()
                mock_pr = Mock()
                mock_pr.labels = [Mock(name="integration")]
                mock_pr.number = 123
                mock_pr.html_url = "https://github.com/test/repo/pull/123"
                mock_pr.title = "Integration PR"
                mock_pr.user.login = "testuser"
                mock_pr.created_at = datetime.now()

                mock_repo.get_pull.return_value = mock_pr
                mock_github.get_repo.return_value = mock_repo
                mock_github_class.return_value = mock_github

                bot = PRReviewBot(
                    name="test_bot",
                    config=mock_config,
                    event_bus=event_bus,
                    state_manager=state_manager,
                    metrics=metrics,
                )

                await bot.initialize()

                # Trigger event
                await event_bus.publish(
                    Event(
                        event_type="integration.pr_created",
                        source="test",
                        data={"repository": "test/repo", "pr_number": 123},
                    )
                )

                # Wait for event processing
                await asyncio.sleep(0.1)

                # Verify PR was queued
                assert "test/repo#123" in bot.pending_reviews

                await bot.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
