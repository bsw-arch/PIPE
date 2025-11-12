#!/usr/bin/env python3
"""
BSW-Arch MCP Server - CAG+RAG Integration
FastAPI-based MCP server for unified CAG+RAG queries
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "cag"))
sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))

from context_manager import ContextManager, UserContext
from query_classifier import QueryClassifier, QueryType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Request model for CAG+RAG queries"""
    query: str = Field(..., description="User query string")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    domains: Optional[List[str]] = Field(None, description="Target domains (optional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class QueryResponse(BaseModel):
    """Response model for CAG+RAG queries"""
    response: str = Field(..., description="Generated response")
    metadata: Dict[str, Any] = Field(..., description="Processing metadata")
    sources: List[Dict[str, Any]] = Field(..., description="Source attribution")
    confidence: float = Field(..., description="Confidence score (0-1)")


class MCPServer:
    """
    MCP Server for CAG+RAG system

    Integrates:
    - CAG Layer (Context, Classification, Routing)
    - RAG Layer (Retrieval, Fusion)
    - BSW-Arch Bot Factory domains
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize MCP Server

        Args:
            config: Server configuration dictionary
        """
        self.app = FastAPI(
            title="BSW-Arch CAG+RAG MCP Server",
            description="Context-Aware Generation + Retrieval-Augmented Generation",
            version="1.0.0"
        )

        self.config = config or self._default_config()

        # Initialize components
        logger.info("Initializing MCP Server components...")
        self.context_manager = ContextManager()
        self.query_classifier = QueryClassifier()

        # Setup routes and middleware
        self._setup_middleware()
        self._setup_routes()

        logger.info("MCP Server initialized successfully")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'domains': {
                'AXIS': {
                    'endpoint': 'http://axis-orchestrator:8000',
                    'description': 'Architecture domain - 45 bots'
                },
                'PIPE': {
                    'endpoint': 'http://pipe-orchestrator:8000',
                    'description': 'Pipeline domain - 48 bots'
                },
                'ECO': {
                    'endpoint': 'http://eco-orchestrator:8000',
                    'description': 'Ecological domain - 48 bots'
                },
                'IV': {
                    'endpoint': 'http://iv-orchestrator:8000',
                    'description': 'Intelligence/Validation domain - 44 bots'
                }
            }
        }

    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.post("/api/v1/query", response_model=QueryResponse)
        async def process_query(request: QueryRequest):
            """
            Process CAG+RAG query

            Args:
                request: QueryRequest with query, user_id, session_id

            Returns:
                QueryResponse with response, metadata, sources, confidence
            """
            try:
                logger.info(f"Processing query from user {request.user_id}")

                # Build context (CAG Layer)
                context = await self.context_manager.build_context(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    query=request.query
                )

                # Classify query
                query_type, target_domains = await self.query_classifier.classify_query(
                    query=request.query,
                    context=context
                )

                # Override with requested domains if provided
                if request.domains:
                    target_domains = request.domains
                    logger.info(f"Using requested domains: {target_domains}")

                # Generate response (simplified for now)
                response_text = await self._generate_response(
                    query=request.query,
                    query_type=query_type,
                    domains=target_domains,
                    context=context
                )

                # Update interaction history
                await self.context_manager.update_interaction_history(
                    user_id=request.user_id,
                    interaction={
                        'query': request.query,
                        'query_type': query_type.value,
                        'domains': target_domains,
                        'response_preview': response_text[:100]
                    }
                )

                return QueryResponse(
                    response=response_text,
                    metadata={
                        'query_type': query_type.value,
                        'domains': target_domains,
                        'processing_time': 0.5  # Placeholder
                    },
                    sources=[
                        {
                            'domain': domain,
                            'type': 'bot_factory',
                            'confidence': 0.85
                        }
                        for domain in target_domains
                    ],
                    confidence=0.85
                )

            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "version": "1.0.0",
                "components": {
                    "cag": "operational",
                    "rag": "operational"
                }
            }

        @self.app.get("/api/v1/domains")
        async def get_domains():
            """Get available bot domains"""
            return {
                "domains": [
                    {
                        "name": name,
                        "description": config['description']
                    }
                    for name, config in self.config['domains'].items()
                ]
            }

        @self.app.get("/api/v1/query-types")
        async def get_query_types():
            """Get supported query types"""
            return {
                "query_types": [qt.value for qt in QueryType]
            }

        @self.app.post("/api/v1/classify")
        async def classify_query_endpoint(request: QueryRequest):
            """Classify a query without generating response"""
            try:
                context = await self.context_manager.build_context(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    query=request.query
                )

                query_type, target_domains = await self.query_classifier.classify_query(
                    query=request.query,
                    context=context
                )

                return {
                    "query": request.query,
                    "query_type": query_type.value,
                    "target_domains": target_domains,
                    "context_preferences": context.domain_preferences
                }

            except Exception as e:
                logger.error(f"Error classifying query: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def _generate_response(self,
                                query: str,
                                query_type: QueryType,
                                domains: List[str],
                                context: UserContext) -> str:
        """
        Generate response using CAG+RAG pipeline

        This is a simplified version. Full implementation would:
        1. Route to domain bots
        2. Perform hybrid retrieval (vector, graph, document)
        3. Fuse knowledge from multiple sources
        4. Generate contextually aware response using LLM

        Args:
            query: User query
            query_type: Classified query type
            domains: Target domains
            context: User context

        Returns:
            Generated response string
        """
        # Simplified response generation
        domain_info = []
        for domain in domains:
            if domain in self.config['domains']:
                domain_info.append(
                    f"- {domain}: {self.config['domains'][domain]['description']}"
                )

        response = f"""Based on your {query_type.value} query across the following domains:

{chr(10).join(domain_info)}

Query: "{query}"

This query has been classified and routed appropriately. In a full implementation, this would:
1. Retrieve relevant information from each domain's knowledge base
2. Perform hybrid search (vector, graph, document)
3. Fuse knowledge from multiple sources
4. Generate a comprehensive, contextually-aware response

Your domain preferences based on history: {', '.join(context.domain_preferences) if context.domain_preferences else 'None yet'}

For the BSW-Arch bot factory, this spans {len(domains)} domain(s) with specialized bots ready to assist."""

        return response

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the MCP server

        Args:
            host: Host address
            port: Port number
        """
        import uvicorn
        logger.info(f"Starting MCP Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="BSW-Arch CAG+RAG MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")

    args = parser.parse_args()

    server = MCPServer()
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
