#!/usr/bin/env python3
"""
Enhanced MCP Server with Spec-Aware Tools
Integrates OpenSpec, Neo4j Knowledge Graph, and ChromaDB for AI-assisted development
Part of the BSW-Arch AI Development Platform
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from neo4j import AsyncGraphDatabase
from sentence_transformers import SentenceTransformer

try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp")
    exit(1)


class EnhancedMCPServer:
    """Enhanced MCP Server with spec-aware knowledge graph tools"""

    def __init__(self):
        self.server = Server("bsw-arch-enhanced-mcp")
        self.neo4j_driver = None
        self.chroma_client = None
        self.embedder = None
        self.spec_collection = None
        self.code_collection = None

        # Configuration
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        self.chroma_path = os.getenv("CHROMA_PATH", "/opt/chroma-data")

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all MCP handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available spec-aware tools"""
            return [
                types.Tool(
                    name="query_spec_aware_graph",
                    description="Query the knowledge graph with spec awareness. Returns code, specs, and their relationships.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about code or specifications"
                            },
                            "include_specs": {
                                "type": "boolean",
                                "description": "Include specification context in results",
                                "default": True
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum graph traversal depth",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="validate_spec_implementation",
                    description="Validate that code properly implements its specification. Returns coverage percentage and missing items.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spec_id": {
                                "type": "string",
                                "description": "Specification ID to validate"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Optional file path to check specific implementation"
                            }
                        },
                        "required": ["spec_id"]
                    }
                ),
                types.Tool(
                    name="analyze_change_impact_with_specs",
                    description="Analyze impact of proposed code changes considering specifications. Returns affected specs, tests, and dependencies.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "File path being changed"
                            },
                            "function_name": {
                                "type": "string",
                                "description": "Optional function name being changed"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="suggest_spec_for_code",
                    description="Generate specification suggestions for existing code. Returns OpenSpec-formatted proposal.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "File path to analyze"
                            },
                            "function_name": {
                                "type": "string",
                                "description": "Optional specific function to spec"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="find_unspecified_code",
                    description="Find code that lacks specification coverage. Returns list of functions/classes without specs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to scan (defaults to project root)"
                            },
                            "min_complexity": {
                                "type": "integer",
                                "description": "Minimum cyclomatic complexity to report",
                                "default": 5
                            }
                        }
                    }
                ),
                types.Tool(
                    name="generate_traceability_matrix",
                    description="Generate complete traceability matrix from requirements to code to tests.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spec_id": {
                                "type": "string",
                                "description": "Optional specific spec ID, or all specs if omitted"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format: 'markdown', 'json', or 'html'",
                                "default": "markdown"
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict
        ) -> List[types.TextContent]:
            """Handle tool execution"""

            # Ensure initialization
            if not self.neo4j_driver:
                await self._initialize()

            try:
                if name == "query_spec_aware_graph":
                    result = await self._query_spec_aware_graph(**arguments)
                elif name == "validate_spec_implementation":
                    result = await self._validate_spec_implementation(**arguments)
                elif name == "analyze_change_impact_with_specs":
                    result = await self._analyze_change_impact(**arguments)
                elif name == "suggest_spec_for_code":
                    result = await self._suggest_spec_for_code(**arguments)
                elif name == "find_unspecified_code":
                    result = await self._find_unspecified_code(**arguments)
                elif name == "generate_traceability_matrix":
                    result = await self._generate_traceability_matrix(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _initialize(self):
        """Initialize connections to Neo4j and ChromaDB"""
        print("🔧 Initializing Enhanced MCP Server...")

        # Initialize Neo4j
        self.neo4j_driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collections
        self.spec_collection = self.chroma_client.get_or_create_collection(
            name="specifications",
            metadata={"hnsw:space": "cosine"}
        )

        self.code_collection = self.chroma_client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize embedder
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        print("✅ Enhanced MCP Server initialized")

    async def _query_spec_aware_graph(
        self,
        query: str,
        include_specs: bool = True,
        max_results: int = 5,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """Query knowledge graph with spec awareness"""

        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()

        results = {
            "query": query,
            "specifications": [],
            "code": [],
            "relationships": []
        }

        # Search specifications if requested
        if include_specs:
            spec_results = self.spec_collection.query(
                query_embeddings=[query_embedding],
                n_results=min(max_results, 3)
            )

            if spec_results['ids'] and spec_results['ids'][0]:
                for i, spec_id in enumerate(spec_results['ids'][0]):
                    metadata = spec_results['metadatas'][0][i]

                    # Get implementation status from graph
                    async with self.neo4j_driver.session() as session:
                        impl_result = await session.run("""
                            MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                            OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)
                            RETURN r.description as requirement,
                                   count(f) as impl_count,
                                   collect(f.name) as functions
                        """, spec_id=spec_id)

                        requirements = []
                        async for record in impl_result:
                            requirements.append({
                                "requirement": record["requirement"],
                                "implemented_by": record["functions"],
                                "implementation_count": record["impl_count"]
                            })

                    results["specifications"].append({
                        "id": spec_id,
                        "title": metadata.get("title", "Unknown"),
                        "status": metadata.get("status", "unknown"),
                        "requirements": requirements,
                        "relevance": spec_results['distances'][0][i]
                    })

        # Search code
        code_results = self.code_collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results
        )

        if code_results['ids'] and code_results['ids'][0]:
            for i, code_id in enumerate(code_results['ids'][0]):
                metadata = code_results['metadatas'][0][i]
                document = code_results['documents'][0][i]

                # Get relationships from graph
                async with self.neo4j_driver.session() as session:
                    rel_result = await session.run("""
                        MATCH (f:Function {id: $code_id})
                        OPTIONAL MATCH (f)-[:IMPLEMENTS]->(r:Requirement)<-[:CONTAINS]-(s:Specification)
                        OPTIONAL MATCH (f)-[:CALLS]->(called:Function)
                        OPTIONAL MATCH (caller:Function)-[:CALLS]->(f)
                        RETURN s.id as spec_id,
                               r.description as requirement,
                               collect(DISTINCT called.name) as calls,
                               collect(DISTINCT caller.name) as called_by
                        LIMIT 1
                    """, code_id=code_id)

                    relationships = await rel_result.single()

                results["code"].append({
                    "id": code_id,
                    "file": metadata.get("file_path", "unknown"),
                    "function": metadata.get("function_name", "unknown"),
                    "content": document[:500],  # Truncate for readability
                    "spec_id": relationships["spec_id"] if relationships else None,
                    "requirement": relationships["requirement"] if relationships else None,
                    "calls": relationships["calls"] if relationships else [],
                    "called_by": relationships["called_by"] if relationships else [],
                    "relevance": code_results['distances'][0][i]
                })

        return results

    async def _validate_spec_implementation(
        self,
        spec_id: str,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate spec implementation coverage"""

        async with self.neo4j_driver.session() as session:
            if file_path:
                result = await session.run("""
                    MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                    OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)-[:IN_FILE]->(file:File {path: $file_path})
                    RETURN count(DISTINCT r) as total_requirements,
                           count(DISTINCT f) as implemented_requirements,
                           collect(DISTINCT r.description) as all_requirements,
                           collect(DISTINCT CASE WHEN f IS NOT NULL THEN r.description END) as implemented
                """, spec_id=spec_id, file_path=file_path)
            else:
                result = await session.run("""
                    MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                    OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)
                    RETURN count(DISTINCT r) as total_requirements,
                           count(DISTINCT f) as implemented_requirements,
                           collect(DISTINCT r.description) as all_requirements,
                           collect(DISTINCT CASE WHEN f IS NOT NULL THEN r.description END) as implemented
                """, spec_id=spec_id)

            record = await result.single()

            total = record["total_requirements"]
            implemented = record["implemented_requirements"]
            coverage = (implemented / total * 100) if total > 0 else 0

            all_reqs = set(r for r in record["all_requirements"] if r)
            impl_reqs = set(r for r in record["implemented"] if r)
            missing = all_reqs - impl_reqs

            return {
                "spec_id": spec_id,
                "file_path": file_path,
                "total_requirements": total,
                "implemented_requirements": implemented,
                "coverage_percentage": round(coverage, 2),
                "status": "complete" if coverage == 100 else "partial" if coverage > 0 else "not_started",
                "missing_requirements": list(missing)
            }

    async def _analyze_change_impact(
        self,
        file_path: str,
        function_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze impact of code changes"""

        async with self.neo4j_driver.session() as session:
            if function_name:
                query = """
                    MATCH (f:Function {name: $function_name})-[:IN_FILE]->(file:File {path: $file_path})
                    OPTIONAL MATCH (f)-[:IMPLEMENTS]->(r:Requirement)<-[:CONTAINS]-(s:Specification)
                    OPTIONAL MATCH (f)-[:CALLS]->(called:Function)
                    OPTIONAL MATCH (caller:Function)-[:CALLS]->(f)
                    OPTIONAL MATCH (f)-[:TESTED_BY]->(t:Test)
                    RETURN s.id as spec_id,
                           collect(DISTINCT r.description) as requirements,
                           collect(DISTINCT called.name) as calls_functions,
                           collect(DISTINCT caller.name) as called_by_functions,
                           collect(DISTINCT t.name) as tests
                """
                params = {"file_path": file_path, "function_name": function_name}
            else:
                query = """
                    MATCH (file:File {path: $file_path})<-[:IN_FILE]-(f:Function)
                    OPTIONAL MATCH (f)-[:IMPLEMENTS]->(r:Requirement)<-[:CONTAINS]-(s:Specification)
                    OPTIONAL MATCH (f)-[:CALLS]->(called:Function)
                    OPTIONAL MATCH (caller:Function)-[:CALLS]->(f)
                    OPTIONAL MATCH (f)-[:TESTED_BY]->(t:Test)
                    RETURN collect(DISTINCT s.id) as spec_ids,
                           collect(DISTINCT r.description) as requirements,
                           collect(DISTINCT called.name) as calls_functions,
                           collect(DISTINCT caller.name) as called_by_functions,
                           collect(DISTINCT t.name) as tests
                """
                params = {"file_path": file_path}

            result = await session.run(query, **params)
            record = await result.single()

            if not record:
                return {
                    "file_path": file_path,
                    "function_name": function_name,
                    "impact": "none",
                    "message": "No graph data found for this code"
                }

            return {
                "file_path": file_path,
                "function_name": function_name,
                "affected_specifications": record.get("spec_ids", []) or [record.get("spec_id")],
                "affected_requirements": [r for r in record["requirements"] if r],
                "calls_functions": [f for f in record["calls_functions"] if f],
                "called_by_functions": [f for f in record["called_by_functions"] if f],
                "affected_tests": [t for t in record["tests"] if t],
                "impact_level": self._calculate_impact_level(record)
            }

    def _calculate_impact_level(self, record: Dict) -> str:
        """Calculate impact level from graph data"""
        impact_score = 0

        if record.get("spec_ids") or record.get("spec_id"):
            impact_score += 3
        if record.get("requirements"):
            impact_score += len([r for r in record["requirements"] if r])
        if record.get("called_by_functions"):
            impact_score += len([f for f in record["called_by_functions"] if f]) * 2

        if impact_score == 0:
            return "none"
        elif impact_score <= 3:
            return "low"
        elif impact_score <= 7:
            return "medium"
        else:
            return "high"

    async def _suggest_spec_for_code(
        self,
        file_path: str,
        function_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate spec suggestions for code"""

        # Read the code
        try:
            code_content = Path(file_path).read_text()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}

        # Extract function if specified
        if function_name:
            # Simple extraction - in production, use AST parsing
            lines = code_content.split('\n')
            func_lines = []
            in_function = False
            indent_level = 0

            for line in lines:
                if f"def {function_name}" in line:
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    func_lines.append(line)
                elif in_function:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= indent_level:
                        break
                    func_lines.append(line)

            code_to_spec = '\n'.join(func_lines)
        else:
            code_to_spec = code_content[:2000]  # Limit size

        # Generate spec proposal
        spec_proposal = {
            "file_path": file_path,
            "function_name": function_name,
            "suggested_spec": {
                "title": f"Specification for {function_name or Path(file_path).stem}",
                "summary": f"Auto-generated specification proposal",
                "requirements": self._extract_requirements_from_code(code_to_spec),
                "openspec_template": self._generate_openspec_template(file_path, function_name, code_to_spec)
            }
        }

        return spec_proposal

    def _extract_requirements_from_code(self, code: str) -> List[str]:
        """Extract potential requirements from code analysis"""
        requirements = []

        # Extract from docstrings
        if '"""' in code:
            docstring = code.split('"""')[1] if code.count('"""') >= 2 else ""
            if docstring:
                requirements.append(f"FUNC-001: {docstring.strip()[:100]}")

        # Extract from function signature
        if "def " in code:
            func_line = [l for l in code.split('\n') if 'def ' in l][0]
            requirements.append(f"FUNC-002: Function signature: {func_line.strip()}")

        # Extract from comments
        comments = [l.strip()[1:].strip() for l in code.split('\n') if l.strip().startswith('#')]
        for i, comment in enumerate(comments[:3]):
            requirements.append(f"FUNC-{i+3:03d}: {comment}")

        return requirements if requirements else ["FUNC-001: No documentation found - manual specification required"]

    def _generate_openspec_template(self, file_path: str, function_name: Optional[str], code: str) -> str:
        """Generate OpenSpec YAML template"""
        name = function_name or Path(file_path).stem
        return f"""---
version: 1.0.0
spec:
  id: SPEC-{name.upper()}-001
  title: Specification for {name}
  status: proposal
  created: {asyncio.get_event_loop().time()}

description: |
  Auto-generated specification for {file_path}
  {f'Function: {function_name}' if function_name else 'Full file specification'}

  REVIEW REQUIRED: This is an auto-generated proposal. Please review and enhance.

requirements:
  - id: REQ-001
    description: "TODO: Describe primary requirement"
    priority: high

  - id: REQ-002
    description: "TODO: Describe secondary requirements"
    priority: medium

implementation:
  file: {file_path}
  {f'function: {function_name}' if function_name else ''}

tests:
  - id: TEST-001
    description: "TODO: Add test requirements"
"""

    async def _find_unspecified_code(
        self,
        directory: Optional[str] = None,
        min_complexity: int = 5
    ) -> Dict[str, Any]:
        """Find code without spec coverage"""

        directory = directory or "."

        async with self.neo4j_driver.session() as session:
            result = await session.run("""
                MATCH (f:Function)-[:IN_FILE]->(file:File)
                WHERE file.path STARTS WITH $directory
                  AND NOT (f)-[:IMPLEMENTS]->(:Requirement)
                  AND f.complexity >= $min_complexity
                RETURN file.path as file_path,
                       f.name as function_name,
                       f.complexity as complexity,
                       f.lines as lines
                ORDER BY f.complexity DESC
                LIMIT 50
            """, directory=directory, min_complexity=min_complexity)

            unspecified = []
            async for record in result:
                unspecified.append({
                    "file": record["file_path"],
                    "function": record["function_name"],
                    "complexity": record["complexity"],
                    "lines": record["lines"]
                })

            return {
                "directory": directory,
                "min_complexity": min_complexity,
                "unspecified_count": len(unspecified),
                "unspecified_functions": unspecified,
                "recommendation": "Consider creating specifications for high-complexity functions first"
            }

    async def _generate_traceability_matrix(
        self,
        spec_id: Optional[str] = None,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """Generate traceability matrix"""

        async with self.neo4j_driver.session() as session:
            if spec_id:
                query = """
                    MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                    OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)
                    OPTIONAL MATCH (f)-[:TESTED_BY]->(t:Test)
                    RETURN s.id as spec_id,
                           s.title as spec_title,
                           r.id as req_id,
                           r.description as req_desc,
                           collect(DISTINCT f.name) as functions,
                           collect(DISTINCT t.name) as tests
                    ORDER BY r.id
                """
                params = {"spec_id": spec_id}
            else:
                query = """
                    MATCH (s:Specification)-[:CONTAINS]->(r:Requirement)
                    OPTIONAL MATCH (r)<-[:IMPLEMENTS]-(f:Function)
                    OPTIONAL MATCH (f)-[:TESTED_BY]->(t:Test)
                    RETURN s.id as spec_id,
                           s.title as spec_title,
                           r.id as req_id,
                           r.description as req_desc,
                           collect(DISTINCT f.name) as functions,
                           collect(DISTINCT t.name) as tests
                    ORDER BY s.id, r.id
                    LIMIT 100
                """
                params = {}

            result = await session.run(query, **params)

            matrix = []
            async for record in result:
                matrix.append({
                    "specification": record["spec_id"],
                    "spec_title": record["spec_title"],
                    "requirement": record["req_id"],
                    "requirement_description": record["req_desc"],
                    "implementations": [f for f in record["functions"] if f],
                    "tests": [t for t in record["tests"] if t],
                    "status": self._get_traceability_status(record)
                })

            if format == "markdown":
                return {"matrix": matrix, "formatted": self._format_matrix_markdown(matrix)}
            elif format == "html":
                return {"matrix": matrix, "formatted": self._format_matrix_html(matrix)}
            else:
                return {"matrix": matrix}

    def _get_traceability_status(self, record: Dict) -> str:
        """Determine traceability status"""
        has_impl = any(record.get("functions", []))
        has_tests = any(record.get("tests", []))

        if has_impl and has_tests:
            return "complete"
        elif has_impl:
            return "implemented_not_tested"
        else:
            return "not_implemented"

    def _format_matrix_markdown(self, matrix: List[Dict]) -> str:
        """Format traceability matrix as Markdown"""
        md = "# Traceability Matrix\n\n"
        md += "| Specification | Requirement | Implementation | Tests | Status |\n"
        md += "|--------------|-------------|----------------|-------|--------|\n"

        for item in matrix:
            md += f"| {item['specification']} | "
            md += f"{item['requirement']} | "
            md += f"{', '.join(item['implementations']) or 'None'} | "
            md += f"{', '.join(item['tests']) or 'None'} | "
            md += f"{item['status']} |\n"

        return md

    def _format_matrix_html(self, matrix: List[Dict]) -> str:
        """Format traceability matrix as HTML"""
        html = "<table border='1'>\n"
        html += "<tr><th>Specification</th><th>Requirement</th><th>Implementation</th><th>Tests</th><th>Status</th></tr>\n"

        for item in matrix:
            html += f"<tr>"
            html += f"<td>{item['specification']}</td>"
            html += f"<td>{item['requirement']}</td>"
            html += f"<td>{', '.join(item['implementations']) or 'None'}</td>"
            html += f"<td>{', '.join(item['tests']) or 'None'}</td>"
            html += f"<td>{item['status']}</td>"
            html += f"</tr>\n"

        html += "</table>"
        return html

    async def run(self):
        """Run the MCP server"""
        await self._initialize()

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bsw-arch-enhanced-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )

    async def cleanup(self):
        """Cleanup connections"""
        if self.neo4j_driver:
            await self.neo4j_driver.close()


async def main():
    """Main entry point"""
    server = EnhancedMCPServer()
    try:
        await server.run()
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
