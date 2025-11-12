#!/usr/bin/env python3
"""
IV Bot Template with Knowledge Graph Integration
Connects to Neo4j knowledge graph and ChromaDB vector store
Supports RAG queries and continuous learning
Part of BSW-Arch AI Development Platform
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from neo4j import AsyncGraphDatabase
from sentence_transformers import SentenceTransformer

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    print("ERROR: chromadb not installed")
    sys.exit(1)


class IVBot:
    """Base IV Bot with Knowledge Graph integration"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize IV Bot"""
        self.config = self._load_config(config_path)
        self.bot_name = self.config.get("bot_name", "iv-bot")
        self.bot_type = self.config.get("bot_type", "generic")

        # Knowledge Graph connection
        self.neo4j_uri = os.getenv("NEO4J_URI", self.config.get("neo4j", {}).get("uri", "bolt://localhost:7687"))
        self.neo4j_user = os.getenv("NEO4J_USER", self.config.get("neo4j", {}).get("user", "neo4j"))
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", self.config.get("neo4j", {}).get("password", "password"))
        self.neo4j_driver = None

        # ChromaDB connection
        chroma_host = os.getenv("CHROMA_HOST", self.config.get("chromadb", {}).get("host", "localhost"))
        chroma_port = os.getenv("CHROMA_PORT", self.config.get("chromadb", {}).get("port", "8000"))

        try:
            self.chroma_client = chromadb.HttpClient(
                host=chroma_host,
                port=int(chroma_port),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.code_collection = self.chroma_client.get_or_create_collection("code_embeddings")
            self.spec_collection = self.chroma_client.get_or_create_collection("specifications")
        except Exception as e:
            print(f"⚠️  ChromaDB connection failed: {e}")
            print("   Falling back to in-memory mode")
            self.chroma_client = chromadb.PersistentClient(
                path="/app/data/chroma",
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.code_collection = self.chroma_client.get_or_create_collection("code_embeddings")
            self.spec_collection = self.chroma_client.get_or_create_collection("specifications")

        # Embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Ollama configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", self.config.get("ollama", {}).get("host", "http://localhost:11434"))
        self.ollama_model = self.config.get("ollama", {}).get("model", "deepseek-coder:6.7b")

        print(f"🤖 Initialized {self.bot_name} ({self.bot_type})")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load bot configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Config not found: {config_path}, using defaults")
            return {}

    async def initialize(self):
        """Initialize connections"""
        print("🔧 Initializing connections...")

        # Connect to Neo4j
        self.neo4j_driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

        # Verify connection
        try:
            async with self.neo4j_driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
            print("✅ Connected to Neo4j")
        except Exception as e:
            print(f"⚠️  Neo4j connection failed: {e}")

        print("✅ IV Bot initialized")

    async def query_knowledge_graph(
        self,
        query: str,
        use_vector_search: bool = True,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Query knowledge graph with optional vector search"""
        results = {
            "query": query,
            "vector_results": [],
            "graph_results": [],
            "combined_context": ""
        }

        # Vector search in ChromaDB
        if use_vector_search:
            query_embedding = self.embedder.encode(query).tolist()

            # Search code
            code_results = self.code_collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results
            )

            if code_results['ids'] and code_results['ids'][0]:
                for i, doc_id in enumerate(code_results['ids'][0]):
                    results["vector_results"].append({
                        "id": doc_id,
                        "content": code_results['documents'][0][i],
                        "metadata": code_results['metadatas'][0][i],
                        "distance": code_results['distances'][0][i] if 'distances' in code_results else None
                    })

        # Graph query
        if self.neo4j_driver:
            async with self.neo4j_driver.session() as session:
                # Simple keyword-based graph query
                graph_query = """
                    MATCH (n)
                    WHERE toLower(n.name) CONTAINS toLower($query)
                       OR toLower(n.description) CONTAINS toLower($query)
                    RETURN n
                    LIMIT $limit
                """

                graph_result = await session.run(
                    graph_query,
                    query=query,
                    limit=max_results
                )

                async for record in graph_result:
                    node = record["n"]
                    results["graph_results"].append({
                        "labels": list(node.labels),
                        "properties": dict(node)
                    })

        # Combine results into context
        context_parts = []

        for vr in results["vector_results"]:
            context_parts.append(f"Code: {vr['content'][:200]}")

        for gr in results["graph_results"]:
            context_parts.append(f"Graph: {gr['properties']}")

        results["combined_context"] = "\n\n".join(context_parts)

        return results

    async def rag_query(
        self,
        question: str,
        use_ollama: bool = True
    ) -> Dict[str, Any]:
        """Perform RAG query: Retrieve context + Generate response"""

        # Step 1: Retrieve relevant context
        context_data = await self.query_knowledge_graph(question)

        if not use_ollama:
            # Return context only
            return {
                "question": question,
                "context": context_data["combined_context"],
                "answer": "No LLM available for generation"
            }

        # Step 2: Generate response with Ollama
        try:
            import aiohttp

            prompt = f"""Based on the following context, answer the question.

Context:
{context_data['combined_context']}

Question: {question}

Answer:"""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "")

                        return {
                            "question": question,
                            "context": context_data["combined_context"],
                            "answer": answer,
                            "model": self.ollama_model
                        }
                    else:
                        return {
                            "question": question,
                            "context": context_data["combined_context"],
                            "answer": f"Error: Ollama returned status {response.status}",
                            "model": self.ollama_model
                        }

        except Exception as e:
            return {
                "question": question,
                "context": context_data["combined_context"],
                "answer": f"Error generating response: {e}",
                "model": self.ollama_model
            }

    async def learn_from_feedback(
        self,
        query: str,
        response: str,
        feedback: Dict[str, Any]
    ):
        """Learn from user feedback (continuous learning)"""
        # Store feedback in knowledge graph
        if self.neo4j_driver:
            async with self.neo4j_driver.session() as session:
                await session.run("""
                    CREATE (f:Feedback {
                        bot_name: $bot_name,
                        query: $query,
                        response: $response,
                        rating: $rating,
                        timestamp: timestamp()
                    })
                """, bot_name=self.bot_name, query=query, response=response,
                    rating=feedback.get("rating", 0))

        print(f"📝 Learned from feedback: {feedback.get('rating', 0)}/5")

    async def run(self):
        """Main bot loop"""
        await self.initialize()

        print(f"🚀 {self.bot_name} is running")
        print("   Type 'query <question>' to ask questions")
        print("   Type 'exit' to stop")
        print()

        try:
            while True:
                # In a real bot, this would be event-driven
                # For template, we use simple input loop
                try:
                    user_input = input(f"{self.bot_name}> ")

                    if user_input.lower() == "exit":
                        break

                    if user_input.startswith("query "):
                        question = user_input[6:].strip()
                        result = await self.rag_query(question)

                        print()
                        print("📊 Context:")
                        print(result["context"][:500])
                        print()
                        print("💡 Answer:")
                        print(result["answer"])
                        print()

                    elif user_input.startswith("graph "):
                        query = user_input[6:].strip()
                        result = await self.query_knowledge_graph(query)

                        print()
                        print("📊 Results:")
                        print(f"  Vector results: {len(result['vector_results'])}")
                        print(f"  Graph results: {len(result['graph_results'])}")
                        print()

                    else:
                        print("Unknown command. Use 'query <question>' or 'graph <search>'")

                except KeyboardInterrupt:
                    print("\n👋 Interrupted")
                    break

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup connections"""
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        print("👋 Cleanup complete")


async def main():
    """Main entry point"""
    bot = IVBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
