#!/usr/bin/env python3
"""
Unit tests for Context Manager
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cag"))

from context_manager import ContextManager, UserContext


@pytest.mark.asyncio
async def test_build_context():
    """Test context building"""
    manager = ContextManager()

    context = await manager.build_context(
        user_id="test_user",
        session_id="test_session",
        query="How do I deploy containers?"
    )

    assert isinstance(context, UserContext)
    assert context.user_id == "test_user"
    assert context.session_id == "test_session"
    assert isinstance(context.domain_preferences, list)
    assert isinstance(context.interaction_history, list)
    assert isinstance(context.metadata, dict)


@pytest.mark.asyncio
async def test_analyze_domain_preferences():
    """Test domain preference analysis"""
    manager = ContextManager()

    history = [
        {'domains': ['ECO', 'PIPE']},
        {'domains': ['ECO']},
        {'domains': ['AXIS', 'ECO']},
    ]

    preferences = await manager._analyze_domain_preferences("test_user", history)

    assert isinstance(preferences, list)
    assert 'ECO' in preferences  # Most frequent
    assert len(preferences) <= 5


@pytest.mark.asyncio
async def test_cache_context():
    """Test context caching"""
    manager = ContextManager()

    context = UserContext(
        user_id="test_user",
        session_id="test_session",
        domain_preferences=['ECO'],
        interaction_history=[],
        metadata={}
    )

    await manager._cache_context("test_user", "test_session", context)

    # Check local cache
    cached = manager.context_cache.get("test_user:test_session")
    assert cached is not None
    assert cached.user_id == "test_user"


@pytest.mark.asyncio
async def test_update_interaction_history():
    """Test interaction history update"""
    manager = ContextManager()

    interaction = {
        'query': 'Test query',
        'domains': ['ECO'],
        'response_preview': 'Test response'
    }

    # Should not raise exception even without Redis
    await manager.update_interaction_history("test_user", interaction)


def test_user_context_to_dict():
    """Test UserContext to_dict conversion"""
    context = UserContext(
        user_id="test_user",
        session_id="test_session",
        domain_preferences=['ECO', 'PIPE'],
        interaction_history=[{'query': 'test'}],
        metadata={'timestamp': '2025-11-10'}
    )

    context_dict = context.to_dict()

    assert isinstance(context_dict, dict)
    assert context_dict['user_id'] == "test_user"
    assert context_dict['domain_preferences'] == ['ECO', 'PIPE']
