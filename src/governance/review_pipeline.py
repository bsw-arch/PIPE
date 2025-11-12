"""Review pipeline for cross-domain integration governance.

Implements the review orchestration system from PIPE AgenticAI
Governance Architecture.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ReviewStatus(Enum):
    """Review status states."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"
    CANCELLED = "cancelled"


class ReviewType(Enum):
    """Types of reviews."""

    INTEGRATION = "integration"
    SECURITY = "security"
    QUALITY = "quality"
    ARCHITECTURE = "architecture"
    COMPLIANCE = "compliance"


class ReviewPriority(Enum):
    """Review priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewPipeline:
    """
    Manages cross-domain review processes and coordination.

    Implements the Review Pipeline component from PIPE AgenticAI
    Governance Architecture for coordinating reviews across domains.
    """

    def __init__(self):
        """Initialize the review pipeline."""
        self.logger = logging.getLogger("pipe.governance.review_pipeline")
        self.reviews: Dict[str, Dict[str, Any]] = {}
        self.review_queue: List[str] = []
        self.review_counter = 0

    def create_review(
        self,
        title: str,
        review_type: ReviewType,
        source_domain: str,
        target_domain: str,
        description: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Create a new review request.

        Args:
            title: Review title
            review_type: Type of review
            source_domain: Source domain code
            target_domain: Target domain code
            description: Detailed description
            priority: Review priority
            metadata: Additional metadata

        Returns:
            Review ID
        """
        self.review_counter += 1
        review_id = f"REV-{self.review_counter:06d}"

        review = {
            "id": review_id,
            "title": title,
            "type": review_type,
            "source_domain": source_domain,
            "target_domain": target_domain,
            "description": description,
            "priority": priority,
            "status": ReviewStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system",
            "reviewers": [],
            "comments": [],
            "approvals": [],
            "changes_requested": [],
            "metadata": metadata or {},
            "timeline": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event": "created",
                    "details": f"Review created with priority {priority.value}",
                }
            ],
        }

        self.reviews[review_id] = review
        self.review_queue.append(review_id)

        self.logger.info(
            f"Created review {review_id}: {title} ({source_domain} → {target_domain})"
        )

        return review_id

    def assign_reviewers(self, review_id: str, reviewers: List[str]) -> bool:
        """
        Assign reviewers to a review.

        Args:
            review_id: Review identifier
            reviewers: List of reviewer identifiers

        Returns:
            True if assignment successful
        """
        if review_id not in self.reviews:
            self.logger.error(f"Review not found: {review_id}")
            return False

        review = self.reviews[review_id]
        review["reviewers"] = reviewers
        review["status"] = ReviewStatus.IN_REVIEW
        review["updated_at"] = datetime.now().isoformat()

        review["timeline"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "reviewers_assigned",
                "details": f"Assigned {len(reviewers)} reviewers",
            }
        )

        self.logger.info(f"Assigned {len(reviewers)} reviewers to review {review_id}")
        return True

    def add_comment(self, review_id: str, reviewer: str, comment: str) -> bool:
        """
        Add a comment to a review.

        Args:
            review_id: Review identifier
            reviewer: Reviewer identifier
            comment: Comment text

        Returns:
            True if comment added
        """
        if review_id not in self.reviews:
            self.logger.error(f"Review not found: {review_id}")
            return False

        review = self.reviews[review_id]
        comment_entry = {
            "reviewer": reviewer,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
        }

        review["comments"].append(comment_entry)
        review["updated_at"] = datetime.now().isoformat()

        self.logger.debug(f"Added comment to review {review_id} from {reviewer}")
        return True

    def request_changes(
        self, review_id: str, reviewer: str, changes: List[str]
    ) -> bool:
        """
        Request changes on a review.

        Args:
            review_id: Review identifier
            reviewer: Reviewer identifier
            changes: List of requested changes

        Returns:
            True if changes requested
        """
        if review_id not in self.reviews:
            self.logger.error(f"Review not found: {review_id}")
            return False

        review = self.reviews[review_id]
        review["status"] = ReviewStatus.REQUIRES_CHANGES
        review["updated_at"] = datetime.now().isoformat()

        change_request = {
            "reviewer": reviewer,
            "changes": changes,
            "timestamp": datetime.now().isoformat(),
        }

        review["changes_requested"].append(change_request)

        review["timeline"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "changes_requested",
                "details": f"{reviewer} requested {len(changes)} changes",
            }
        )

        self.logger.info(
            f"Changes requested on review {review_id} by {reviewer}: {len(changes)} items"
        )
        return True

    def approve_review(self, review_id: str, reviewer: str, notes: str = None) -> bool:
        """
        Approve a review.

        Args:
            review_id: Review identifier
            reviewer: Reviewer identifier
            notes: Optional approval notes

        Returns:
            True if approval recorded
        """
        if review_id not in self.reviews:
            self.logger.error(f"Review not found: {review_id}")
            return False

        review = self.reviews[review_id]

        approval = {
            "reviewer": reviewer,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
        }

        review["approvals"].append(approval)
        review["updated_at"] = datetime.now().isoformat()

        # Check if all reviewers have approved
        if len(review["approvals"]) >= len(review["reviewers"]):
            review["status"] = ReviewStatus.APPROVED
            review["timeline"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "event": "approved",
                    "details": "All reviewers approved",
                }
            )
            self.logger.info(f"Review {review_id} fully approved")
        else:
            self.logger.info(
                f"Review {review_id} approved by {reviewer} "
                f"({len(review['approvals'])}/{len(review['reviewers'])})"
            )

        return True

    def reject_review(self, review_id: str, reviewer: str, reason: str) -> bool:
        """
        Reject a review.

        Args:
            review_id: Review identifier
            reviewer: Reviewer identifier
            reason: Rejection reason

        Returns:
            True if rejection recorded
        """
        if review_id not in self.reviews:
            self.logger.error(f"Review not found: {review_id}")
            return False

        review = self.reviews[review_id]
        review["status"] = ReviewStatus.REJECTED
        review["updated_at"] = datetime.now().isoformat()

        review["timeline"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "rejected",
                "details": f"Rejected by {reviewer}: {reason}",
            }
        )

        self.logger.info(f"Review {review_id} rejected by {reviewer}")
        return True

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review details."""
        return self.reviews.get(review_id)

    def list_reviews(
        self,
        status: ReviewStatus = None,
        review_type: ReviewType = None,
        domain: str = None,
    ) -> List[Dict[str, Any]]:
        """
        List reviews with optional filtering.

        Args:
            status: Filter by status
            review_type: Filter by type
            domain: Filter by source or target domain

        Returns:
            List of review records
        """
        reviews = list(self.reviews.values())

        if status:
            reviews = [r for r in reviews if r["status"] == status]

        if review_type:
            reviews = [r for r in reviews if r["type"] == review_type]

        if domain:
            reviews = [
                r
                for r in reviews
                if r["source_domain"] == domain or r["target_domain"] == domain
            ]

        return reviews

    def get_review_metrics(self) -> Dict[str, Any]:
        """
        Get review pipeline metrics.

        Returns:
            Dictionary of metrics
        """
        total_reviews = len(self.reviews)

        status_counts = {}
        for status in ReviewStatus:
            count = len([r for r in self.reviews.values() if r["status"] == status])
            status_counts[status.value] = count

        type_counts = {}
        for review_type in ReviewType:
            count = len([r for r in self.reviews.values() if r["type"] == review_type])
            type_counts[review_type.value] = count

        # Calculate average review time for completed reviews
        completed = [
            r
            for r in self.reviews.values()
            if r["status"] in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]
        ]

        return {
            "total_reviews": total_reviews,
            "pending": status_counts.get(ReviewStatus.PENDING.value, 0),
            "in_review": status_counts.get(ReviewStatus.IN_REVIEW.value, 0),
            "approved": status_counts.get(ReviewStatus.APPROVED.value, 0),
            "rejected": status_counts.get(ReviewStatus.REJECTED.value, 0),
            "requires_changes": status_counts.get(
                ReviewStatus.REQUIRES_CHANGES.value, 0
            ),
            "by_type": type_counts,
            "completed_reviews": len(completed),
        }
