#!/usr/bin/env python3
"""
BSW-Arch Bot Specification Indexer
Indexes bot specifications, documentation, and templates into Neo4j knowledge graph
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import yaml
import hashlib
from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer


class BotSpecIndexer:
    """Index bot specifications and documentation into knowledge graph"""

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "bsw-secure-password-2024",
        chroma_path: str = "./knowledge-graph/data/chroma_db"
    ):
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # ChromaDB for vector search
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="bsw_bot_specs",
            metadata={"description": "BSW-Arch bot specifications and documentation"}
        )

        # Sentence transformer for embeddings
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        print("✓ Connected to Neo4j and ChromaDB")

    def index_repository(self, repo_path: str):
        """Index entire BSW-Arch repository"""
        repo_path = Path(repo_path).resolve()
        print(f"📂 Indexing repository: {repo_path}")

        # Index bot specifications
        print("\n1. Indexing bot specifications...")
        self.index_bot_specs(repo_path / "docs/specifications/bots")

        # Index container specs
        print("\n2. Indexing container specifications...")
        self.index_container_specs(repo_path / "docs/specifications/containers")

        # Index documentation
        print("\n3. Indexing documentation...")
        self.index_documentation(repo_path / "docs")

        # Index templates
        print("\n4. Indexing templates...")
        self.index_templates(repo_path / "docs/templates")

        # Index bot examples
        print("\n5. Indexing bot examples...")
        self.index_bot_examples(repo_path)

        # Create indexes for performance
        print("\n6. Creating database indexes...")
        self.create_indexes()

        print("\n✓ Indexing complete!")
        self.print_statistics()

    def index_bot_specs(self, specs_dir: Path):
        """Index bot specification YAML files"""
        if not specs_dir.exists():
            print(f"   ⚠ Directory not found: {specs_dir}")
            return

        for yaml_file in specs_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    spec = yaml.safe_load(f)

                if not spec:
                    continue

                # Extract domain from path (axis/pipe/eco/iv)
                domain = self._extract_domain(yaml_file)

                # Index in Neo4j
                with self.driver.session() as session:
                    session.run("""
                        MERGE (b:Bot {name: $name})
                        SET b.domain = $domain,
                            b.description = $description,
                            b.file_path = $file_path,
                            b.type = $type,
                            b.capabilities = $capabilities
                    """,
                        name=spec.get('name', yaml_file.stem),
                        domain=domain,
                        description=spec.get('description', ''),
                        file_path=str(yaml_file),
                        type=spec.get('type', 'bot'),
                        capabilities=str(spec.get('capabilities', []))
                    )

                # Create relationships
                if 'dependencies' in spec:
                    for dep in spec['dependencies']:
                        session.run("""
                            MATCH (b:Bot {name: $bot_name})
                            MERGE (d:Bot {name: $dep_name})
                            MERGE (b)-[:DEPENDS_ON]->(d)
                        """,
                            bot_name=spec.get('name', yaml_file.stem),
                            dep_name=dep
                        )

                # Index in ChromaDB for semantic search
                doc_text = f"{spec.get('name', '')}\n{spec.get('description', '')}\n{yaml.dump(spec)}"
                embedding = self.embedder.encode(doc_text)

                self.collection.add(
                    ids=[hashlib.md5(str(yaml_file).encode()).hexdigest()],
                    embeddings=[embedding.tolist()],
                    documents=[doc_text],
                    metadatas=[{
                        'type': 'bot_spec',
                        'domain': domain,
                        'name': spec.get('name', yaml_file.stem),
                        'file_path': str(yaml_file)
                    }]
                )

                print(f"   ✓ Indexed: {yaml_file.name} ({domain})")

            except Exception as e:
                print(f"   ✗ Error indexing {yaml_file}: {e}")

    def index_documentation(self, docs_dir: Path):
        """Index markdown documentation"""
        if not docs_dir.exists():
            print(f"   ⚠ Directory not found: {docs_dir}")
            return

        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract domain and type from path
                domain = self._extract_domain(md_file)
                doc_type = self._extract_doc_type(md_file)

                # Index in Neo4j
                with self.driver.session() as session:
                    session.run("""
                        MERGE (d:Document {path: $path})
                        SET d.domain = $domain,
                            d.type = $doc_type,
                            d.title = $title,
                            d.size = $size
                    """,
                        path=str(md_file),
                        domain=domain,
                        doc_type=doc_type,
                        title=md_file.stem,
                        size=len(content)
                    )

                # Create embeddings and index in ChromaDB
                # Split large documents into chunks
                chunks = self._chunk_text(content, max_size=1000)

                for i, chunk in enumerate(chunks):
                    embedding = self.embedder.encode(chunk)
                    chunk_id = hashlib.md5(f"{md_file}_{i}".encode()).hexdigest()

                    self.collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding.tolist()],
                        documents=[chunk],
                        metadatas=[{
                            'type': 'documentation',
                            'domain': domain,
                            'doc_type': doc_type,
                            'file_path': str(md_file),
                            'chunk_index': i
                        }]
                    )

                print(f"   ✓ Indexed: {md_file.relative_to(docs_dir)} ({len(chunks)} chunks)")

            except Exception as e:
                print(f"   ✗ Error indexing {md_file}: {e}")

    def index_templates(self, templates_dir: Path):
        """Index bot templates"""
        if not templates_dir.exists():
            print(f"   ⚠ Directory not found: {templates_dir}")
            return

        for template_file in templates_dir.rglob("*"):
            if template_file.is_file():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    template_type = template_file.parent.name

                    # Index in Neo4j
                    with self.driver.session() as session:
                        session.run("""
                            MERGE (t:Template {path: $path})
                            SET t.name = $name,
                                t.type = $type,
                                t.size = $size
                        """,
                            path=str(template_file),
                            name=template_file.name,
                            type=template_type,
                            size=len(content)
                        )

                    # Index in ChromaDB
                    embedding = self.embedder.encode(content)

                    self.collection.add(
                        ids=[hashlib.md5(str(template_file).encode()).hexdigest()],
                        embeddings=[embedding.tolist()],
                        documents=[content],
                        metadatas=[{
                            'type': 'template',
                            'template_type': template_type,
                            'name': template_file.name,
                            'file_path': str(template_file)
                        }]
                    )

                    print(f"   ✓ Indexed: {template_file.name} ({template_type})")

                except Exception as e:
                    print(f"   ✗ Error indexing {template_file}: {e}")

    def index_container_specs(self, containers_dir: Path):
        """Index container specifications"""
        if not containers_dir.exists():
            print(f"   ⚠ Directory not found: {containers_dir}")
            return

        for yaml_file in containers_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    spec = yaml.safe_load(f)

                if not spec:
                    continue

                domain = self._extract_domain(yaml_file)

                # Index in Neo4j
                with self.driver.session() as session:
                    session.run("""
                        MERGE (c:Container {name: $name})
                        SET c.domain = $domain,
                            c.image = $image,
                            c.file_path = $file_path
                    """,
                        name=spec.get('name', yaml_file.stem),
                        domain=domain,
                        image=spec.get('image', ''),
                        file_path=str(yaml_file)
                    )

                    # Link containers to bots
                    bot_name = spec.get('bot_name')
                    if bot_name:
                        session.run("""
                            MATCH (c:Container {name: $container_name})
                            MERGE (b:Bot {name: $bot_name})
                            MERGE (b)-[:RUNS_IN]->(c)
                        """,
                            container_name=spec.get('name', yaml_file.stem),
                            bot_name=bot_name
                        )

                print(f"   ✓ Indexed: {yaml_file.name} ({domain})")

            except Exception as e:
                print(f"   ✗ Error indexing {yaml_file}: {e}")

    def index_bot_examples(self, repo_path: Path):
        """Index bot example code"""
        example_dirs = [
            repo_path / "eco-bots/examples",
            # Add other bot example directories as they exist
        ]

        for examples_dir in example_dirs:
            if not examples_dir.exists():
                continue

            for py_file in examples_dir.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()

                    domain = self._extract_domain(py_file)

                    # Index in Neo4j
                    with self.driver.session() as session:
                        session.run("""
                            MERGE (e:BotExample {path: $path})
                            SET e.name = $name,
                                e.domain = $domain,
                                e.language = 'python'
                        """,
                            path=str(py_file),
                            name=py_file.stem,
                            domain=domain
                        )

                    # Index in ChromaDB
                    embedding = self.embedder.encode(code)

                    self.collection.add(
                        ids=[hashlib.md5(str(py_file).encode()).hexdigest()],
                        embeddings=[embedding.tolist()],
                        documents=[code],
                        metadatas=[{
                            'type': 'bot_example',
                            'domain': domain,
                            'language': 'python',
                            'file_path': str(py_file)
                        }]
                    )

                    print(f"   ✓ Indexed: {py_file.name} ({domain})")

                except Exception as e:
                    print(f"   ✗ Error indexing {py_file}: {e}")

    def create_indexes(self):
        """Create Neo4j indexes for performance"""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX bot_name IF NOT EXISTS FOR (b:Bot) ON (b.name)",
                "CREATE INDEX bot_domain IF NOT EXISTS FOR (b:Bot) ON (b.domain)",
                "CREATE INDEX doc_path IF NOT EXISTS FOR (d:Document) ON (d.path)",
                "CREATE INDEX doc_domain IF NOT EXISTS FOR (d:Document) ON (d.domain)",
                "CREATE INDEX template_type IF NOT EXISTS FOR (t:Template) ON (t.type)",
                "CREATE INDEX container_name IF NOT EXISTS FOR (c:Container) ON (c.name)",
            ]

            for index in indexes:
                try:
                    session.run(index)
                    print(f"   ✓ Created index")
                except Exception as e:
                    print(f"   ⚠ Index may already exist: {e}")

    def print_statistics(self):
        """Print indexing statistics"""
        with self.driver.session() as session:
            # Count bots by domain
            result = session.run("""
                MATCH (b:Bot)
                RETURN b.domain as domain, count(b) as count
                ORDER BY domain
            """)

            print("\n📊 Knowledge Graph Statistics")
            print("=" * 50)
            print("\nBots by Domain:")
            for record in result:
                print(f"  {record['domain']}: {record['count']} bots")

            # Count other nodes
            for label in ['Document', 'Template', 'Container', 'BotExample']:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = result.single()['count']
                print(f"\n{label}s: {count}")

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()['count']
            print(f"\nRelationships: {rel_count}")

            # ChromaDB statistics
            print(f"\nVector embeddings: {self.collection.count()}")

    def _extract_domain(self, file_path: Path) -> str:
        """Extract domain (axis/pipe/eco/iv) from file path"""
        path_str = str(file_path).lower()

        if 'axis' in path_str:
            return 'AXIS'
        elif 'pipe' in path_str:
            return 'PIPE'
        elif 'eco' in path_str:
            return 'ECO'
        elif 'iv' in path_str:
            return 'IV'
        else:
            return 'GENERAL'

    def _extract_doc_type(self, file_path: Path) -> str:
        """Extract document type from path"""
        path_str = str(file_path).lower()

        if 'architecture' in path_str:
            return 'architecture'
        elif 'guide' in path_str or 'guides' in path_str:
            return 'guide'
        elif 'specification' in path_str:
            return 'specification'
        elif 'template' in path_str:
            return 'template'
        elif 'process' in path_str:
            return 'process'
        else:
            return 'documentation'

    def _chunk_text(self, text: str, max_size: int = 1000) -> List[str]:
        """Split text into chunks for embedding"""
        chunks = []
        lines = text.split('\n')

        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)

            if current_size + line_size > max_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def close(self):
        """Close connections"""
        self.driver.close()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "."

    indexer = BotSpecIndexer()

    try:
        indexer.index_repository(repo_path)
    finally:
        indexer.close()


if __name__ == "__main__":
    main()
