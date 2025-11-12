# Bot Utilities

Python utilities for bots to access and scan the bsw-arch documentation repository.

## 📦 Contents

- `doc_scanner.py` - Command-line tool for scanning and querying documentation
- `github_api_client.py` - GitHub API client for programmatic access
- `create_embeddings_chunks.py` - Create embeddings-ready document chunks

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/bsw-arch/bsw-arch.git /opt/documentation

# Install dependencies (Python 3.8+)
pip install pyyaml requests
```

### Basic Usage

```python
from doc_scanner import DocScanner

# Initialize scanner
scanner = DocScanner("/opt/documentation")

# Get critical priority documents
critical_docs = scanner.get_documents_by_priority("critical")

# Get documents for specific bot
axis_docs = scanner.get_documents_for_bot("axis-docs-bot")

# Read a document
content = scanner.read_document("arch-001")
```

## 🔧 Tools

### 1. Documentation Scanner (`doc_scanner.py`)

Provides programmatic access to documentation with filtering and search capabilities.

**CLI Usage:**

```bash
# List all initial scan documents
python3 doc_scanner.py --action list

# List critical priority documents
python3 doc_scanner.py --action list --priority critical

# List documents by category
python3 doc_scanner.py --action list --category architecture

# List documents for a specific domain
python3 doc_scanner.py --action list --domain AXIS

# List documents for a specific bot
python3 doc_scanner.py --action list --bot axis-docs-bot

# Scan all documents and export
python3 doc_scanner.py --action scan --output scan_results.json

# Read a specific document
python3 doc_scanner.py --action read --doc-id arch-001

# Get repository statistics
python3 doc_scanner.py --action stats

# Get domain information
python3 doc_scanner.py --action domain --domain PIPE
```

**Python API:**

```python
from doc_scanner import DocScanner

scanner = DocScanner()

# Load metadata and catalogue
scanner.load_metadata()
scanner.load_catalogue()

# Get documents by priority
critical = scanner.get_documents_by_priority("critical")
high = scanner.get_documents_by_priority("high")

# Get documents by category
architecture = scanner.get_documents_by_category("architecture")
guides = scanner.get_documents_by_category("guides")

# Get documents for bot
my_docs = scanner.get_documents_for_bot("axis-coordination-bot")

# Get initial scan documents
initial = scanner.get_initial_scan_documents()

# Read document content
content = scanner.read_document("arch-001")

# Get statistics
stats = scanner.get_statistics()
print(f"Total bots supported: {stats['bots_supported']}")

# Scan all documents
all_docs = scanner.scan_all_documents()
```

### 2. GitHub API Client (`github_api_client.py`)

Access documentation via GitHub API without cloning the repository.

**Usage:**

```python
from github_api_client import GitHubDocsClient

# Initialize client (optional GitHub token for higher rate limits)
client = GitHubDocsClient(token="your_github_token")

# Fetch metadata
metadata = client.get_metadata()
print(f"Repository: {metadata['repository']['name']}")
print(f"Bots supported: {metadata['statistics']['bots_supported']}")

# Fetch catalogue
catalogue = client.get_catalogue()
docs = catalogue['documents']

# Get a specific document
doc_content = client.get_document("docs/INDEX.md")

# List directory contents
files = client.list_directory("docs/architecture")

# Search for documents
results = client.search_documents("knowledge base")
```

**Rate Limits:**
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

### 3. Embeddings Chunk Creator (`create_embeddings_chunks.py`)

Splits documentation into embedding-ready chunks for RAG systems.

**Usage:**

```bash
# Create embeddings chunks
python3 create_embeddings_chunks.py
```

This generates `embeddings_chunks.json` with:
- Semantic chunks split by headings
- Max 1,000 characters per chunk
- Heading path context
- Token estimates
- Source file references

**Output Format:**

```json
[
  {
    "id": "COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS-0",
    "source_file": "docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md",
    "chunk_index": 0,
    "heading": "Executive Summary",
    "heading_path": "Executive Summary",
    "content": "...",
    "char_count": 856,
    "token_estimate": 214
  }
]
```

## 📊 Usage Patterns

### For AXIS Bots (Architecture)

```python
scanner = DocScanner()

# Get architecture-focused documents
docs = scanner.get_documents_by_category("architecture")
docs += scanner.get_documents_by_category("processes")

# Get AXIS-specific documents
axis_docs = scanner.get_documents_by_domain("AXIS")

# Recommended initial scan
initial = scanner.get_initial_scan_documents()
```

### For PIPE Bots (Pipeline)

```python
scanner = DocScanner()

# Get pipeline-focused documents
docs = scanner.get_documents_by_category("processes")
docs += scanner.get_documents_by_category("reference")

# Filter for PIPE-relevant topics
pipe_docs = [d for d in docs
             if any(topic in d.get('topics', [])
                   for topic in ['ci-cd', 'deployment', 'automation'])]
```

### For ECO Bots (Ecological)

```python
scanner = DocScanner()

# Get infrastructure and optimization docs
docs = scanner.get_documents_by_category("infrastructure")
docs += scanner.get_documents_by_priority("medium")

# Focus on container strategy
container_docs = [d for d in docs
                  if 'containers' in d.get('topics', [])]
```

### For IV Bots (Intelligence/Validation)

```python
scanner = DocScanner()

# Get AI/ML and knowledge base docs
docs = scanner.get_documents_by_category("guides")
kb_docs = [d for d in docs
           if 'knowledge-base' in d.get('topics', [])]

# Get validation and analysis docs
analysis_docs = scanner.get_documents_for_bot("iv-analysis-bot")
```

## 🔄 Update Detection

Check for documentation updates:

```python
import requests

# Fetch latest metadata
response = requests.get(
    "https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json"
)
metadata = response.json()

print(f"Version: {metadata['repository']['version']}")
print(f"Last updated: {metadata['repository']['updated']}")

# Compare with local version to detect changes
```

## 🐳 Docker Integration

Add to your bot's `Dockerfile`:

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install dependencies
RUN apk add git python-3.11 py3-pip

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install pyyaml requests

# Add bot-utils to Python path
ENV PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"
ENV DOCS_PATH="/opt/documentation/docs"

# Your bot code
COPY . /app
WORKDIR /app

CMD ["python3", "main.py"]
```

## 📝 Example Bot Implementation

```python
#!/usr/bin/env python3
"""Example bot using documentation scanner"""

import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner

def main():
    # Initialize scanner
    scanner = DocScanner("/opt/documentation")

    # Get recommended documents for this bot
    bot_name = "axis-docs-bot"
    docs = scanner.get_documents_for_bot(bot_name)

    print(f"📚 Found {len(docs)} documents for {bot_name}")

    # Read and process each document
    for doc in docs:
        print(f"\n📄 Processing: {doc['title']}")
        content = scanner.read_document(doc['id'])

        if content:
            # Process document content
            # (implement your bot logic here)
            print(f"  ✅ Processed {len(content)} characters")

if __name__ == "__main__":
    main()
```

## 🔗 Related Documentation

- [Documentation Index](../docs/INDEX.md)
- [Metadata Schema](../docs/metadata.json)
- [Document Catalogue](../docs/catalogue.yaml)
- [Changelog](../docs/CHANGELOG.md)

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
