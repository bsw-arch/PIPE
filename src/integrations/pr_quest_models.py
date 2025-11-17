"""
Data models for PR-QUEST integration.

This module defines Pydantic models for PR-QUEST API requests and responses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class RiskLevel(str, Enum):
    """Risk severity levels from PR analysis."""

    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    CRITICAL = "CRITICAL"


class RiskType(str, Enum):
    """Types of risks that can be detected in PRs."""

    SECURITY = "SECURITY"  # Security vulnerabilities
    BREAKING_CHANGE = "BREAKING_CHANGE"  # API breaking changes
    ANTI_PATTERN = "ANTI_PATTERN"  # Code anti-patterns
    PERFORMANCE = "PERFORMANCE"  # Performance issues
    COMPLIANCE = "COMPLIANCE"  # Compliance violations
    MAINTAINABILITY = "MAINTAINABILITY"  # Code complexity issues
    TESTING = "TESTING"  # Insufficient test coverage
    DOCUMENTATION = "DOCUMENTATION"  # Missing or poor documentation


class ReviewDecision(str, Enum):
    """Possible review decisions."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEEDS_REVIEW = "NEEDS_REVIEW"


# ============================================================================
# PR-QUEST API Models
# ============================================================================


class CodeCluster(BaseModel):
    """A group of related code changes identified by LLM."""

    id: str = Field(..., description="Unique cluster identifier")
    description: str = Field(..., description="LLM-generated description of changes")
    files: List[str] = Field(..., description="Files in this cluster")
    line_count: int = Field(..., description="Total lines changed in cluster")
    category: Optional[str] = Field(None, description="Category (feature, bugfix, refactor)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "cluster-1",
                "description": "Authentication middleware updates",
                "files": ["src/auth/middleware.py", "tests/test_auth.py"],
                "line_count": 156,
                "category": "feature",
            }
        }


class Risk(BaseModel):
    """A detected risk in the PR."""

    id: str = Field(..., description="Unique risk identifier")
    type: RiskType = Field(..., description="Type of risk")
    severity: RiskLevel = Field(..., description="Risk severity level")
    description: str = Field(..., description="Human-readable description")
    location: Optional[str] = Field(None, description="File:line where risk is located")
    recommendation: Optional[str] = Field(None, description="How to fix")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in detection (0.0 to 1.0)"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "risk-1",
                "type": "SECURITY",
                "severity": "CRITICAL",
                "description": "SQL injection vulnerability detected",
                "location": "src/db/queries.py:42",
                "recommendation": "Use parameterized queries instead of string concatenation",
                "confidence": 0.95,
            }
        }


class PRAnalysisResult(BaseModel):
    """Complete result from PR-QUEST analysis."""

    analysis_id: str = Field(..., description="Unique analysis identifier")
    pr_url: HttpUrl = Field(..., description="GitHub PR URL")
    pr_number: int = Field(..., description="PR number")
    repository: str = Field(..., description="Repository (owner/repo)")

    # Analysis results
    clusters: List[CodeCluster] = Field(default_factory=list, description="Grouped code changes")
    risks: List[Risk] = Field(default_factory=list, description="Detected risks")
    overall_risk_level: RiskLevel = Field(
        RiskLevel.NONE, description="Overall risk assessment"
    )
    suggestions: List[str] = Field(default_factory=list, description="LLM-generated suggestions")

    # Metadata
    xp_awarded: int = Field(0, description="XP points awarded for review")
    analyzed_at: int = Field(..., description="Unix timestamp of analysis")
    analysis_duration_seconds: float = Field(..., description="Time taken for analysis")

    # LLM info
    llm_used: bool = Field(True, description="Whether LLM was used for analysis")
    llm_model: Optional[str] = Field(None, description="LLM model used (e.g., gpt-4o-mini)")

    @validator("overall_risk_level", always=True)
    def calculate_overall_risk(cls, v, values):
        """Calculate overall risk level from individual risks."""
        if "risks" not in values or not values["risks"]:
            return RiskLevel.NONE

        # Get highest severity from risks
        severities = [risk.severity for risk in values["risks"]]
        if RiskLevel.CRITICAL in severities:
            return RiskLevel.CRITICAL
        elif RiskLevel.MODERATE in severities:
            return RiskLevel.MODERATE
        elif RiskLevel.LOW in severities:
            return RiskLevel.LOW
        return RiskLevel.NONE

    def has_critical_risks(self) -> bool:
        """Check if any critical risks exist."""
        return any(risk.severity == RiskLevel.CRITICAL for risk in self.risks)

    def has_moderate_risks(self) -> bool:
        """Check if any moderate risks exist."""
        return any(risk.severity == RiskLevel.MODERATE for risk in self.risks)

    def get_risks_by_type(self, risk_type: RiskType) -> List[Risk]:
        """Get all risks of a specific type."""
        return [risk for risk in self.risks if risk.type == risk_type]

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "analysis_id": "ana_1234567890",
                "pr_url": "https://github.com/bsw-arch/PIPE/pull/123",
                "pr_number": 123,
                "repository": "bsw-arch/PIPE",
                "clusters": [],
                "risks": [],
                "overall_risk_level": "NONE",
                "suggestions": ["Consider adding integration tests"],
                "xp_awarded": 150,
                "analyzed_at": 1705507200,
                "analysis_duration_seconds": 12.5,
                "llm_used": True,
                "llm_model": "gpt-4o-mini",
            }
        }


