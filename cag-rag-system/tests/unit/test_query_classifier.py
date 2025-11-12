#!/usr/bin/env python3
"""
Unit tests for Query Classifier
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cag"))

from query_classifier import QueryClassifier, QueryType


@pytest.mark.asyncio
async def test_classify_query_eco():
    """Test query classification for ECO domain"""
    classifier = QueryClassifier(use_transformers=False)

    query = "How do I optimize resource usage in Kubernetes?"
    query_type, domains = await classifier.classify_query(query)

    assert isinstance(query_type, QueryType)
    assert 'ECO' in domains


@pytest.mark.asyncio
async def test_classify_query_pipe():
    """Test query classification for PIPE domain"""
    classifier = QueryClassifier(use_transformers=False)

    query = "Set up a CI/CD pipeline for deployment"
    query_type, domains = await classifier.classify_query(query)

    assert isinstance(query_type, QueryType)
    assert 'PIPE' in domains


@pytest.mark.asyncio
async def test_classify_query_axis():
    """Test query classification for AXIS domain"""
    classifier = QueryClassifier(use_transformers=False)

    query = "Design a microservices architecture"
    query_type, domains = await classifier.classify_query(query)

    assert isinstance(query_type, QueryType)
    assert 'AXIS' in domains


@pytest.mark.asyncio
async def test_classify_query_type_informational():
    """Test query type classification - informational"""
    classifier = QueryClassifier(use_transformers=False)

    query = "What is the status of the deployment?"
    query_type, _ = await classifier.classify_query(query)

    assert query_type == QueryType.INFORMATIONAL


@pytest.mark.asyncio
async def test_classify_query_type_transactional():
    """Test query type classification - transactional"""
    classifier = QueryClassifier(use_transformers=False)

    query = "Deploy the application to production"
    query_type, _ = await classifier.classify_query(query)

    assert query_type == QueryType.TRANSACTIONAL


@pytest.mark.asyncio
async def test_classify_query_type_analytical():
    """Test query type classification - analytical"""
    classifier = QueryClassifier(use_transformers=False)

    query = "Analyze the performance metrics and compare"
    query_type, _ = await classifier.classify_query(query)

    assert query_type == QueryType.ANALYTICAL


@pytest.mark.asyncio
async def test_multiple_domains():
    """Test classification with multiple domains"""
    classifier = QueryClassifier(use_transformers=False)

    query = "Deploy containers to kubernetes infrastructure"
    query_type, domains = await classifier.classify_query(query)

    # Should detect both PIPE (deploy) and ECO (kubernetes)
    assert len(domains) > 0
    assert any(d in ['PIPE', 'ECO'] for d in domains)


def test_add_domain_pattern():
    """Test adding custom domain pattern"""
    classifier = QueryClassifier(use_transformers=False)

    classifier.add_domain_pattern('ECO', r'\boptimize\b')

    assert len(classifier.domain_patterns['ECO']) > 0


def test_get_domain_keywords():
    """Test getting domain keywords"""
    classifier = QueryClassifier(use_transformers=False)

    keywords = classifier.get_domain_keywords('ECO')

    assert isinstance(keywords, list)
    assert len(keywords) > 0
