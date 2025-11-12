#!/usr/bin/env python3
"""
Shared Utilities Package
Provides common models, configuration, and utilities for CAG+RAG services
"""

from .models import (
    QueryRequest,
    QueryResponse,
    CAGResponse,
    RAGResponse,
    UserContext,
    SessionContext,
    KnowledgeSource,
    QueryType,
    Domain,
    RetrievalMethod,
    HealthStatus,
    ErrorResponse,
)

from .config import (
    CAGServiceConfig,
    RAGServiceConfig,
    MCPServiceConfig,
    ConfigLoader,
    get_environment,
    is_production,
    is_development,
)

__version__ = "1.0.0"
__author__ = "BSW-Tech Architecture Team"

__all__ = [
    # Models
    "QueryRequest",
    "QueryResponse",
    "CAGResponse",
    "RAGResponse",
    "UserContext",
    "SessionContext",
    "KnowledgeSource",
    "QueryType",
    "Domain",
    "RetrievalMethod",
    "HealthStatus",
    "ErrorResponse",
    # Config
    "CAGServiceConfig",
    "RAGServiceConfig",
    "MCPServiceConfig",
    "ConfigLoader",
    "get_environment",
    "is_production",
    "is_development",
]
