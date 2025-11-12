#!/usr/bin/env python3
"""
MCP Server - Master Control Plane
Orchestrates CAG + RAG pipeline
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CAG+RAG MCP Server",
    description="Master orchestrator for 2-tier CAG+RAG system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs (configured via environment)
CAG_SERVICE_URL = "http://cag-service:8001"
RAG_SERVICE_URL = "http://rag-service:8002"


class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7

class QueryResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]
    sources: List[Dict[str, Any]]
    confidence: float
    processing_breakdown: Dict[str, float]


@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Complete CAG+RAG pipeline

    Flow:
    1. CAG Layer: Build context, classify, route
    2. RAG Layer: Retrieve knowledge, generate response
    3. Return final response with metadata
    """
    start_time = datetime.utcnow()
    processing_breakdown = {}

    try:
        logger.info(f"Processing query for user {request.user_id}")

        # STEP 1: CAG Processing
        cag_start = datetime.utcnow()

        async with httpx.AsyncClient(timeout=30.0) as client:
            cag_response = await client.post(
                f"{CAG_SERVICE_URL}/api/v1/process",
                json={
                    "query": request.query,
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "domains": request.domains
                }
            )
            cag_response.raise_for_status()
            cag_data = cag_response.json()

        processing_breakdown['cag_ms'] = cag_data['processing_time_ms']
        target_domains = cag_data['target_domains']

        logger.info(f"CAG complete - Domains: {target_domains}")

        # STEP 2: RAG Processing
        rag_start = datetime.utcnow()

        # Generate response using first domain
        # (In production, you might aggregate across domains)
        primary_domain = target_domains[0] if target_domains else "PIPE"

        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for LLM
            rag_response = await client.post(
                f"{RAG_SERVICE_URL}/api/v1/generate",
                json={
                    "query": request.query,
                    "domain": primary_domain,
                    "context": cag_data['context'],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )
            rag_response.raise_for_status()
            rag_data = rag_response.json()

        processing_breakdown['rag_ms'] = rag_data['processing_time_ms']

        logger.info(f"RAG complete - Generated {len(rag_data['response'])} chars")

        # Calculate total processing time
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        processing_breakdown['total_ms'] = total_time

        # Calculate confidence based on retrieval scores
        confidence = calculate_confidence(rag_data['retrieved_knowledge'])

        return QueryResponse(
            response=rag_data['response'],
            metadata={
                'query_type': cag_data['query_type'],
                'domains': target_domains,
                'model': rag_data['metadata'].get('model', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'knowledge_count': rag_data['metadata'].get('knowledge_count', 0)
            },
            sources=rag_data['retrieved_knowledge'],
            confidence=confidence,
            processing_breakdown=processing_breakdown
        )

    except httpx.HTTPError as e:
        logger.error(f"HTTP error in pipeline: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Service communication error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline processing failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check - verifies all services
    """
    status = {
        "mcp_server": "healthy",
        "cag_service": "unknown",
        "rag_service": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check CAG service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CAG_SERVICE_URL}/health")
            if response.status_code == 200:
                status["cag_service"] = "healthy"
    except Exception as e:
        status["cag_service"] = f"unhealthy: {str(e)}"

    # Check RAG service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RAG_SERVICE_URL}/health")
            if response.status_code == 200:
                status["rag_service"] = "healthy"
    except Exception as e:
        status["rag_service"] = f"unhealthy: {str(e)}"

    # Overall status
    if all(v == "healthy" for v in status.values() if v != status["timestamp"]):
        return status
    else:
        raise HTTPException(status_code=503, detail=status)


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # Check if downstream services are ready
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            cag_ready = await client.get(f"{CAG_SERVICE_URL}/ready")
            rag_ready = await client.get(f"{RAG_SERVICE_URL}/ready")

            if cag_ready.status_code == 200 and rag_ready.status_code == 200:
                return {"status": "ready"}
            else:
                raise HTTPException(status_code=503, detail="Services not ready")

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")


def calculate_confidence(knowledge: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence score based on retrieved knowledge

    Returns: Float between 0.0 and 1.0
    """
    if not knowledge:
        return 0.0

    # Average of top 3 scores
    top_scores = [k.get('score', 0.0) for k in knowledge[:3]]

    if not top_scores:
        return 0.0

    avg_score = sum(top_scores) / len(top_scores)

    # Adjust based on number of results
    result_factor = min(len(knowledge) / 5.0, 1.0)  # Prefer more results

    confidence = avg_score * 0.8 + result_factor * 0.2

    return round(confidence, 2)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
