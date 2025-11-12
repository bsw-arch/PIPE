#!/usr/bin/env python3
"""
CAG Layer Service - Context-Aware Generation
Handles user context, query classification, and domain routing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from context_manager import ContextManager, UserContext
from query_classifier import QueryClassifier, QueryType
from domain_router import DomainRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="CAG Layer Service",
    description="Context-Aware Generation for 2-Tier CAG+RAG System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Global components (initialized on startup)
context_manager: Optional[ContextManager] = None
query_classifier: Optional[QueryClassifier] = None
domain_router: Optional[DomainRouter] = None


# Request/Response Models
class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I build a CAG+RAG system?",
                "user_id": "user_123",
                "session_id": "sess_456",
                "domains": ["PIPE", "IV"]
            }
        }


class CAGResponse(BaseModel):
    """CAG processing response"""
    query_type: str
    target_domains: List[str]
    context: Dict[str, Any]
    routing_info: Dict[str, Any]
    processing_time_ms: float
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global context_manager, query_classifier, domain_router

    logger.info("Starting CAG Layer Service...")

    # Initialize Context Manager
    context_manager = ContextManager(
        db_url="postgresql://postgres:changeme@postgresql:5432/cag_db",
        redis_url="redis://:changeme@redis-master:6379/0"
    )
    await context_manager.initialise()
    logger.info("✓ Context Manager initialized")

    # Initialize Query Classifier
    query_classifier = QueryClassifier(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    await query_classifier.initialise()
    logger.info("✓ Query Classifier initialized")

    # Initialize Domain Router
    domain_router = DomainRouter(
        kafka_brokers=["cag-rag-kafka-kafka-bootstrap.kafka:9092"]
    )
    await domain_router.initialise()
    logger.info("✓ Domain Router initialized")

    logger.info("CAG Layer Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CAG Layer Service...")

    if context_manager:
        await context_manager.close()

    if domain_router:
        await domain_router.close()

    logger.info("CAG Layer Service stopped")


@app.post("/api/v1/process", response_model=CAGResponse)
async def process_query(request: QueryRequest):
    """
    Process query through CAG layer

    Steps:
    1. Build user context
    2. Classify query type
    3. Detect target domains
    4. Route to appropriate services
    """
    start_time = datetime.utcnow()

    try:
        # Step 1: Build Context
        logger.info(f"Processing query for user {request.user_id}")

        context = await context_manager.build_context(
            user_id=request.user_id,
            session_id=request.session_id,
            query=request.query
        )

        # Step 2: Classify Query
        query_type, detected_domains = await query_classifier.classify_query(
            query=request.query,
            context=context
        )

        # Override with requested domains if provided
        target_domains = request.domains if request.domains else detected_domains

        # Step 3: Route to Domains
        routing_info = await domain_router.route_query(
            query=request.query,
            target_domains=target_domains,
            context=context
        )

        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Log metrics
        logger.info(
            f"Query processed in {processing_time:.2f}ms - "
            f"Type: {query_type.value}, Domains: {target_domains}"
        )

        return CAGResponse(
            query_type=query_type.value,
            target_domains=target_domains,
            context={
                'user_id': context.user_id,
                'session_id': context.session_id,
                'preferences': context.domain_preferences,
                'interaction_count': len(context.interaction_history),
                'metadata': context.metadata
            },
            routing_info=routing_info,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"CAG processing failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cag-layer",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "context_manager": context_manager is not None,
            "query_classifier": query_classifier is not None,
            "domain_router": domain_router is not None
        }
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if not all([context_manager, query_classifier, domain_router]):
        raise HTTPException(status_code=503, detail="Service not ready")

    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Metrics are exposed by Instrumentator
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
