#!/usr/bin/env python3
"""
Shared Pydantic Models
Used across CAG, RAG, and MCP services
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class QueryType(str, Enum):
    """Query classification types"""
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    GENERATIVE = "generative"


class Domain(str, Enum):
    """BSW-Tech domains"""
    PIPE = "PIPE"  # Process Integration & Pipeline Engineering
    IV = "IV"      # Information Verification
    AXIS = "AXIS"  # Architecture
    BNI = "BNI"    # Business Network Infrastructure
    BNP = "BNP"    # Business Network Platforms
    ECO = "ECO"    # Ecosystem
    DC = "DC"      # Data Centre
    BU = "BU"      # Business Unit


class RetrievalMethod(str, Enum):
    """Knowledge retrieval methods"""
    VECTOR = "vector"
    GRAPH = "graph"
    HYBRID = "hybrid"
    KEYWORD = "keyword"


# ============================================================================
# Request Models
# ============================================================================

class QueryRequest(BaseModel):
    """Base query request model"""
    query: str = Field(..., description="User query text")
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Session identifier")
    domains: Optional[List[str]] = Field(None, description="Target domains")
    max_tokens: Optional[int] = Field(512, ge=50, le=2048, description="Max generation tokens")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Generation temperature")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "How do I implement CAG+RAG architecture?",
                "user_id": "user_123",
                "session_id": "sess_456",
                "domains": ["PIPE", "AXIS"],
                "max_tokens": 512,
                "temperature": 0.7
            }
        }
    )


class CAGProcessRequest(BaseModel):
    """CAG layer processing request"""
    query: str
    user_id: str
    session_id: str
    domains: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class RAGGenerationRequest(BaseModel):
    """RAG layer generation request"""
    query: str
    domain: str = "PIPE"
    context: Optional[Dict[str, Any]] = None
    max_tokens: int = 512
    temperature: float = 0.7
    top_k: int = 10
    retrieval_method: RetrievalMethod = RetrievalMethod.HYBRID


# ============================================================================
# Response Models
# ============================================================================

class KnowledgeSource(BaseModel):
    """Single knowledge source/reference"""
    content: str = Field(..., description="Knowledge content")
    source: str = Field(..., description="Source identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Source metadata")
    doc_id: Optional[str] = Field(None, description="Document ID")
    chunk_id: Optional[str] = Field(None, description="Chunk ID")


class CAGResponse(BaseModel):
    """CAG layer response"""
    query_type: str = Field(..., description="Classified query type")
    target_domains: List[str] = Field(..., description="Target domains")
    context: Dict[str, Any] = Field(..., description="User context")
    routing_info: Dict[str, Any] = Field(..., description="Routing information")
    processing_time_ms: float = Field(..., description="Processing time in ms")
    timestamp: str = Field(..., description="Response timestamp")


class RAGResponse(BaseModel):
    """RAG layer response"""
    response: str = Field(..., description="Generated response")
    retrieved_knowledge: List[Dict[str, Any]] = Field(..., description="Retrieved sources")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")
    processing_time_ms: float = Field(..., description="Processing time in ms")
    timestamp: str = Field(..., description="Response timestamp")


class QueryResponse(BaseModel):
    """Complete query response from MCP"""
    response: str = Field(..., description="Final generated response")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    sources: List[Dict[str, Any]] = Field(..., description="Knowledge sources")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    processing_breakdown: Dict[str, float] = Field(..., description="Processing time breakdown")


# ============================================================================
# Context Models
# ============================================================================

class UserContext(BaseModel):
    """User context information"""
    user_id: str
    session_id: str
    domain_preferences: Dict[str, float] = Field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionContext(BaseModel):
    """Session-level context"""
    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    query_count: int = 0
    domains_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Knowledge Models
# ============================================================================

class DocumentMetadata(BaseModel):
    """Document metadata for indexing"""
    doc_id: str
    title: str
    domain: Domain
    source: str
    created_at: datetime
    indexed_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    """Single knowledge chunk for vector store"""
    chunk_id: str
    doc_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    domain: Domain
    chunk_index: int


class Entity(BaseModel):
    """Entity for knowledge graph"""
    name: str
    type: str
    domain: Domain
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    """Relationship between entities"""
    from_entity: str
    to_entity: str
    relationship_type: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    properties: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Health & Monitoring Models
# ============================================================================

class HealthStatus(BaseModel):
    """Service health status"""
    status: str = Field(..., description="Health status: healthy/unhealthy")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Check timestamp")
    components: Optional[Dict[str, Any]] = Field(None, description="Component statuses")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class MetricsSnapshot(BaseModel):
    """Service metrics snapshot"""
    service: str
    timestamp: datetime
    queries_total: int
    queries_per_second: float
    avg_latency_ms: float
    error_rate: float
    active_sessions: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Configuration Models
# ============================================================================

class ServiceConfig(BaseModel):
    """Base service configuration"""
    service_name: str
    host: str = "0.0.0.0"
    port: int
    log_level: str = "INFO"
    environment: str = "development"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CAGConfig(ServiceConfig):
    """CAG service configuration"""
    db_url: str
    redis_url: str
    kafka_brokers: List[str]
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class RAGConfig(ServiceConfig):
    """RAG service configuration"""
    vector_db_path: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    llm_model: str = "meta-llama/Llama-2-7b-chat-hf"
    use_4bit_quantization: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"


class MCPConfig(ServiceConfig):
    """MCP service configuration"""
    cag_service_url: str
    rag_service_url: str
    timeout_seconds: int = 120


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: Optional[str] = Field(None, description="Request identifier")


# ============================================================================
# Utility Functions
# ============================================================================

def create_timestamp() -> str:
    """Create ISO format timestamp"""
    return datetime.utcnow().isoformat()


def validate_domain(domain: str) -> bool:
    """Validate domain string against Domain enum"""
    try:
        Domain(domain)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    # Test model creation
    query = QueryRequest(
        query="Test query",
        user_id="user_123",
        session_id="sess_456",
        domains=["PIPE", "AXIS"]
    )
    print(f"Query model: {query.model_dump_json(indent=2)}")

    health = HealthStatus(
        status="healthy",
        service="test-service",
        timestamp=create_timestamp()
    )
    print(f"\nHealth model: {health.model_dump_json(indent=2)}")
