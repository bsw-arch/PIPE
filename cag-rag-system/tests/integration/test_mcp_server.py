#!/usr/bin/env python3
"""
Integration tests for MCP Server
"""

import pytest
import sys
from pathlib import Path
from httpx import AsyncClient

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp"))

from mcp_server import MCPServer


@pytest.fixture
def mcp_server():
    """Create MCP server instance"""
    server = MCPServer()
    return server


@pytest.mark.asyncio
async def test_health_endpoint(mcp_server):
    """Test health check endpoint"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data


@pytest.mark.asyncio
async def test_domains_endpoint(mcp_server):
    """Test domains listing endpoint"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        response = await client.get("/api/v1/domains")

        assert response.status_code == 200
        data = response.json()
        assert 'domains' in data
        assert len(data['domains']) == 4  # AXIS, PIPE, ECO, IV


@pytest.mark.asyncio
async def test_query_types_endpoint(mcp_server):
    """Test query types endpoint"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        response = await client.get("/api/v1/query-types")

        assert response.status_code == 200
        data = response.json()
        assert 'query_types' in data
        assert len(data['query_types']) > 0


@pytest.mark.asyncio
async def test_process_query_endpoint(mcp_server):
    """Test query processing endpoint"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        request = {
            "query": "How do I optimize ECO resources?",
            "user_id": "test_user",
            "session_id": "test_session"
        }

        response = await client.post("/api/v1/query", json=request)

        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        assert 'metadata' in data
        assert 'sources' in data
        assert 'confidence' in data
        assert data['confidence'] > 0


@pytest.mark.asyncio
async def test_classify_endpoint(mcp_server):
    """Test query classification endpoint"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        request = {
            "query": "Deploy containers to Kubernetes",
            "user_id": "test_user",
            "session_id": "test_session"
        }

        response = await client.post("/api/v1/classify", json=request)

        assert response.status_code == 200
        data = response.json()
        assert 'query_type' in data
        assert 'target_domains' in data
        assert len(data['target_domains']) > 0


@pytest.mark.asyncio
async def test_query_with_specific_domains(mcp_server):
    """Test query with specific domain targeting"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        request = {
            "query": "Test query",
            "user_id": "test_user",
            "session_id": "test_session",
            "domains": ["ECO", "PIPE"]
        }

        response = await client.post("/api/v1/query", json=request)

        assert response.status_code == 200
        data = response.json()
        assert 'ECO' in data['metadata']['domains']
        assert 'PIPE' in data['metadata']['domains']


@pytest.mark.asyncio
async def test_invalid_query_request(mcp_server):
    """Test handling of invalid query request"""
    async with AsyncClient(app=mcp_server.app, base_url="http://test") as client:
        # Missing required fields
        request = {
            "query": "Test query"
            # Missing user_id and session_id
        }

        response = await client.post("/api/v1/query", json=request)

        assert response.status_code == 422  # Validation error
