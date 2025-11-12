#!/usr/bin/env python3
"""
BSW-Arch CAG Layer - Context Manager
Manages context for Context-Aware Generation processing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """User context for CAG processing"""
    user_id: str
    session_id: str
    domain_preferences: List[str]
    interaction_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ContextManager:
    """
    Manages context for CAG layer processing

    Responsibilities:
    - User history management
    - Domain preference analysis
    - Session tracking
    - Metadata extraction
    """

    def __init__(self, redis_client=None, ttl: int = 3600):
        """
        Initialize Context Manager

        Args:
            redis_client: Redis client for caching (optional)
            ttl: Time-to-live for cached context (seconds)
        """
        self.redis_client = redis_client
        self.ttl = ttl
        self.context_cache = {}

        logger.info("Context Manager initialized")

    async def build_context(self,
                           user_id: str,
                           session_id: str,
                           query: str) -> UserContext:
        """
        Build comprehensive context for query processing

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User query

        Returns:
            UserContext with history, preferences, and metadata
        """
        logger.info(f"Building context for user {user_id}, session {session_id}")

        # Retrieve user history
        history = await self._get_user_history(user_id)

        # Analyze domain preferences
        domain_preferences = await self._analyze_domain_preferences(
            user_id, history
        )

        # Extract metadata
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'query_hash': hashlib.md5(query.encode()).hexdigest(),
            'session_start': await self._get_session_start(session_id),
            'interaction_count': len(history),
            'query_length': len(query)
        }

        context = UserContext(
            user_id=user_id,
            session_id=session_id,
            domain_preferences=domain_preferences,
            interaction_history=history[-10:],  # Last 10 interactions
            metadata=metadata
        )

        # Cache context
        await self._cache_context(user_id, session_id, context)

        logger.info(
            f"Context built: {len(domain_preferences)} preferences, "
            f"{len(history)} interactions"
        )

        return context

    async def _get_user_history(self, user_id: str) -> List[Dict]:
        """
        Retrieve user interaction history

        Args:
            user_id: User identifier

        Returns:
            List of interaction dictionaries
        """
        if self.redis_client:
            try:
                history_key = f"user:history:{user_id}"
                history_json = await self.redis_client.get(history_key)
                if history_json:
                    return json.loads(history_json)
            except Exception as e:
                logger.error(f"Error retrieving user history from Redis: {e}")

        return []

    async def _analyze_domain_preferences(self,
                                         user_id: str,
                                         history: List[Dict]) -> List[str]:
        """
        Analyze and rank domain preferences based on history

        Args:
            user_id: User identifier
            history: User interaction history

        Returns:
            Ranked list of domain preferences
        """
        domain_counts = {}

        for interaction in history:
            domains = interaction.get('domains', [])
            for domain in domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Sort by frequency
        sorted_domains = sorted(
            domain_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 5 domains
        preferences = [domain for domain, _ in sorted_domains[:5]]

        logger.debug(f"Domain preferences for {user_id}: {preferences}")

        return preferences

    async def _get_session_start(self, session_id: str) -> str:
        """
        Get session start timestamp

        Args:
            session_id: Session identifier

        Returns:
            ISO format timestamp
        """
        if self.redis_client:
            try:
                session_key = f"session:start:{session_id}"
                session_start = await self.redis_client.get(session_key)
                if session_start:
                    return session_start.decode('utf-8')
            except Exception as e:
                logger.error(f"Error retrieving session start: {e}")

        # Default to current time if not found
        return datetime.utcnow().isoformat()

    async def _cache_context(self,
                           user_id: str,
                           session_id: str,
                           context: UserContext):
        """
        Cache context for future use

        Args:
            user_id: User identifier
            session_id: Session identifier
            context: User context to cache
        """
        cache_key = f"{user_id}:{session_id}"

        # Local cache
        self.context_cache[cache_key] = context

        # Redis cache
        if self.redis_client:
            try:
                redis_key = f"context:{cache_key}"
                context_json = json.dumps(context.to_dict())
                await self.redis_client.set(
                    redis_key,
                    context_json,
                    ex=self.ttl
                )
            except Exception as e:
                logger.error(f"Error caching context to Redis: {e}")

    async def get_cached_context(self,
                                user_id: str,
                                session_id: str) -> Optional[UserContext]:
        """
        Retrieve cached context

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Cached UserContext or None
        """
        cache_key = f"{user_id}:{session_id}"

        # Check local cache
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]

        # Check Redis cache
        if self.redis_client:
            try:
                redis_key = f"context:{cache_key}"
                context_json = await self.redis_client.get(redis_key)
                if context_json:
                    context_dict = json.loads(context_json)
                    return UserContext(**context_dict)
            except Exception as e:
                logger.error(f"Error retrieving cached context: {e}")

        return None

    async def update_interaction_history(self,
                                       user_id: str,
                                       interaction: Dict[str, Any]):
        """
        Update user interaction history

        Args:
            user_id: User identifier
            interaction: Interaction data to add
        """
        if not self.redis_client:
            return

        try:
            history_key = f"user:history:{user_id}"

            # Get current history
            history_json = await self.redis_client.get(history_key)
            history = json.loads(history_json) if history_json else []

            # Add new interaction
            history.append({
                **interaction,
                'timestamp': datetime.utcnow().isoformat()
            })

            # Keep last 100 interactions
            history = history[-100:]

            # Save updated history
            await self.redis_client.set(
                history_key,
                json.dumps(history),
                ex=self.ttl * 24  # Keep for 24 hours
            )

            logger.debug(f"Updated interaction history for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating interaction history: {e}")

    def clear_cache(self):
        """Clear local context cache"""
        self.context_cache.clear()
        logger.info("Local context cache cleared")
