#!/usr/bin/env python3
"""
Unit tests for Hybrid Retrieval Engine
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rag"))

from hybrid_retrieval_engine import HybridRetrievalEngine


@pytest.mark.asyncio
async def test_hybrid_search():
    """Test hybrid search"""
    engine = HybridRetrievalEngine()

    results = await engine.hybrid_search(
        query="How do I optimize resources?",
        domain="ECO",
        top_k=5
    )

    assert isinstance(results, list)
    assert len(results) <= 5
    if len(results) > 0:
        assert 'id' in results[0]
        assert 'score' in results[0]
        assert 'final_score' in results[0]


@pytest.mark.asyncio
async def test_mock_vector_search():
    """Test mock vector search"""
    engine = HybridRetrievalEngine()

    results = await engine._mock_vector_search(
        query="test query",
        domain="ECO",
        top_k=5
    )

    assert isinstance(results, list)
    assert len(results) == 5
    assert results[0]['type'] == 'vector'
    assert results[0]['score'] > results[-1]['score']  # Descending order


@pytest.mark.asyncio
async def test_mock_graph_search():
    """Test mock graph search"""
    engine = HybridRetrievalEngine()

    results = await engine._mock_graph_search(
        query="test query",
        domain="PIPE",
        top_k=5
    )

    assert isinstance(results, list)
    assert len(results) == 5
    assert results[0]['type'] == 'graph'
    assert 'entity' in results[0]['content']


@pytest.mark.asyncio
async def test_mock_document_search():
    """Test mock document search"""
    engine = HybridRetrievalEngine()

    results = await engine._mock_document_search(
        query="test query",
        domain="AXIS",
        top_k=5
    )

    assert isinstance(results, list)
    assert len(results) == 5
    assert results[0]['type'] == 'document'
    assert 'text' in results[0]['content']


@pytest.mark.asyncio
async def test_fuse_results():
    """Test result fusion"""
    engine = HybridRetrievalEngine()

    vector_results = [{'id': 'v1', 'score': 0.9, 'type': 'vector'}]
    graph_results = [{'id': 'g1', 'score': 0.8, 'type': 'graph'}]
    document_results = [{'id': 'd1', 'score': 0.7, 'type': 'document'}]

    fused = await engine._fuse_results(
        vector_results,
        graph_results,
        document_results
    )

    assert isinstance(fused, list)
    assert len(fused) == 3
    assert all('final_score' in r for r in fused)
    assert fused[0]['final_score'] >= fused[1]['final_score']  # Sorted


def test_update_fusion_weights():
    """Test updating fusion weights"""
    engine = HybridRetrievalEngine()

    new_weights = {
        'vector': 0.5,
        'graph': 0.3,
        'document': 0.2
    }

    engine.update_fusion_weights(new_weights)

    assert engine.fusion_weights == new_weights


def test_default_config():
    """Test default configuration"""
    engine = HybridRetrievalEngine()

    assert 'embedding_model' in engine.config
    assert 'fusion_weights' in engine.config
    assert sum(engine.fusion_weights.values()) == pytest.approx(1.0, 0.01)
