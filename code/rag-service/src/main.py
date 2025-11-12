#!/usr/bin/env python3
"""
RAG Layer Service - Retrieval-Augmented Generation
Handles hybrid retrieval and Llama-based generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from vector_store import VectorStore
from llm_interface import LlamaInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RAG Layer Service",
    description="Retrieval-Augmented Generation with Llama-2",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Global components
vector_store: Optional[VectorStore] = None
llm: Optional[LlamaInterface] = None


# Request/Response Models
class RetrievalRequest(BaseModel):
    query: str
    domain: str
    top_k: Optional[int] = 10
    min_score: Optional[float] = 0.3

class GenerationRequest(BaseModel):
    query: str
    domain: str
    context: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 10
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7

class RAGResponse(BaseModel):
    query: str
    response: str
    retrieved_knowledge: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time_ms: float


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, llm

    logger.info("Starting RAG Layer Service...")

    # Initialize Vector Store
    vector_store = VectorStore(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        dimension=384,
        index_type="IP"  # Inner product for cosine similarity
    )
    await vector_store.initialise()

    # Load pre-indexed documents if available
    try:
        vector_store.load("/data/vector_store")
        logger.info("✓ Loaded existing vector store")
    except Exception as e:
        logger.info("No existing vector store found, starting fresh")

    # Initialize Llama model
    llm = LlamaInterface(
        model_name="meta-llama/Llama-2-7b-chat-hf",
        use_4bit=True,  # 4-bit quantization for 48GB RAM
        device="auto"
    )
    await llm.initialise()
    logger.info("✓ Llama model loaded")

    logger.info("RAG Layer Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down RAG Layer Service...")

    # Save vector store
    if vector_store:
        try:
            vector_store.save("/data/vector_store")
            logger.info("✓ Vector store saved")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    logger.info("RAG Layer Service stopped")


@app.post("/api/v1/retrieve")
async def retrieve(request: RetrievalRequest):
    """
    Retrieve relevant knowledge without generation
    """
    start_time = datetime.utcnow()

    try:
        # Perform vector search
        results = vector_store.search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            "query": request.query,
            "domain": request.domain,
            "results": results,
            "count": len(results),
            "processing_time_ms": processing_time
        }

    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate", response_model=RAGResponse)
async def generate(request: GenerationRequest):
    """
    Full RAG pipeline: Retrieve + Generate with Llama
    """
    start_time = datetime.utcnow()

    try:
        logger.info(f"Processing RAG request for: {request.query[:100]}")

        # Step 1: Retrieve relevant knowledge
        retrieved_knowledge = vector_store.search(
            query=request.query,
            top_k=request.top_k,
            min_score=0.3
        )

        logger.info(f"Retrieved {len(retrieved_knowledge)} knowledge pieces")

        # Step 2: Generate response with Llama
        response_text = await llm.generate_response(
            query=request.query,
            retrieved_knowledge=retrieved_knowledge,
            context=request.context,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(f"RAG pipeline completed in {processing_time:.2f}ms")

        return RAGResponse(
            query=request.query,
            response=response_text,
            retrieved_knowledge=retrieved_knowledge[:5],  # Top 5 for response
            metadata={
                "domain": request.domain,
                "knowledge_count": len(retrieved_knowledge),
                "model": llm.model_name,
                "timestamp": datetime.utcnow().isoformat()
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/index")
async def index_documents(documents: List[Dict[str, Any]]):
    """
    Index documents into vector store
    """
    try:
        vector_store.add_documents(documents)

        return {
            "status": "success",
            "indexed": len(documents),
            "total": vector_store.index.ntotal
        }

    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rag-layer",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "vector_store": vector_store is not None,
            "llm": llm is not None
        },
        "stats": {
            "vector_store": vector_store.get_stats() if vector_store else {},
            "llm": llm.get_model_info() if llm else {}
        }
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    if not all([vector_store, llm]):
        raise HTTPException(status_code=503, detail="Service not ready")

    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,  # Disable reload due to large model
        log_level="info"
    )
