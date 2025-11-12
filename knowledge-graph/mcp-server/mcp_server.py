#!/usr/bin/env python3
"""
BSW-Arch MCP Server
Provides domain-specific tools for bot factory via Model Context Protocol
"""

import os
from fastmcp import FastMCP
from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Initialize MCP server
mcp = FastMCP("BSW-Arch Bot Factory")

# Get configuration from environment
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "bsw-secure-password-2024")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./knowledge-graph/data/chroma_db")

# Initialize connections
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("bsw_bot_specs")
embedder = SentenceTransformer('all-MiniLM-L6-v2')


@mcp.tool()
async def query_bot_knowledge(
    query: str,
    domain: str = "ALL",
    search_type: str = "hybrid",
    max_results: int = 5
) -> str:
    """
    Query the bot factory knowledge graph with hybrid search.

    Args:
        query: Natural language query about bots, architecture, or processes
        domain: Filter by domain (AXIS, PIPE, ECO, IV, or ALL)
        search_type: "hybrid" (graph+semantic), "graph" only, or "semantic" only
        max_results: Maximum number of results to return

    Returns:
        Formatted results with context from knowledge graph

    Example:
        query_bot_knowledge("How do AXIS bots handle architecture validation?", "AXIS")
    """

    results = []

    # Semantic search via ChromaDB
    if search_type in ["hybrid", "semantic"]:
        query_embedding = embedder.encode(query)

        where_filter = {}
        if domain != "ALL":
            where_filter = {"domain": domain}

        chroma_results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=max_results,
            where=where_filter if where_filter else None
        )

        for i, doc in enumerate(chroma_results['documents'][0]):
            metadata = chroma_results['metadatas'][0][i]
            results.append({
                'source': 'semantic_search',
                'content': doc,
                'metadata': metadata,
                'score': chroma_results['distances'][0][i] if chroma_results.get('distances') else 0
            })

    # Graph search via Neo4j
    if search_type in ["hybrid", "graph"]:
        with neo4j_driver.session() as session:
            # Search bots
            cypher_query = """
            MATCH (b:Bot)
            WHERE ($domain = 'ALL' OR b.domain = $domain)
            AND (toLower(b.name) CONTAINS toLower($query)
                 OR toLower(b.description) CONTAINS toLower($query)
                 OR toLower(b.capabilities) CONTAINS toLower($query))
            OPTIONAL MATCH (b)-[r:DEPENDS_ON]->(dep:Bot)
            OPTIONAL MATCH (b)-[:RUNS_IN]->(c:Container)
            RETURN b, collect(DISTINCT dep.name) as dependencies,
                   collect(DISTINCT c.name) as containers
            LIMIT $max_results
            """

            result = session.run(
                cypher_query,
                query=query,
                domain=domain,
                max_results=max_results
            )

            for record in result:
                bot = dict(record['b'])
                results.append({
                    'source': 'graph_search',
                    'type': 'bot',
                    'content': bot,
                    'dependencies': record['dependencies'],
                    'containers': record['containers']
                })

    # Format results
    if not results:
        return f"No results found for query: '{query}' in domain: {domain}"

    formatted = [f"# Query Results: {query}\n"]
    formatted.append(f"Domain: {domain}\n")
    formatted.append(f"Found {len(results)} results\n\n")

    for i, result in enumerate(results[:max_results], 1):
        formatted.append(f"## Result {i}\n")

        if result['source'] == 'semantic_search':
            formatted.append(f"**Source:** Semantic Search\n")
            formatted.append(f"**Type:** {result['metadata'].get('type', 'unknown')}\n")

            if result['metadata'].get('type') == 'bot_spec':
                formatted.append(f"**Bot:** {result['metadata'].get('name')}\n")

            formatted.append(f"\n{result['content'][:500]}...\n\n")

        elif result['source'] == 'graph_search':
            formatted.append(f"**Source:** Knowledge Graph\n")
            formatted.append(f"**Bot:** {result['content'].get('name')}\n")
            formatted.append(f"**Domain:** {result['content'].get('domain')}\n")
            formatted.append(f"**Description:** {result['content'].get('description')}\n")

            if result.get('dependencies'):
                formatted.append(f"**Dependencies:** {', '.join(result['dependencies'])}\n")

            if result.get('containers'):
                formatted.append(f"**Containers:** {', '.join(result['containers'])}\n")

            formatted.append("\n")

    return "\n".join(formatted)


