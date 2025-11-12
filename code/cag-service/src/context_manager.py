"""
Context Manager - Manages user context for CAG processing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncpg
import redis.asyncio as redis
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
    """Manages context for CAG layer processing"""

    def __init__(self, db_url: str, redis_url: str, ttl: int = 3600):
        self.db_url = db_url
        self.redis_url = redis_url
        self.ttl = ttl
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None

    async def initialise(self):
        """Initialise database connections"""
        try:
            # PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20
            )

            # Create tables if not exist
            await self._create_tables()

            # Redis connection
            self.redis_client = await redis.from_url(
                self.redis_url,
                decode_responses=True
            )

            logger.info("Context Manager initialised successfully")

        except Exception as e:
            logger.error(f"Failed to initialise Context Manager: {e}")
            raise

    async def _create_tables(self):
        """Create database tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    query TEXT NOT NULL,
                    query_type VARCHAR(50),
                    domains TEXT[],
                    response_time_ms FLOAT,
                    success BOOLEAN DEFAULT true,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    metadata JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id
                ON user_interactions(user_id);

                CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp
                ON user_interactions(timestamp DESC);
            """)

    async def build_context(self,
                           user_id: str,
                           session_id: str,
                           query: str) -> UserContext:
        """Build comprehensive context for query processing"""

        # Try to get from cache first
        cache_key = f"context:{user_id}:{session_id}"
        cached_context = await self._get_from_cache(cache_key)

        if cached_context:
            logger.debug(f"Context cache hit for {user_id}")
            # Update with current query
            cached_context['metadata']['current_query'] = query
            cached_context['metadata']['timestamp'] = datetime.utcnow().isoformat()
            return UserContext(**cached_context)

        # Build fresh context
        history = await self._get_user_history(user_id)
        preferences = await self._analyse_domain_preferences(user_id, history)

        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'query_hash': self._hash_query(query),
            'session_start': await self._get_session_start(session_id),
            'interaction_count': len(history),
            'current_query': query
        }

        context = UserContext(
            user_id=user_id,
            session_id=session_id,
            domain_preferences=preferences,
            interaction_history=history[-10:],  # Last 10 interactions
            metadata=metadata
        )

        # Cache the context
        await self._cache_context(cache_key, context)

        return context

    async def _get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user interaction history"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        query,
                        query_type,
                        domains,
                        response_time_ms,
                        success,
                        timestamp,
                        metadata
                    FROM user_interactions
                    WHERE user_id = $1
                    AND timestamp > NOW() - INTERVAL '30 days'
                    ORDER BY timestamp DESC
                    LIMIT 50
                """, user_id)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error fetching user history: {e}")
            return []

    async def _analyse_domain_preferences(self,
                                         user_id: str,
                                         history: List[Dict]) -> List[str]:
        """Analyse and rank domain preferences based on history"""
        domain_counts = {}

        for interaction in history:
            domains = interaction.get('domains', [])
            if domains:
                for domain in domains:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Sort by frequency
        sorted_domains = sorted(
            domain_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [domain for domain, _ in sorted_domains[:5]]

    async def _get_session_start(self, session_id: str) -> str:
        """Get session start time"""
        cache_key = f"session:{session_id}:start"

        session_start = await self.redis_client.get(cache_key)

        if not session_start:
            session_start = datetime.utcnow().isoformat()
            await self.redis_client.set(
                cache_key,
                session_start,
                ex=86400  # 24 hours
            )

        return session_start

    async def store_interaction(self,
                               user_id: str,
                               session_id: str,
                               query: str,
                               query_type: str,
                               domains: List[str],
                               response_time_ms: float,
                               success: bool = True,
                               metadata: Dict[str, Any] = None):
        """Store user interaction"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_interactions
                    (user_id, session_id, query, query_type, domains,
                     response_time_ms, success, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                                 user_id, session_id, query, query_type,
                                 domains, response_time_ms, success,
                                 json.dumps(metadata) if metadata else None)

            # Invalidate cache
            cache_key = f"context:{user_id}:{session_id}"
            await self.redis_client.delete(cache_key)

        except Exception as e:
            logger.error(f"Error storing interaction: {e}")

    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from Redis cache"""
        try:
            cached = await self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read error: {e}")

        return None

    async def _cache_context(self, key: str, context: UserContext):
        """Cache context in Redis"""
        try:
            await self.redis_client.set(
                key,
                json.dumps(context.to_dict(), default=str),
                ex=self.ttl
            )
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def _hash_query(self, query: str) -> str:
        """Generate hash of query"""
        return hashlib.md5(query.encode()).hexdigest()[:16]

    async def close(self):
        """Close connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()

        logger.info("Context Manager closed")
