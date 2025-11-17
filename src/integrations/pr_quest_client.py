"""
PR-QUEST client for interactive PR code review.

This module provides an async client for integrating with PR-QUEST
(https://github.com/Fission-AI/PR-QUEST), an interactive platform for
reviewing GitHub pull requests with LLM-powered analysis and gamification.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientError, ClientTimeout

from .pr_quest_models import (
    AnalyzeRequest,
    PRAnalysisResult,
    ReviewNote,
    ReviewStep,
    ReviewerXP,
    SubmitNotesRequest,
    parse_pr_url,
)

logger = logging.getLogger(__name__)


class PRQuestError(Exception):
    """Base exception for PR-QUEST client errors."""

    pass


class PRQuestConnectionError(PRQuestError):
    """Raised when cannot connect to PR-QUEST service."""

    pass


class PRQuestAnalysisError(PRQuestError):
    """Raised when PR analysis fails."""

    pass


class PRQuestClient:
    """
    Async client for PR-QUEST interactive PR review platform.

    PR-QUEST provides:
    - LLM-powered PR analysis and clustering
    - Risk detection (security, breaking changes, anti-patterns)
    - Interactive review steps with diff rendering
    - Gamification with XP and achievements
    - Markdown export for governance records

    Example:
        ```python
        client = PRQuestClient("http://localhost:3000")
        await client.initialize()

        # Analyze a PR
        result = await client.analyze_pr(
            "https://github.com/org/repo/pull/123",
            include_llm_analysis=True
        )

        print(f"Found {len(result.risks)} risks")
        print(f"Overall risk level: {result.overall_risk_level}")

        # Export as markdown
        markdown = await client.export_markdown(result.analysis_id)
        ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize PR-QUEST client.

        Args:
            base_url: Base URL of PR-QUEST service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info(f"Initialized PR-QUEST client for {self.base_url}")

    async def initialize(self) -> bool:
        """
        Initialize the client and create HTTP session.

        Returns:
            bool: True if initialization successful

        Raises:
            PRQuestConnectionError: If cannot connect to PR-QUEST
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

        # Verify connectivity
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    logger.info("PR-QUEST service is healthy")
                    return True
                else:
                    raise PRQuestConnectionError(
                        f"PR-QUEST returned status {response.status}"
                    )
        except ClientError as e:
            raise PRQuestConnectionError(
                f"Cannot connect to PR-QUEST at {self.base_url}: {e}"
            ) from e

    async def cleanup(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("PR-QUEST client session closed")

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to PR-QUEST API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: JSON data for POST/PUT requests
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            PRQuestConnectionError: If request fails after retries
        """
        if not self.session or self.session.closed:
            await self.initialize()

        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method, url, json=data, params=params, headers=headers
                ) as response:
                    response_data = await response.json()

                    if response.status == 200:
                        return response_data
                    elif response.status == 404:
                        raise PRQuestError(f"Resource not found: {url}")
                    elif response.status >= 500:
                        # Server error - retry
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff
                            logger.warning(
                                f"PR-QUEST server error (attempt {attempt + 1}/{self.max_retries}). "
                                f"Retrying in {wait_time}s..."
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise PRQuestConnectionError(
                                f"PR-QUEST server error: {response_data}"
                            )
                    else:
                        raise PRQuestError(
                            f"PR-QUEST request failed: {response.status} - {response_data}"
                        )

            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request timeout (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise PRQuestConnectionError(
                        f"Request timeout after {self.max_retries} attempts"
                    )

            except ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request failed: {e} (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise PRQuestConnectionError(f"Request failed: {e}") from e

        # Should not reach here
        raise PRQuestConnectionError("Max retries exceeded")

    async def analyze_pr(
        self,
        pr_url: str,
        include_llm_analysis: bool = True,
        llm_model: Optional[str] = None,
    ) -> PRAnalysisResult:
        """
        Analyze a GitHub PR using PR-QUEST.

        This sends the PR to PR-QUEST for comprehensive analysis including:
        - Diff parsing and normalization
        - LLM-powered clustering of related changes
        - Risk detection (security, breaking changes, etc.)
        - Suggestion generation

        Args:
            pr_url: Full GitHub PR URL (e.g., https://github.com/org/repo/pull/123)
            include_llm_analysis: Use LLM for intelligent clustering (default: True)
            llm_model: Specific LLM model to use (default: configured in PR-QUEST)

        Returns:
            PRAnalysisResult with complete analysis

        Raises:
            PRQuestAnalysisError: If analysis fails
            ValueError: If PR URL is invalid
        """
        logger.info(f"Analyzing PR: {pr_url} (LLM: {include_llm_analysis})")

        # Validate and parse PR URL
        try:
            pr_parts = parse_pr_url(pr_url)
        except ValueError as e:
            raise ValueError(f"Invalid PR URL: {e}") from e

        # Create analysis request
        request = AnalyzeRequest(
            pr_url=pr_url,
            include_llm_analysis=include_llm_analysis,
            llm_model=llm_model,
        )

        try:
            # Send analysis request
            response_data = await self._request(
                "POST", "/api/analyze", data=request.model_dump(mode="json")
            )

            # Parse response into PRAnalysisResult
            analysis = PRAnalysisResult(**response_data)

            logger.info(
                f"PR analysis complete: {analysis.analysis_id} - "
                f"{len(analysis.clusters)} clusters, {len(analysis.risks)} risks, "
                f"risk level: {analysis.overall_risk_level}"
            )

            return analysis

        except Exception as e:
            logger.error(f"PR analysis failed for {pr_url}: {e}")
            raise PRQuestAnalysisError(f"Failed to analyze PR: {e}") from e

    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the status of an ongoing analysis.

        Useful for long-running analyses to check progress.

        Args:
            analysis_id: Analysis identifier

        Returns:
            Dict with status info (status, progress, eta)

        Raises:
            PRQuestError: If analysis not found
        """
        logger.debug(f"Checking analysis status: {analysis_id}")

        response_data = await self._request("GET", f"/api/analyze/{analysis_id}/status")

        return response_data

    async def get_review_steps(self, analysis_id: str) -> List[ReviewStep]:
        """
        Get interactive review steps for a PR analysis.

        Review steps provide a guided walkthrough of the PR changes,
        grouped by logical clusters with diff rendering.

        Args:
            analysis_id: Analysis identifier

        Returns:
            List of ReviewStep objects

        Raises:
            PRQuestError: If analysis not found
        """
        logger.info(f"Fetching review steps for analysis: {analysis_id}")

        response_data = await self._request("GET", f"/api/analyze/{analysis_id}/steps")

        steps = [ReviewStep(**step_data) for step_data in response_data.get("steps", [])]

        logger.info(f"Retrieved {len(steps)} review steps")

        return steps

    async def submit_review_notes(
        self, analysis_id: str, notes: List[ReviewNote]
    ) -> bool:
        """
        Submit review notes for specific PR sections.

        Notes are attached to review steps and can be exported to markdown.

        Args:
            analysis_id: Analysis identifier
            notes: List of ReviewNote objects to add

        Returns:
            bool: True if notes saved successfully

        Raises:
            PRQuestError: If submission fails
        """
        logger.info(f"Submitting {len(notes)} review notes for analysis: {analysis_id}")

        request = SubmitNotesRequest(
            analysis_id=analysis_id, notes=notes
        )

        response_data = await self._request(
            "POST",
            f"/api/analyze/{analysis_id}/notes",
            data=request.model_dump(mode="json"),
        )

        success = response_data.get("success", False)

        if success:
            logger.info("Review notes submitted successfully")
        else:
            logger.warning("Review notes submission may have failed")

        return success

    async def export_markdown(self, analysis_id: str) -> str:
        """
        Export complete PR review as markdown document.

        The markdown includes:
        - PR metadata
        - Analysis summary
        - All clusters with descriptions
        - Detected risks and suggestions
        - Reviewer notes (if any)

        Perfect for including in governance documentation.

        Args:
            analysis_id: Analysis identifier

        Returns:
            str: Markdown-formatted review document

        Raises:
            PRQuestError: If export fails
        """
        logger.info(f"Exporting markdown for analysis: {analysis_id}")

        response_data = await self._request("GET", f"/api/analyze/{analysis_id}/export")

        markdown = response_data.get("markdown", "")

        logger.info(f"Exported {len(markdown)} character markdown document")

        return markdown

    async def get_xp_leaderboard(self, limit: int = 10) -> List[ReviewerXP]:
        """
        Get reviewer XP leaderboard for gamification.

        The leaderboard shows top reviewers by total XP earned,
        encouraging thorough and timely reviews.

        Args:
            limit: Number of top reviewers to return (default: 10)

        Returns:
            List of ReviewerXP objects, sorted by rank

        Raises:
            PRQuestError: If request fails
        """
        logger.info(f"Fetching XP leaderboard (top {limit})")

        response_data = await self._request(
            "GET", "/api/leaderboard", params={"limit": limit}
        )

        leaderboard = [
            ReviewerXP(**reviewer_data)
            for reviewer_data in response_data.get("leaderboard", [])
        ]

        logger.info(f"Retrieved leaderboard with {len(leaderboard)} reviewers")

        return leaderboard

    async def get_reviewer_stats(self, username: str) -> ReviewerXP:
        """
        Get XP statistics for a specific reviewer.

        Args:
            username: Reviewer username

        Returns:
            ReviewerXP object with stats

        Raises:
            PRQuestError: If reviewer not found
        """
        logger.info(f"Fetching stats for reviewer: {username}")

        response_data = await self._request("GET", f"/api/reviewers/{username}/stats")

        stats = ReviewerXP(**response_data)

        logger.info(
            f"Reviewer {username}: {stats.total_xp} XP, "
            f"{stats.reviews_completed} reviews, rank #{stats.rank}"
        )

        return stats

    async def healthcheck(self) -> bool:
        """
        Check if PR-QUEST service is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            response_data = await self._request("GET", "/api/health")
            status = response_data.get("status", "unknown")
            healthy = status == "healthy" or status == "ok"

            if healthy:
                logger.debug("PR-QUEST health check: OK")
            else:
                logger.warning(f"PR-QUEST health check: {status}")

            return healthy

        except Exception as e:
            logger.error(f"PR-QUEST health check failed: {e}")
            return False


# ============================================================================
# Singleton Factory
# ============================================================================

_pr_quest_client_instance: Optional[PRQuestClient] = None


async def get_pr_quest_client(
    base_url: str = "http://localhost:3000",
    timeout: int = 30,
    force_new: bool = False,
) -> PRQuestClient:
    """
    Get singleton PR-QUEST client instance.

    Args:
        base_url: Base URL of PR-QUEST service
        timeout: Request timeout in seconds
        force_new: Force creation of new instance (default: False)

    Returns:
        Initialized PRQuestClient instance

    Raises:
        PRQuestConnectionError: If cannot connect to PR-QUEST
    """
    global _pr_quest_client_instance

    if force_new or _pr_quest_client_instance is None:
        _pr_quest_client_instance = PRQuestClient(base_url=base_url, timeout=timeout)
        await _pr_quest_client_instance.initialize()

    return _pr_quest_client_instance


async def cleanup_pr_quest_client() -> None:
    """Cleanup singleton PR-QUEST client instance."""
    global _pr_quest_client_instance

    if _pr_quest_client_instance is not None:
        await _pr_quest_client_instance.cleanup()
        _pr_quest_client_instance = None