@mcp.tool()
async def get_bot_dependencies(
    bot_name: str,
    domain: str = "ALL",
    depth: int = 2
) -> str:
    """
    Get dependency tree for a specific bot.

    Args:
        bot_name: Name of the bot to analyze
        domain: Optional domain filter
        depth: Traversal depth for dependencies

    Returns:
        Dependency tree showing what the bot depends on and what depends on it

    Example:
        get_bot_dependencies("axis-docs-bot", "AXIS", 2)
    """

    with neo4j_driver.session() as session:
        # Find bot with dependencies
        result = session.run("""
            MATCH (b:Bot {name: $bot_name})
            WHERE $domain = 'ALL' OR b.domain = $domain

            // Get dependencies (what this bot depends on)
            OPTIONAL MATCH (b)-[:DEPENDS_ON*1..""" + str(depth) + """]->(dep:Bot)
            WITH b, collect(DISTINCT {name: dep.name, domain: dep.domain}) as dependencies

            // Get dependents (what depends on this bot)
            OPTIONAL MATCH (dependent:Bot)-[:DEPENDS_ON*1..""" + str(depth) + """]->(b)
            WITH b, dependencies,
                 collect(DISTINCT {name: dependent.name, domain: dependent.domain}) as dependents

            RETURN b, dependencies, dependents
        """,
            bot_name=bot_name,
            domain=domain
        )

        record = result.single()

        if not record:
            return f"Bot '{bot_name}' not found in domain '{domain}'"

        bot = dict(record['b'])
        dependencies = record['dependencies']
        dependents = record['dependents']

        # Format output
        output = [f"# Dependency Analysis: {bot_name}\n"]
        output.append(f"**Domain:** {bot.get('domain')}\n")
        output.append(f"**Description:** {bot.get('description')}\n\n")

        output.append(f"## Dependencies ({len(dependencies)})\n")
        output.append(f"Bots that **{bot_name}** depends on:\n\n")

        if dependencies:
            for dep in dependencies:
                output.append(f"- **{dep['name']}** ({dep['domain']})\n")
        else:
            output.append("- No dependencies\n")

        output.append(f"\n## Dependents ({len(dependents)})\n")
        output.append(f"Bots that depend on **{bot_name}**:\n\n")

        if dependents:
            for dep in dependents:
                output.append(f"- **{dep['name']}** ({dep['domain']})\n")
        else:
            output.append("- No dependents\n")

        return "\n".join(output)


@mcp.tool()
async def analyze_bot_impact(
    bot_name: str,
    change_type: str = "modification"
) -> str:
    """
    Analyze the impact of changes to a bot.

    Args:
        bot_name: Name of the bot being changed
        change_type: Type of change (modification, removal, upgrade)

    Returns:
        Impact analysis showing affected bots and risk level

    Example:
        analyze_bot_impact("pipe-build-bot", "modification")
    """

    with neo4j_driver.session() as session:
        # Find bot and all its dependents
        result = session.run("""
            MATCH (b:Bot {name: $bot_name})

            // Get all bots that depend on this (directly or indirectly)
            OPTIONAL MATCH path = (dependent:Bot)-[:DEPENDS_ON*1..5]->(b)
            WITH b, collect(DISTINCT {
                name: dependent.name,
                domain: dependent.domain,
                distance: length(path)
            }) as dependents

            RETURN b, dependents
        """,
            bot_name=bot_name
        )

        record = result.single()

        if not record:
            return f"Bot '{bot_name}' not found"

        bot = dict(record['b'])
        dependents = record['dependents']

        # Categorize by risk
        high_risk = [d for d in dependents if d['distance'] <= 1]
        medium_risk = [d for d in dependents if 2 <= d['distance'] <= 3]
        low_risk = [d for d in dependents if d['distance'] > 3]

        # Format output
        output = [f"# Impact Analysis: {bot_name}\n"]
        output.append(f"**Change Type:** {change_type}\n")
        output.append(f"**Domain:** {bot.get('domain')}\n\n")

        output.append(f"**Total Affected Bots:** {len(dependents)}\n\n")

        if change_type == "removal":
            output.append("⚠️ **WARNING:** Removing this bot will break dependencies!\n\n")

        output.append(f"## 🔴 HIGH RISK (distance ≤ 1) - {len(high_risk)} bots\n")
        output.append("Direct dependents that will be immediately affected:\n\n")
        for dep in high_risk:
            output.append(f"- **{dep['name']}** ({dep['domain']})\n")

        output.append(f"\n## 🟡 MEDIUM RISK (distance 2-3) - {len(medium_risk)} bots\n")
        output.append("Indirect dependents that may be affected:\n\n")
        for dep in medium_risk:
            output.append(f"- **{dep['name']}** ({dep['domain']})\n")

        output.append(f"\n## 🟢 LOW RISK (distance > 3) - {len(low_risk)} bots\n")
        output.append("Distant dependents with minimal impact:\n\n")
        for dep in low_risk[:5]:  # Limit to 5
            output.append(f"- **{dep['name']}** ({dep['domain']})\n")

        if len(low_risk) > 5:
            output.append(f"- ... and {len(low_risk) - 5} more\n")

        output.append("\n## Recommendations\n")
        if high_risk:
            output.append("1. ⚠️ Update high-risk bots first\n")
            output.append("2. ⚠️ Add integration tests for direct dependents\n")
            output.append("3. ⚠️ Consider backward compatibility\n")
        else:
            output.append("✅ No high-risk dependencies found\n")

        return "\n".join(output)


