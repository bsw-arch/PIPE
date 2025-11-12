#!/usr/bin/env python3
"""
Knowledge Graph Indexer with OpenSpec Support
Indexes code and specifications into Neo4j graph database
Supports incremental updates and relationship mapping
Part of the BSW-Arch AI Development Platform
"""

import ast
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ERROR: ChromaDB not installed. Install with: pip install chromadb")
    sys.exit(1)


class GraphIndexer:
    """Index code and specs into knowledge graph"""

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        chroma_path: str = "/opt/chroma-data"
    ):
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Get or create collections
        self.spec_collection = self.chroma_client.get_or_create_collection(
            name="specifications",
            metadata={"hnsw:space": "cosine"}
        )
        self.code_collection = self.chroma_client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize Neo4j schema with constraints and indexes"""
        with self.neo4j_driver.session() as session:
            # Create constraints for unique IDs
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Specification) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Function) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (file:File) REQUIRE file.path IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Test) REQUIRE t.id IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    # Constraint might already exist
                    pass

            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS FOR (s:Specification) ON (s.status)",
                "CREATE INDEX IF NOT EXISTS FOR (f:Function) ON (f.name)",
                "CREATE INDEX IF NOT EXISTS FOR (f:Function) ON (f.complexity)",
                "CREATE INDEX IF NOT EXISTS FOR (c:Class) ON (c.name)",
            ]

            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    pass

        print("✅ Neo4j schema initialized")

    def index_specification(self, spec_path: Path) -> bool:
        """Index an OpenSpec specification"""
        try:
            with open(spec_path, 'r') as f:
                spec_data = yaml.safe_load(f)

            if not spec_data or 'spec' not in spec_data:
                print(f"⚠️  Invalid spec format: {spec_path}")
                return False

            spec = spec_data['spec']
            spec_id = spec.get('id')
            if not spec_id:
                print(f"⚠️  Spec missing ID: {spec_path}")
                return False

            # Extract data
            title = spec.get('title', 'Untitled')
            status = spec.get('status', 'proposal')
            description = spec_data.get('description', '')
            requirements = spec_data.get('requirements', [])

            # Generate embedding for spec
            spec_text = f"{title}\n{description}"
            embedding = self.embedder.encode(spec_text).tolist()

            # Store in ChromaDB
            self.spec_collection.upsert(
                ids=[spec_id],
                documents=[spec_text],
                embeddings=[embedding],
                metadatas=[{
                    "title": title,
                    "status": status,
                    "file_path": str(spec_path),
                    "requirement_count": len(requirements)
                }]
            )

            # Store in Neo4j
            with self.neo4j_driver.session() as session:
                # Create/update specification node
                session.run("""
                    MERGE (s:Specification {id: $spec_id})
                    SET s.title = $title,
                        s.status = $status,
                        s.description = $description,
                        s.file_path = $file_path,
                        s.updated_at = timestamp()
                """, spec_id=spec_id, title=title, status=status,
                    description=description, file_path=str(spec_path))

                # Create requirement nodes and relationships
                for req in requirements:
                    req_id = req.get('id')
                    if not req_id:
                        continue

                    req_desc = req.get('description', '')
                    req_priority = req.get('priority', 'medium')

                    session.run("""
                        MERGE (r:Requirement {id: $req_id})
                        SET r.description = $description,
                            r.priority = $priority,
                            r.updated_at = timestamp()
                        WITH r
                        MATCH (s:Specification {id: $spec_id})
                        MERGE (s)-[:CONTAINS]->(r)
                    """, req_id=req_id, description=req_desc,
                        priority=req_priority, spec_id=spec_id)

            print(f"✅ Indexed specification: {spec_id}")
            return True

        except Exception as e:
            print(f"❌ Error indexing spec {spec_path}: {e}")
            return False

    def index_python_file(self, file_path: Path, project_root: Path) -> bool:
        """Index a Python source file"""
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()

            # Parse AST
            try:
                tree = ast.parse(source_code, filename=str(file_path))
            except SyntaxError as e:
                print(f"⚠️  Syntax error in {file_path}: {e}")
                return False

            rel_path = str(file_path.relative_to(project_root))

            # Create file node
            with self.neo4j_driver.session() as session:
                session.run("""
                    MERGE (file:File {path: $path})
                    SET file.size = $size,
                        file.lines = $lines,
                        file.updated_at = timestamp()
                """, path=rel_path, size=len(source_code),
                    lines=len(source_code.split('\n')))

            # Extract and index functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._index_function(node, rel_path, source_code)
                elif isinstance(node, ast.ClassDef):
                    self._index_class(node, rel_path, source_code)

            print(f"✅ Indexed file: {rel_path}")
            return True

        except Exception as e:
            print(f"❌ Error indexing {file_path}: {e}")
            return False

    def _index_function(self, node: ast.FunctionDef, file_path: str, source_code: str):
        """Index a function node"""
        func_name = node.name
        func_id = f"{file_path}::{func_name}"

        # Extract function source
        func_lines = source_code.split('\n')[node.lineno-1:node.end_lineno]
        func_source = '\n'.join(func_lines)

        # Calculate complexity (simple cyclomatic complexity)
        complexity = self._calculate_complexity(node)

        # Extract docstring
        docstring = ast.get_docstring(node) or ""

        # Generate embedding
        func_text = f"{func_name}\n{docstring}\n{func_source[:500]}"
        embedding = self.embedder.encode(func_text).tolist()

        # Store in ChromaDB
        self.code_collection.upsert(
            ids=[func_id],
            documents=[func_text],
            embeddings=[embedding],
            metadatas=[{
                "file_path": file_path,
                "function_name": func_name,
                "type": "function",
                "complexity": complexity,
                "lines": len(func_lines)
            }]
        )

        # Store in Neo4j
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (f:Function {id: $func_id})
                SET f.name = $name,
                    f.docstring = $docstring,
                    f.complexity = $complexity,
                    f.lines = $lines,
                    f.start_line = $start_line,
                    f.end_line = $end_line,
                    f.updated_at = timestamp()
                WITH f
                MATCH (file:File {path: $file_path})
                MERGE (f)-[:IN_FILE]->(file)
            """, func_id=func_id, name=func_name, docstring=docstring,
                complexity=complexity, lines=len(func_lines),
                start_line=node.lineno, end_line=node.end_lineno,
                file_path=file_path)

            # Index function calls
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        called_func = child.func.id
                        # Create CALLS relationship (will need to resolve later)
                        session.run("""
                            MATCH (f:Function {id: $func_id})
                            MERGE (called:Function {name: $called_name})
                            MERGE (f)-[:CALLS]->(called)
                        """, func_id=func_id, called_name=called_func)

    def _index_class(self, node: ast.ClassDef, file_path: str, source_code: str):
        """Index a class node"""
        class_name = node.name
        class_id = f"{file_path}::{class_name}"

        # Extract class source
        class_lines = source_code.split('\n')[node.lineno-1:node.end_lineno]
        class_source = '\n'.join(class_lines)

        # Extract docstring
        docstring = ast.get_docstring(node) or ""

        # Store in Neo4j
        with self.neo4j_driver.session() as session:
            session.run("""
                MERGE (c:Class {id: $class_id})
                SET c.name = $name,
                    c.docstring = $docstring,
                    c.lines = $lines,
                    c.start_line = $start_line,
                    c.end_line = $end_line,
                    c.updated_at = timestamp()
                WITH c
                MATCH (file:File {path: $file_path})
                MERGE (c)-[:IN_FILE]->(file)
            """, class_id=class_id, name=class_name, docstring=docstring,
                lines=len(class_lines), start_line=node.lineno,
                end_line=node.end_lineno, file_path=file_path)

            # Index methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    method_id = f"{class_id}::{method_name}"

                    session.run("""
                        MERGE (m:Function {id: $method_id})
                        SET m.name = $name,
                            m.is_method = true,
                            m.updated_at = timestamp()
                        WITH m
                        MATCH (c:Class {id: $class_id})
                        MERGE (c)-[:HAS_METHOD]->(m)
                    """, method_id=method_id, name=method_name, class_id=class_id)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def link_specs_to_code(self):
        """Link specifications to code implementations"""
        print("🔗 Linking specs to code...")

        with self.neo4j_driver.session() as session:
            # Find all specs with implementation info
            result = session.run("""
                MATCH (s:Specification)
                WHERE s.file_path IS NOT NULL
                RETURN s.id as spec_id, s.file_path as spec_path
            """)

            for record in result:
                spec_id = record["spec_id"]
                spec_path = Path(record["spec_path"])

                # Read spec to get implementation references
                try:
                    with open(spec_path, 'r') as f:
                        spec_data = yaml.safe_load(f)

                    impl = spec_data.get('implementation', {})
                    impl_file = impl.get('file')
                    impl_function = impl.get('function')

                    if impl_file:
                        # Link requirements to implementing functions
                        if impl_function:
                            session.run("""
                                MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                                MATCH (f:Function)-[:IN_FILE]->(file:File {path: $impl_file})
                                WHERE f.name = $impl_function
                                MERGE (f)-[:IMPLEMENTS]->(r)
                            """, spec_id=spec_id, impl_file=impl_file,
                                impl_function=impl_function)
                        else:
                            # Link to all functions in file
                            session.run("""
                                MATCH (s:Specification {id: $spec_id})-[:CONTAINS]->(r:Requirement)
                                MATCH (f:Function)-[:IN_FILE]->(file:File {path: $impl_file})
                                MERGE (f)-[:IMPLEMENTS]->(r)
                            """, spec_id=spec_id, impl_file=impl_file)

                        print(f"✅ Linked {spec_id} to {impl_file}")

                except Exception as e:
                    print(f"⚠️  Could not process spec {spec_id}: {e}")

    def index_directory(
        self,
        directory: Path,
        spec_dirs: Optional[List[Path]] = None,
        ignore_patterns: Optional[List[str]] = None
    ):
        """Index all code and specs in directory"""
        if ignore_patterns is None:
            ignore_patterns = ['__pycache__', '.git', '.venv', 'venv', 'node_modules']

        print(f"📚 Indexing directory: {directory}")

        # Index specifications first
        if spec_dirs:
            for spec_dir in spec_dirs:
                if spec_dir.exists():
                    print(f"\n📋 Indexing specifications from: {spec_dir}")
                    for spec_file in spec_dir.rglob("*.yaml"):
                        if not any(pattern in str(spec_file) for pattern in ignore_patterns):
                            self.index_specification(spec_file)
                    for spec_file in spec_dir.rglob("*.yml"):
                        if not any(pattern in str(spec_file) for pattern in ignore_patterns):
                            self.index_specification(spec_file)

        # Index Python code
        print(f"\n💻 Indexing Python code from: {directory}")
        python_files = list(directory.rglob("*.py"))
        total_files = len(python_files)

        for i, py_file in enumerate(python_files, 1):
            if any(pattern in str(py_file) for pattern in ignore_patterns):
                continue

            print(f"[{i}/{total_files}] ", end='')
            self.index_python_file(py_file, directory)

        # Link specs to code
        print("\n🔗 Linking specifications to implementations...")
        self.link_specs_to_code()

        print("\n✅ Indexing complete!")

    def incremental_update(self, file_path: Path, project_root: Path):
        """Incrementally update index for a single file"""
        if file_path.suffix == '.py':
            print(f"🔄 Updating index for: {file_path}")
            self.index_python_file(file_path, project_root)
            print("✅ Incremental update complete")
        elif file_path.suffix in ['.yaml', '.yml']:
            print(f"🔄 Updating spec index for: {file_path}")
            self.index_specification(file_path)
            self.link_specs_to_code()
            print("✅ Incremental spec update complete")

    def get_stats(self) -> Dict[str, int]:
        """Get indexing statistics"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Specification) WITH count(s) as specs
                MATCH (r:Requirement) WITH specs, count(r) as reqs
                MATCH (f:Function) WITH specs, reqs, count(f) as funcs
                MATCH (c:Class) WITH specs, reqs, funcs, count(c) as classes
                MATCH (file:File) WITH specs, reqs, funcs, classes, count(file) as files
                MATCH ()-[rel:IMPLEMENTS]->() WITH specs, reqs, funcs, classes, files, count(rel) as impls
                RETURN specs, reqs, funcs, classes, files, impls
            """)

            record = result.single()
            if record:
                return {
                    "specifications": record["specs"],
                    "requirements": record["reqs"],
                    "functions": record["funcs"],
                    "classes": record["classes"],
                    "files": record["files"],
                    "implementations": record["impls"]
                }
            return {}

    def close(self):
        """Close connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Index code and specs into knowledge graph")
    parser.add_argument("path", type=Path, help="Directory or file to index")
    parser.add_argument("--spec-dirs", nargs="+", type=Path, help="Directories containing OpenSpec files")
    parser.add_argument("--incremental", action="store_true", help="Incremental update for single file")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="password", help="Neo4j password")
    parser.add_argument("--chroma-path", default="/opt/chroma-data", help="ChromaDB storage path")
    parser.add_argument("--stats", action="store_true", help="Show indexing statistics")

    args = parser.parse_args()

    # Initialize indexer
    indexer = GraphIndexer(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        chroma_path=args.chroma_path
    )

    try:
        if args.stats:
            stats = indexer.get_stats()
            print("\n📊 Knowledge Graph Statistics:")
            print(f"  Specifications: {stats.get('specifications', 0)}")
            print(f"  Requirements: {stats.get('requirements', 0)}")
            print(f"  Functions: {stats.get('functions', 0)}")
            print(f"  Classes: {stats.get('classes', 0)}")
            print(f"  Files: {stats.get('files', 0)}")
            print(f"  Implementations: {stats.get('implementations', 0)}")
        elif args.incremental:
            indexer.incremental_update(args.path, args.project_root)
        else:
            indexer.index_directory(
                args.path,
                spec_dirs=args.spec_dirs
            )

            # Show stats
            stats = indexer.get_stats()
            print("\n📊 Indexing Statistics:")
            print(f"  Specifications: {stats.get('specifications', 0)}")
            print(f"  Requirements: {stats.get('requirements', 0)}")
            print(f"  Functions: {stats.get('functions', 0)}")
            print(f"  Classes: {stats.get('classes', 0)}")
            print(f"  Files: {stats.get('files', 0)}")
            print(f"  Implementations: {stats.get('implementations', 0)}")

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
