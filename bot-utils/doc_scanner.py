#!/usr/bin/env python3
"""
BSW-Arch Documentation Scanner for Bots
Provides programmatic access to documentation repository
"""

import json
import yaml
import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Document:
    """Represents a documentation file"""
    id: str
    title: str
    path: str
    category: str
    priority: str
    size_bytes: int
    size_lines: int
    topics: List[str]
    bot_relevance: List[str]
    checksum: str
    last_modified: str

class DocScanner:
    """Scanner for BSW-Arch documentation repository"""

    def __init__(self, repo_path: str = "/opt/documentation"):
        self.repo_path = Path(repo_path)
        self.docs_path = self.repo_path / "docs"
        self.metadata_path = self.docs_path / "metadata.json"
        self.catalogue_path = self.docs_path / "catalogue.yaml"
        self.metadata: Dict = {}
        self.catalogue: Dict = {}

    def load_metadata(self) -> bool:
        """Load metadata.json"""
        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading metadata: {e}", file=sys.stderr)
            return False

    def load_catalogue(self) -> bool:
        """Load catalogue.yaml"""
        try:
            with open(self.catalogue_path, 'r') as f:
                self.catalogue = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading catalogue: {e}", file=sys.stderr)
            return False

    def get_documents_by_priority(self, priority: str) -> List[Dict]:
        """Get all documents matching a priority level"""
        if not self.catalogue:
            self.load_catalogue()

        documents = self.catalogue.get('documents', [])
        return [doc for doc in documents if doc.get('priority') == priority]

    def get_documents_by_category(self, category: str) -> List[Dict]:
        """Get all documents in a category"""
        if not self.catalogue:
            self.load_catalogue()

        documents = self.catalogue.get('documents', [])
        return [doc for doc in documents if doc.get('category') == category]

    def get_documents_for_bot(self, bot_name: str) -> List[Dict]:
        """Get recommended documents for a specific bot"""
        if not self.catalogue:
            self.load_catalogue()

        documents = self.catalogue.get('documents', [])
        return [doc for doc in documents
                if bot_name in doc.get('bot_relevance', [])]

    def get_documents_by_domain(self, domain: str) -> List[Dict]:
        """Get documents relevant to a domain (AXIS, PIPE, ECO, IV)"""
        if not self.catalogue:
            self.load_catalogue()

        domain = domain.upper()
        documents = self.catalogue.get('documents', [])
        return [doc for doc in documents
                if domain in doc.get('domains', [])]

    def get_initial_scan_documents(self) -> List[Dict]:
        """Get recommended documents for initial bot scan"""
        if not self.catalogue:
            self.load_catalogue()

        scan_config = self.catalogue.get('scanning_recommendations', {}).get('initial_scan', {})
        doc_ids = scan_config.get('order', [])

        documents = self.catalogue.get('documents', [])
        result = []
        for doc_id in doc_ids:
            for doc in documents:
                if doc.get('id') == doc_id:
                    result.append(doc)
                    break
        return result

    def read_document(self, doc_id: str) -> Optional[str]:
        """Read the contents of a document by ID"""
        if not self.catalogue:
            self.load_catalogue()

        documents = self.catalogue.get('documents', [])
        doc = next((d for d in documents if d.get('id') == doc_id), None)

        if not doc:
            return None

        doc_path = self.repo_path / doc['path']
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading document {doc_id}: {e}", file=sys.stderr)
            return None

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except:
            return ""

    def scan_all_documents(self) -> List[Document]:
        """Scan all markdown documents in the repository"""
        documents = []

        for md_file in self.docs_path.rglob("*.md"):
            try:
                stat = md_file.stat()
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    line_count = len(content.splitlines())

                # Extract title from first heading
                title = md_file.stem
                for line in content.splitlines()[:10]:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break

                doc = Document(
                    id=md_file.stem,
                    title=title,
                    path=str(md_file.relative_to(self.repo_path)),
                    category=md_file.parent.name,
                    priority="unknown",
                    size_bytes=stat.st_size,
                    size_lines=line_count,
                    topics=[],
                    bot_relevance=[],
                    checksum=self.calculate_checksum(md_file),
                    last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
                )
                documents.append(doc)
            except Exception as e:
                print(f"⚠️  Error scanning {md_file}: {e}", file=sys.stderr)

        return documents

    def get_statistics(self) -> Dict:
        """Get repository statistics"""
        if not self.metadata:
            self.load_metadata()

        return self.metadata.get('statistics', {})

    def get_domain_info(self, domain: str) -> Optional[Dict]:
        """Get information about a specific domain"""
        if not self.metadata:
            self.load_metadata()

        domains = self.metadata.get('domains', [])
        return next((d for d in domains if d['id'] == domain.upper()), None)

    def export_scan_results(self, output_file: str, format: str = 'json'):
        """Export scan results to file"""
        documents = self.scan_all_documents()

        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump([asdict(doc) for doc in documents], f, indent=2)
        elif format == 'yaml':
            with open(output_file, 'w') as f:
                yaml.dump([asdict(doc) for doc in documents], f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"✅ Exported {len(documents)} documents to {output_file}")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="BSW-Arch Documentation Scanner for Bots"
    )
    parser.add_argument(
        '--repo-path',
        default='/opt/documentation',
        help='Path to documentation repository'
    )
    parser.add_argument(
        '--action',
        choices=['list', 'scan', 'read', 'stats', 'domain', 'bot'],
        required=True,
        help='Action to perform'
    )
    parser.add_argument(
        '--priority',
        choices=['critical', 'high', 'medium', 'low'],
        help='Filter by priority'
    )
    parser.add_argument(
        '--category',
        help='Filter by category'
    )
    parser.add_argument(
        '--domain',
        choices=['AXIS', 'PIPE', 'ECO', 'IV'],
        help='Filter by domain'
    )
    parser.add_argument(
        '--bot',
        help='Filter for specific bot name'
    )
    parser.add_argument(
        '--doc-id',
        help='Document ID to read'
    )
    parser.add_argument(
        '--output',
        help='Output file for export'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'yaml'],
        default='json',
        help='Output format'
    )

    args = parser.parse_args()

    scanner = DocScanner(args.repo_path)

    if args.action == 'list':
        if args.priority:
            docs = scanner.get_documents_by_priority(args.priority)
            print(f"\n📋 Documents with priority '{args.priority}':")
        elif args.category:
            docs = scanner.get_documents_by_category(args.category)
            print(f"\n📋 Documents in category '{args.category}':")
        elif args.domain:
            docs = scanner.get_documents_by_domain(args.domain)
            print(f"\n📋 Documents for domain '{args.domain}':")
        elif args.bot:
            docs = scanner.get_documents_for_bot(args.bot)
            print(f"\n📋 Documents for bot '{args.bot}':")
        else:
            docs = scanner.get_initial_scan_documents()
            print("\n📋 Initial scan documents:")

        for doc in docs:
            print(f"  [{doc.get('id')}] {doc.get('title')}")
            print(f"      Priority: {doc.get('priority')} | Category: {doc.get('category')}")
            print(f"      Path: {doc.get('path')}")
            print()

    elif args.action == 'scan':
        print("\n🔍 Scanning all documents...")
        if args.output:
            scanner.export_scan_results(args.output, args.format)
        else:
            docs = scanner.scan_all_documents()
            print(f"\n✅ Found {len(docs)} documents:")
            for doc in docs:
                print(f"  - {doc.title} ({doc.size_lines} lines, {doc.size_bytes} bytes)")

    elif args.action == 'read':
        if not args.doc_id:
            print("❌ --doc-id required for read action", file=sys.stderr)
            sys.exit(1)

        content = scanner.read_document(args.doc_id)
        if content:
            print(f"\n📄 Content of document '{args.doc_id}':\n")
            print(content)
        else:
            print(f"❌ Document '{args.doc_id}' not found", file=sys.stderr)
            sys.exit(1)

    elif args.action == 'stats':
        stats = scanner.get_statistics()
        print("\n📊 Repository Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif args.action == 'domain':
        if not args.domain:
            print("❌ --domain required for domain action", file=sys.stderr)
            sys.exit(1)

        domain_info = scanner.get_domain_info(args.domain)
        if domain_info:
            print(f"\n🏗️  Domain: {domain_info['name']} ({domain_info['id']})")
            print(f"  Purpose: {domain_info['purpose']}")
            print(f"  Bots: {domain_info['bots_count']}")
            print(f"  Key bots: {', '.join(domain_info['key_bots'])}")
        else:
            print(f"❌ Domain '{args.domain}' not found", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