class ReviewStep(BaseModel):
    """An interactive review step from PR-QUEST."""

    step_id: str = Field(..., description="Step identifier")
    cluster_id: str = Field(..., description="Associated cluster")
    title: str = Field(..., description="Step title")
    diff_section: str = Field(..., description="Diff content for this step")
    guidance: Optional[str] = Field(None, description="LLM guidance for reviewing this step")
    notes: List[str] = Field(default_factory=list, description="Reviewer notes")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "step_id": "step-1",
                "cluster_id": "cluster-1",
                "title": "Review authentication middleware changes",
                "diff_section": "--- a/src/auth/middleware.py\n+++ b/src/auth/middleware.py\n...",
                "guidance": "Check that JWT validation is secure",
                "notes": [],
            }
        }


class ReviewNote(BaseModel):
    """A note added during PR review."""

    step_id: str = Field(..., description="Step this note is for")
    content: str = Field(..., description="Note content")
    reviewer: str = Field(..., description="Reviewer username")
    timestamp: int = Field(..., description="Unix timestamp")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "step_id": "step-1",
                "content": "Verified JWT signature algorithm is secure",
                "reviewer": "john.doe",
                "timestamp": 1705507200,
            }
        }


class ReviewerXP(BaseModel):
    """Reviewer XP and gamification stats."""

    username: str = Field(..., description="Reviewer username")
    total_xp: int = Field(..., description="Total XP earned")
    reviews_completed: int = Field(..., description="Number of reviews completed")
    rank: int = Field(..., description="Leaderboard rank")
    level: int = Field(..., description="Reviewer level (based on XP)")
    achievements: List[str] = Field(default_factory=list, description="Earned achievements")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "username": "john.doe",
                "total_xp": 4500,
                "reviews_completed": 25,
                "rank": 3,
                "level": 7,
                "achievements": ["First Review", "Critical Eye", "Speed Reviewer"],
            }
        }


# ============================================================================
# Request Models
# ============================================================================


class AnalyzeRequest(BaseModel):
    """Request to analyze a PR."""

    pr_url: HttpUrl = Field(..., description="GitHub PR URL to analyze")
    include_llm_analysis: bool = Field(True, description="Use LLM for intelligent clustering")
    llm_model: Optional[str] = Field(None, description="Specific LLM model to use")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "pr_url": "https://github.com/bsw-arch/PIPE/pull/123",
                "include_llm_analysis": True,
                "llm_model": "gpt-4o-mini",
            }
        }


class SubmitNotesRequest(BaseModel):
    """Request to submit review notes."""

    analysis_id: str = Field(..., description="Analysis ID")
    notes: List[ReviewNote] = Field(..., description="Review notes to add")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "analysis_id": "ana_1234567890",
                "notes": [
                    {
                        "step_id": "step-1",
                        "content": "Looks good!",
                        "reviewer": "john.doe",
                        "timestamp": 1705507200,
                    }
                ],
            }
        }


# ============================================================================
# Utility Functions
# ============================================================================


def parse_pr_url(pr_url: str) -> Dict[str, str]:
    """
    Parse GitHub PR URL to extract owner, repo, and PR number.

    Args:
        pr_url: GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

    Returns:
        Dict with 'owner', 'repo', and 'pr_number' keys

    Raises:
        ValueError: If URL format is invalid
    """
    try:
        # Remove trailing slash if present
        pr_url = pr_url.rstrip("/")

        # Expected format: https://github.com/owner/repo/pull/123
        parts = pr_url.split("/")

        if len(parts) < 7 or parts[2] != "github.com" or parts[5] != "pull":
            raise ValueError("Invalid GitHub PR URL format")

        return {
            "owner": parts[3],
            "repo": parts[4],
            "pr_number": parts[6],
        }
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Failed to parse PR URL: {pr_url}") from e


def determine_decision_from_analysis(
    analysis: PRAnalysisResult, auto_approve_threshold: float = 0.95
) -> ReviewDecision:
    """
    Determine review decision based on PR analysis.

    Args:
        analysis: PR analysis result
        auto_approve_threshold: Confidence threshold for auto-approval (0.0 to 1.0)

    Returns:
        ReviewDecision enum value
    """
    # Check for critical risks - always reject
    if analysis.has_critical_risks():
        return ReviewDecision.REJECT

    # Check for moderate risks - needs human review
    if analysis.has_moderate_risks():
        return ReviewDecision.NEEDS_REVIEW

    # Low/no risks - can auto-approve if confidence is high enough
    if analysis.risks:
        # Calculate average confidence from all risks
        avg_confidence = sum(risk.confidence for risk in analysis.risks) / len(analysis.risks)
        if avg_confidence >= auto_approve_threshold:
            return ReviewDecision.APPROVE
        else:
            return ReviewDecision.NEEDS_REVIEW

    # No risks detected - auto-approve
    return ReviewDecision.APPROVE