@mcp.tool()
async def find_similar_bots(
    bot_description: str,
    domain: str = "ALL",
    max_results: int = 5
) -> str:
    """
    Find bots with similar functionality.

    Args:
        bot_description: Description of desired functionality
        domain: Optional domain filter
        max_results: Maximum number of similar bots to return

    Returns:
        List of similar bots with explanations

    Example:
        find_similar_bots("handles documentation generation", "AXIS")
    """

    # Generate embedding for description
    query_embedding = embedder.encode(bot_description)

    # Query ChromaDB
    where_filter = {}
    if domain != "ALL":
        where_filter = {"domain": domain, "type": "bot_spec"}
    else:
        where_filter = {"type": "bot_spec"}

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=max_results,
        where=where_filter
    )

    if not results['documents'][0]:
        return f"No similar bots found for: '{bot_description}'"

    # Format output
    output = [f"# Similar Bots: {bot_description}\n"]
    output.append(f"Domain: {domain}\n")
    output.append(f"Found {len(results['documents'][0])} similar bots\n\n")

    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        output.append(f"## {i}. {metadata.get('name')}\n")
        output.append(f"**Domain:** {metadata.get('domain')}\n")
        output.append(f"**Similarity:** {1 - results['distances'][0][i-1]:.2%}\n\n")
        output.append(f"{doc[:300]}...\n\n")

    return "\n".join(output)


@mcp.tool()
async def get_domain_overview(domain: str) -> str:
    """
    Get comprehensive overview of a bot domain.

    Args:
        domain: Domain to analyze (AXIS, PIPE, ECO, or IV)

    Returns:
        Overview including bot count, dependencies, and key bots

    Example:
        get_domain_overview("AXIS")
    """

    with neo4j_driver.session() as session:
        # Get domain statistics
        result = session.run("""
            MATCH (b:Bot {domain: $domain})

            // Count total bots
            WITH count(b) as total_bots, collect(b) as all_bots

            // Get bots with most dependencies
            UNWIND all_bots as bot
            OPTIONAL MATCH (bot)-[:DEPENDS_ON]->(dep)
            WITH total_bots, bot, count(dep) as dep_count
            ORDER BY dep_count DESC

            // Get bots with most dependents
            OPTIONAL MATCH (dependent)-[:DEPENDS_ON]->(bot)
            WITH total_bots,
                 collect({name: bot.name, dependencies: dep_count})[..5] as most_dependent,
                 bot, count(dependent) as dependent_count
            ORDER BY dependent_count DESC

            RETURN total_bots,
                   most_dependent,
                   collect({name: bot.name, dependents: dependent_count})[..5] as most_critical
        """,
            domain=domain
        )

        record = result.single()

        if not record:
            return f"Domain '{domain}' not found"

        output = [f"# {domain} Domain Overview\n"]
        output.append(f"**Total Bots:** {record['total_bots']}\n\n")

        output.append("## Most Complex Bots (by dependencies)\n")
        for bot in record['most_dependent']:
            output.append(f"- **{bot['name']}**: {bot['dependencies']} dependencies\n")

        output.append("\n## Most Critical Bots (by dependents)\n")
        for bot in record['most_critical']:
            output.append(f"- **{bot['name']}**: {bot['dependents']} dependents\n")

        return "\n".join(output)


@mcp.resource("project://stats")
async def get_project_stats() -> str:
    """
    Get overall statistics about the bot factory.

    Returns:
        Comprehensive statistics about bots, domains, and relationships
    """

    with neo4j_driver.session() as session:
        # Count by domain
        result = session.run("""
            MATCH (b:Bot)
            RETURN b.domain as domain, count(b) as count
            ORDER BY domain
        """)

        output = ["# BSW-Arch Bot Factory Statistics\n\n"]
        output.append("## Bots by Domain\n")

        total_bots = 0
        for record in result:
            count = record['count']
            total_bots += count
            output.append(f"- **{record['domain']}**: {count} bots\n")

        output.append(f"\n**Total Bots:** {total_bots}\n\n")

        # Count other entities
        for label in ['Document', 'Template', 'Container']:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()['count']
            output.append(f"**{label}s:** {count}\n")

        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()['count']
        output.append(f"**Relationships:** {rel_count}\n")

        # Vector embeddings
        output.append(f"**Vector Embeddings:** {collection.count()}\n")

    return "\n".join(output)


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
