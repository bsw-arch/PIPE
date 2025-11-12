# Proton Drive Integration for IV Bots and CAG+RAG Architecture

## Executive Summary

This guide demonstrates how to integrate Proton Drive as a secure, FAGAM-compliant documentation repository for the IV bots and CAG+RAG architecture. Proton Drive serves as the secure cloud storage layer while maintaining the privacy-first, locally-executed AI infrastructure.

**Key Benefits:**
- ✅ **FAGAM Compliant**: Proton is Switzerland-based, not part of FAGAM
- ✅ **End-to-End Encrypted**: All documents encrypted at rest
- ✅ **Privacy First**: Aligns with local LLM architecture
- ✅ **Secure Collaboration**: Team access with encryption
- ✅ **Version Control**: Document versioning and history
- ✅ **Automated Sync**: Continuous documentation updates

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Proton Drive Setup](#2-proton-drive-setup)
3. [Integration Patterns](#3-integration-patterns)
4. [IV Bots Integration](#4-iv-bots-integration)
5. [CAG+RAG Integration](#5-cag-rag-integration)
6. [OpenCode/OpenSpec Integration](#6-opencodeOpenspec-integration)
7. [Automated Sync Workflows](#7-automated-sync-workflows)
8. [Security Considerations](#8-security-considerations)
9. [Implementation Examples](#9-implementation-examples)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Architecture Overview

### 1.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROTON DRIVE CLOUD LAYER                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Encrypted Documentation Repository                │  │
│  │  • bsw-arch/docs/        (Architecture docs)             │  │
│  │  • bsw-arch/specs/       (OpenSpec specifications)       │  │
│  │  • bsw-arch/knowledge/   (RAG knowledge base)            │  │
│  │  • bsw-arch/bot-configs/ (IV bot configurations)         │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────────────┘
                        │
                        │ Encrypted Sync (ProtonDrive CLI/API)
                        │
┌───────────────────────┼──────────────────────────────────────────┐
│              LOCAL INFRASTRUCTURE LAYER                          │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │           Proton Drive Sync Agent                         │  │
│  │  • proton-drive-sync.py                                   │  │
│  │  • Watches for remote changes                             │  │
│  │  • Syncs to /opt/documentation                            │  │
│  │  • Triggers knowledge base updates                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Local Documentation Cache                        │   │
│  │         /opt/documentation/                              │   │
│  │  • Mirrored from Proton Drive                            │   │
│  │  • Used by IV bots                                       │   │
│  │  • Indexed by knowledge graph                            │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                          │
│       ┌───────────────┼───────────────┐                         │
│       │               │               │                         │
│       ▼               ▼               ▼                         │
│  ┌─────────┐  ┌──────────────┐  ┌────────────┐                │
│  │ IV Bots │  │ Knowledge    │  │ OpenCode   │                │
│  │         │  │ Graph (Neo4j)│  │ + OpenSpec │                │
│  │ 44 bots │  │ + ChromaDB   │  │ Workflows  │                │
│  └─────────┘  └──────────────┘  └────────────┘                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
Documentation Update Workflow:

1. Team Member → Proton Drive (Web/Desktop)
   - Upload/edit documentation
   - End-to-end encrypted

2. Proton Drive → Local Sync Agent
   - Webhook or polling detects changes
   - Downloads encrypted files
   - Decrypts locally

3. Sync Agent → Knowledge Graph
   - Triggers iv-docs-bot
   - Re-indexes changed documents
   - Updates embeddings

4. Knowledge Graph → IV Bots
   - Updated context available
   - RAG queries use latest docs
   - CAG layer has fresh context
```

---

## 2. Proton Drive Setup

### 2.1 Prerequisites

```bash
# Proton Account Requirements
- Proton account (free or paid)
- Proton Drive storage (recommended: 200GB+ for team documentation)
- API access enabled

# System Requirements
- Python 3.10+
- Linux/macOS (Windows via WSL)
- Network access to Proton services
```

### 2.2 Install Proton Bridge/CLI

#### Option 1: Proton Bridge (GUI)

```bash
# Download from: https://proton.me/drive/download

# Linux (Debian/Ubuntu)
wget https://proton.me/download/bridge/protonmail-bridge_3.0.0-1_amd64.deb
sudo dpkg -i protonmail-bridge_3.0.0-1_amd64.deb

# macOS
brew install --cask protonmail-bridge

# Configure Bridge
protonmail-bridge --cli
> login
> info
> exit
```

#### Option 2: Proton Drive Python Library

```bash
# Install Proton Drive Python client
pip install --break-system-packages \
    proton-drive-cli \
    proton-core \
    watchdog \
    python-dotenv

# Or build from source
git clone https://github.com/proton-community/proton-drive-cli
cd proton-drive-cli
pip install -e .
```

### 2.3 Authentication

```bash
# Create credentials file
mkdir -p ~/.config/proton-drive
cat > ~/.config/proton-drive/credentials.env << 'EOF'
PROTON_USERNAME=your-email@proton.me
PROTON_PASSWORD=your-secure-password
PROTON_2FA_SECRET=your-2fa-secret  # Optional but recommended
PROTON_DRIVE_ROOT=/bsw-arch
EOF

chmod 600 ~/.config/proton-drive/credentials.env

# Test authentication
proton-drive-cli login
proton-drive-cli list
```

### 2.4 Directory Structure in Proton Drive

```
Proton Drive: /bsw-arch/
├── docs/
│   ├── architecture/
│   │   ├── COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
│   │   ├── CAG-RAG-SOLUTION-ARCHITECTURE.md
│   │   └── components/
│   │       └── BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
│   ├── guides/
│   │   ├── setup/
│   │   │   └── IV-BOTS-SETUP.md
│   │   └── development/
│   │       └── BSW-TECH-AI-INTEGRATION-GUIDE.md
│   ├── specifications/
│   │   └── bots/
│   │       └── iv-bots.yaml
│   └── reference/
├── openspec/
│   ├── specs/
│   ├── changes/
│   └── project.md
├── bot-utils/
│   ├── doc_scanner.py
│   ├── github_api_client.py
│   └── create_embeddings_chunks.py
└── metadata.json
```

---

## 3. Integration Patterns

### 3.1 Pattern 1: Direct Sync (Simple)

**Use Case**: Single-user or small team, infrequent updates

```python
#!/usr/bin/env python3
"""
Simple Proton Drive sync for documentation
"""

import os
import subprocess
from pathlib import Path

def sync_proton_drive():
    """Sync Proton Drive to local directory"""

    # Proton Drive remote path
    remote_path = "/bsw-arch"

    # Local cache path
    local_path = "/opt/documentation"

    # Sync using proton-drive-cli
    print(f"🔄 Syncing {remote_path} → {local_path}")

    result = subprocess.run([
        "proton-drive-cli", "sync",
        "--remote", remote_path,
        "--local", local_path,
        "--recursive"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Sync complete")
        return True
    else:
        print(f"❌ Sync failed: {result.stderr}")
        return False

if __name__ == "__main__":
    sync_proton_drive()
```

### 3.2 Pattern 2: Continuous Sync (Advanced)

**Use Case**: Active development, real-time updates needed

```python
#!/usr/bin/env python3
"""
Continuous Proton Drive sync with change detection
"""

import time
import hashlib
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProtonDriveSyncHandler(FileSystemEventHandler):
    def __init__(self, local_path, on_change_callback):
        self.local_path = Path(local_path)
        self.on_change_callback = on_change_callback
        self.file_hashes = {}
        self._load_hashes()

    def _load_hashes(self):
        """Load previous file hashes"""
        hash_file = self.local_path / ".sync_hashes.json"
        if hash_file.exists():
            with open(hash_file) as f:
                self.file_hashes = json.load(f)

    def _save_hashes(self):
        """Save current file hashes"""
        hash_file = self.local_path / ".sync_hashes.json"
        with open(hash_file, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)

    def _get_file_hash(self, file_path):
        """Calculate file hash"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip hidden files and sync metadata
        if file_path.name.startswith('.'):
            return

        # Calculate hash
        try:
            new_hash = self._get_file_hash(file_path)
        except Exception as e:
            print(f"⚠️  Error hashing {file_path}: {e}")
            return

        # Check if actually changed
        rel_path = str(file_path.relative_to(self.local_path))
        old_hash = self.file_hashes.get(rel_path)

        if new_hash != old_hash:
            print(f"📝 File changed: {rel_path}")
            self.file_hashes[rel_path] = new_hash
            self._save_hashes()

            # Trigger callback
            if self.on_change_callback:
                self.on_change_callback(file_path)

class ContinuousProtonSync:
    def __init__(self, remote_path, local_path, poll_interval=60):
        self.remote_path = remote_path
        self.local_path = Path(local_path)
        self.poll_interval = poll_interval
        self.observer = None

    def on_file_changed(self, file_path):
        """Callback when file changes"""
        print(f"🔄 Change detected: {file_path}")

        # Trigger knowledge base update
        self.trigger_kb_update(file_path)

    def trigger_kb_update(self, file_path):
        """Trigger IV bots to update knowledge base"""
        import subprocess

        # Re-index changed file
        subprocess.run([
            "python3", "/opt/documentation/bot-utils/graph_indexer.py",
            str(file_path),
            "--incremental"
        ])

        print(f"✅ Knowledge base updated for: {file_path}")

    def sync_from_remote(self):
        """Sync from Proton Drive"""
        import subprocess

        print(f"⬇️  Syncing from Proton Drive...")

        result = subprocess.run([
            "proton-drive-cli", "sync",
            "--remote", self.remote_path,
            "--local", str(self.local_path),
            "--recursive"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Sync complete")
            return True
        else:
            print(f"❌ Sync failed: {result.stderr}")
            return False

    def start_watching(self):
        """Start watching local directory for changes"""
        event_handler = ProtonDriveSyncHandler(
            self.local_path,
            self.on_file_changed
        )

        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.local_path), recursive=True)
        self.observer.start()

        print(f"👀 Watching {self.local_path} for changes...")

    def run(self):
        """Run continuous sync"""
        self.start_watching()

        try:
            while True:
                # Periodic sync from remote
                self.sync_from_remote()

                # Wait for next sync
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n🛑 Stopping sync...")
            if self.observer:
                self.observer.stop()
                self.observer.join()

# Usage
if __name__ == "__main__":
    sync = ContinuousProtonSync(
        remote_path="/bsw-arch",
        local_path="/opt/documentation",
        poll_interval=300  # 5 minutes
    )
    sync.run()
```

### 3.3 Pattern 3: On-Demand Sync (Event-Driven)

**Use Case**: Manual control, triggered by specific events

```python
#!/usr/bin/env python3
"""
On-demand Proton Drive sync triggered by events
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Proton Drive Sync API")

class SyncRequest(BaseModel):
    path: str = "/"
    force: bool = False

class ProtonDriveSyncAPI:
    def __init__(self, remote_root="/bsw-arch", local_root="/opt/documentation"):
        self.remote_root = remote_root
        self.local_root = local_root

    async def sync_path(self, path: str, force: bool = False) -> dict:
        """Sync specific path from Proton Drive"""
        import subprocess

        remote_path = f"{self.remote_root}/{path}"
        local_path = f"{self.local_root}/{path}"

        cmd = [
            "proton-drive-cli", "sync",
            "--remote", remote_path,
            "--local", local_path
        ]

        if force:
            cmd.append("--force")

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "success": result.returncode == 0,
            "path": path,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

sync_api = ProtonDriveSyncAPI()

@app.post("/sync")
async def sync_documentation(request: SyncRequest):
    """Sync documentation from Proton Drive"""
    result = await sync_api.sync_path(request.path, request.force)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])

    return result

@app.post("/sync/full")
async def sync_full():
    """Sync entire documentation"""
    result = await sync_api.sync_path("/", force=False)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])

    return {"message": "Full sync complete", "details": result}

@app.get("/status")
async def sync_status():
    """Get sync status"""
    import os
    from datetime import datetime

    sync_marker = f"{sync_api.local_root}/.last_sync"

    if os.path.exists(sync_marker):
        mtime = os.path.getmtime(sync_marker)
        last_sync = datetime.fromtimestamp(mtime).isoformat()
    else:
        last_sync = "Never"

    return {
        "local_path": sync_api.local_root,
        "remote_path": sync_api.remote_root,
        "last_sync": last_sync
    }

# Run: uvicorn proton_sync_api:app --host 0.0.0.0 --port 8090
```

---

## 4. IV Bots Integration

### 4.1 Modified IV Bot Initialization

Update IV bot Dockerfiles to include Proton Drive sync:

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install dependencies
RUN apk add --no-cache \
    git \
    python-3.11 \
    py3-pip \
    py3-numpy \
    py3-scipy

# Install Proton Drive sync dependencies
RUN pip install --no-cache-dir \
    proton-drive-cli \
    watchdog \
    python-dotenv

# Create documentation directory
WORKDIR /opt
RUN mkdir -p /opt/documentation

# Copy Proton Drive sync script
COPY proton-drive-sync.py /opt/proton-drive-sync.py

# Copy bot code
COPY . /app
WORKDIR /app

# Environment for Proton Drive
ENV PROTON_DRIVE_ROOT="/bsw-arch"
ENV DOCS_PATH="/opt/documentation/docs"
ENV PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"

# Non-root user
RUN addgroup -g 65532 nonroot && \
    adduser -u 65532 -G nonroot -s /bin/sh -D nonroot && \
    chown -R nonroot:nonroot /app /opt

USER nonroot

# Sync documentation on startup, then run bot
CMD python3 /opt/proton-drive-sync.py --once && python3 main.py
```

### 4.2 IV Bot Startup Script with Sync

```python
#!/usr/bin/env python3
"""
IV Bot startup with Proton Drive documentation sync
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_documentation():
    """Sync documentation from Proton Drive before starting bot"""

    remote_path = os.getenv("PROTON_DRIVE_ROOT", "/bsw-arch")
    local_path = "/opt/documentation"

    logger.info(f"📥 Syncing documentation from Proton Drive...")
    logger.info(f"   Remote: {remote_path}")
    logger.info(f"   Local: {local_path}")

    try:
        # Check if proton-drive-cli is available
        result = subprocess.run(
            ["proton-drive-cli", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.warning("⚠️  Proton Drive CLI not available, using git clone fallback")
            return sync_git_fallback()

        # Sync from Proton Drive
        result = subprocess.run([
            "proton-drive-cli", "sync",
            "--remote", remote_path,
            "--local", local_path,
            "--recursive"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logger.info("✅ Documentation synced successfully")
            return True
        else:
            logger.error(f"❌ Sync failed: {result.stderr}")
            return sync_git_fallback()

    except subprocess.TimeoutExpired:
        logger.error("❌ Sync timeout (5 minutes)")
        return sync_git_fallback()

    except Exception as e:
        logger.error(f"❌ Sync error: {e}")
        return sync_git_fallback()

def sync_git_fallback():
    """Fallback to git clone if Proton Drive sync fails"""
    logger.info("📦 Falling back to git clone...")

    result = subprocess.run([
        "git", "clone",
        "https://github.com/bsw-arch/bsw-arch.git",
        "/opt/documentation"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        logger.info("✅ Git clone successful")
        return True
    else:
        logger.error(f"❌ Git clone failed: {result.stderr}")
        return False

def verify_documentation():
    """Verify required documentation files exist"""
    required_files = [
        "/opt/documentation/docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md",
        "/opt/documentation/docs/guides/setup/IV-BOTS-SETUP.md",
        "/opt/documentation/bot-utils/doc_scanner.py"
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        logger.warning(f"⚠️  Missing files: {missing}")
        return False

    logger.info("✅ All required documentation files present")
    return True

def main():
    """Main startup sequence"""
    logger.info("🚀 Starting IV Bot with Proton Drive sync...")

    # Step 1: Sync documentation
    if not sync_documentation():
        logger.error("❌ Failed to sync documentation")
        sys.exit(1)

    # Step 2: Verify documentation
    if not verify_documentation():
        logger.warning("⚠️  Documentation incomplete, but continuing...")

    # Step 3: Start the actual bot
    logger.info("🤖 Starting IV bot...")

    # Add bot-utils to Python path
    sys.path.insert(0, "/opt/documentation/bot-utils")

    # Import and run the actual bot
    from iv_bot_main import run_bot
    run_bot()

if __name__ == "__main__":
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Sync once and exit")
    args = parser.parse_args()

    if args.once:
        sync_documentation()
        verify_documentation()
    else:
        main()
```

### 4.3 Kubernetes ConfigMap for Proton Credentials

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: proton-drive-credentials
  namespace: iv-bots
type: Opaque
stringData:
  username: your-email@proton.me
  password: your-secure-password
  2fa-secret: your-2fa-secret
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: proton-drive-config
  namespace: iv-bots
data:
  remote-root: "/bsw-arch"
  sync-interval: "300"  # 5 minutes
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iv-rag-bot
  namespace: iv-bots
spec:
  replicas: 3
  selector:
    matchLabels:
      app: iv-rag-bot
  template:
    metadata:
      labels:
        app: iv-rag-bot
    spec:
      containers:
      - name: iv-rag-bot
        image: bsw-arch/iv-rag-bot:latest
        env:
        - name: PROTON_USERNAME
          valueFrom:
            secretKeyRef:
              name: proton-drive-credentials
              key: username
        - name: PROTON_PASSWORD
          valueFrom:
            secretKeyRef:
              name: proton-drive-credentials
              key: password
        - name: PROTON_2FA_SECRET
          valueFrom:
            secretKeyRef:
              name: proton-drive-credentials
              key: 2fa-secret
        - name: PROTON_DRIVE_ROOT
          valueFrom:
            configMapKeyRef:
              name: proton-drive-config
              key: remote-root
        volumeMounts:
        - name: documentation
          mountPath: /opt/documentation
      volumes:
      - name: documentation
        emptyDir: {}
```

---

## 5. CAG+RAG Integration

### 5.1 Proton Drive as Knowledge Source

Update the CAG+RAG pipeline to use Proton Drive as the primary documentation source:

```python
#!/usr/bin/env python3
"""
CAG+RAG Pipeline with Proton Drive Integration
"""

import os
from pathlib import Path
from typing import Dict, List, Any

class ProtonDriveCAGRAG:
    def __init__(self):
        self.proton_root = os.getenv("PROTON_DRIVE_ROOT", "/bsw-arch")
        self.local_cache = Path("/opt/documentation")
        self.sync_interval = int(os.getenv("SYNC_INTERVAL", "300"))

        # Initialize components
        self.doc_scanner = None
        self.knowledge_graph = None
        self.vector_store = None

    async def initialize(self):
        """Initialize CAG+RAG with Proton Drive sync"""

        # Step 1: Sync documentation
        await self.sync_documentation()

        # Step 2: Initialize doc scanner
        from doc_scanner import DocScanner
        self.doc_scanner = DocScanner(str(self.local_cache))

        # Step 3: Initialize knowledge graph
        from neo4j import GraphDatabase
        self.knowledge_graph = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password")
            )
        )

        # Step 4: Initialize vector store
        import chromadb
        self.vector_store = chromadb.PersistentClient(
            path=os.getenv("CHROMA_PATH", "./chroma_db")
        )

        # Step 5: Index documents if needed
        await self.index_if_needed()

    async def sync_documentation(self):
        """Sync documentation from Proton Drive"""
        import subprocess

        result = subprocess.run([
            "proton-drive-cli", "sync",
            "--remote", self.proton_root,
            "--local", str(self.local_cache),
            "--recursive"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"Proton Drive sync failed: {result.stderr}")

    async def index_if_needed(self):
        """Index documents if knowledge base is empty or outdated"""

        # Check if indexing needed
        marker_file = self.local_cache / ".indexed"
        docs_dir = self.local_cache / "docs"

        if not marker_file.exists():
            # Never indexed
            await self.index_all_documents()
        else:
            # Check if docs changed since last index
            marker_time = marker_file.stat().st_mtime

            changed_files = []
            for doc_file in docs_dir.rglob("*.md"):
                if doc_file.stat().st_mtime > marker_time:
                    changed_files.append(doc_file)

            if changed_files:
                # Incremental index
                await self.index_documents(changed_files)

    async def index_all_documents(self):
        """Full index of all documents"""
        import subprocess

        print("📚 Indexing all documents...")

        result = subprocess.run([
            "python3",
            str(self.local_cache / "bot-utils" / "graph_indexer.py"),
            str(self.local_cache / "docs")
        ], capture_output=True, text=True)

        if result.returncode == 0:
            # Mark as indexed
            (self.local_cache / ".indexed").touch()
            print("✅ Indexing complete")
        else:
            raise Exception(f"Indexing failed: {result.stderr}")

    async def index_documents(self, files: List[Path]):
        """Incremental index of specific documents"""
        import subprocess

        print(f"📝 Incrementally indexing {len(files)} files...")

        for file in files:
            result = subprocess.run([
                "python3",
                str(self.local_cache / "bot-utils" / "graph_indexer.py"),
                str(file),
                "--incremental"
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"⚠️  Failed to index {file}: {result.stderr}")

        # Update marker
        (self.local_cache / ".indexed").touch()
        print("✅ Incremental indexing complete")

    async def query(self, question: str, domains: List[str] = None) -> Dict[str, Any]:
        """
        Process CAG+RAG query with Proton Drive-backed knowledge
        """

        # TIER 1: Context-Aware Generation
        context = await self.build_context(question, domains)

        # TIER 2: Retrieval-Augmented Generation
        retrieved_docs = await self.retrieve_documents(question, context)

        # Generate response
        response = await self.generate_response(question, retrieved_docs, context)

        return response

    async def build_context(self, question: str, domains: List[str]) -> Dict[str, Any]:
        """Build context from user query and domain info"""

        # Classify query
        classified = self.classify_query(question)

        # Get domain-specific context
        domain_context = {}
        if domains:
            for domain in domains:
                docs = self.doc_scanner.get_documents_by_domain(domain)
                domain_context[domain] = docs

        return {
            "question": question,
            "classification": classified,
            "domains": domain_context,
            "timestamp": str(datetime.now())
        }

    async def retrieve_documents(self, question: str, context: Dict) -> List[Dict]:
        """Retrieve relevant documents using hybrid search"""

        # This would use the knowledge graph and vector store
        # Implementation similar to IV-BOTS-SETUP.md examples

        pass

    async def generate_response(self, question: str, docs: List[Dict], context: Dict) -> Dict:
        """Generate response using LLM with retrieved context"""

        # This would call Ollama or Claude
        # Implementation similar to IV-BOTS-SETUP.md examples

        pass

# Usage
async def main():
    pipeline = ProtonDriveCAGRAG()
    await pipeline.initialize()

    result = await pipeline.query(
        "How does the bot factory handle deployment?",
        domains=["PIPE", "IV"]
    )

    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 6. OpenCode/OpenSpec Integration

### 6.1 OpenSpec with Proton Drive Specs

Configure OpenSpec to use Proton Drive as the spec repository:

```bash
# Initialize OpenSpec with Proton Drive
cd /path/to/project

# Create symlink to Proton Drive-synced specs
ln -s /opt/documentation/openspec ./openspec

# Or configure OpenSpec to use Proton Drive location
cat > .openspec.json << 'EOF'
{
  "specsDir": "/opt/documentation/openspec/specs",
  "changesDir": "/opt/documentation/openspec/changes",
  "projectFile": "/opt/documentation/openspec/project.md",
  "agentsFile": "/opt/documentation/openspec/AGENTS.md"
}
EOF
```

### 6.2 Custom OpenCode Command for Proton Sync

File: `.opencode/commands/proton-sync.md`

```markdown
---
description: "Sync documentation from Proton Drive and refresh knowledge"
---

Syncing documentation from Proton Drive...

1. Pull latest documentation:
   - Run proton-drive-cli sync
   - Check for updated files
   - Verify sync completed successfully

2. Refresh knowledge base:
   - Re-index changed documents
   - Update embeddings
   - Rebuild knowledge graph

3. Report changes:
   - List updated files
   - Show new documentation
   - Highlight breaking changes

Ready to work with latest documentation!
```

### 6.3 Integration with OpenCode Knowledge Graph Guide

Combine the Proton Drive sync with the OpenCode knowledge graph from the guide you provided:

```python
#!/usr/bin/env python3
"""
Complete integration:
Proton Drive → Local Docs → Neo4j Knowledge Graph → OpenCode
"""

import subprocess
from pathlib import Path

class ProtonOpenCodeIntegration:
    def __init__(self):
        self.proton_root = "/bsw-arch"
        self.local_docs = Path("/opt/documentation")
        self.graph_indexer = self.local_docs / "bot-utils" / "graph_indexer.py"

    def sync_from_proton(self) -> bool:
        """Step 1: Sync from Proton Drive"""
        print("📥 Syncing from Proton Drive...")

        result = subprocess.run([
            "proton-drive-cli", "sync",
            "--remote", self.proton_root,
            "--local", str(self.local_docs),
            "--recursive"
        ], capture_output=True, text=True)

        return result.returncode == 0

    def index_to_graph(self) -> bool:
        """Step 2: Index to Neo4j knowledge graph"""
        print("📊 Indexing to knowledge graph...")

        result = subprocess.run([
            "python3", str(self.graph_indexer),
            str(self.local_docs / "docs"),
            "--neo4j-uri", "bolt://localhost:7687",
            "--neo4j-user", "neo4j",
            "--neo4j-password", "password"
        ], capture_output=True, text=True)

        return result.returncode == 0

    def start_mcp_server(self):
        """Step 3: Start MCP server for OpenCode"""
        print("🚀 Starting MCP server...")

        subprocess.Popen([
            "python3",
            str(self.local_docs / "bot-utils" / "mcp_server.py")
        ])

    def run_full_sync(self):
        """Run complete sync pipeline"""
        print("🔄 Starting full Proton Drive → OpenCode sync...")

        if not self.sync_from_proton():
            print("❌ Proton sync failed")
            return False

        if not self.index_to_graph():
            print("❌ Graph indexing failed")
            return False

        self.start_mcp_server()

        print("✅ Full sync complete! OpenCode ready with latest docs.")
        return True

# Usage
if __name__ == "__main__":
    integration = ProtonOpenCodeIntegration()
    integration.run_full_sync()
```

---

## 7. Automated Sync Workflows

### 7.1 Systemd Service (Linux)

File: `/etc/systemd/system/proton-drive-sync.service`

```ini
[Unit]
Description=Proton Drive Documentation Sync
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=bsw-arch
Group=bsw-arch
WorkingDirectory=/opt/documentation
Environment="PROTON_DRIVE_ROOT=/bsw-arch"
Environment="DOCS_PATH=/opt/documentation"
ExecStart=/usr/bin/python3 /opt/proton-drive-sync.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable proton-drive-sync
sudo systemctl start proton-drive-sync
sudo systemctl status proton-drive-sync
```

### 7.2 Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: proton-drive-sync
  namespace: iv-bots
spec:
  schedule: "*/15 * * * *"  # Every 15 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sync
            image: bsw-arch/proton-drive-sync:latest
            env:
            - name: PROTON_USERNAME
              valueFrom:
                secretKeyRef:
                  name: proton-drive-credentials
                  key: username
            - name: PROTON_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: proton-drive-credentials
                  key: password
            - name: PROTON_DRIVE_ROOT
              value: "/bsw-arch"
            volumeMounts:
            - name: documentation
              mountPath: /opt/documentation
          restartPolicy: OnFailure
          volumes:
          - name: documentation
            persistentVolumeClaim:
              claimName: documentation-pvc
```

### 7.3 GitHub Actions (Backup Sync)

File: `.github/workflows/proton-sync-backup.yml`

```yaml
name: Proton Drive Sync Backup

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync-to-github:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Proton Drive CLI
        run: |
          pip install proton-drive-cli

      - name: Sync from Proton Drive
        env:
          PROTON_USERNAME: ${{ secrets.PROTON_USERNAME }}
          PROTON_PASSWORD: ${{ secrets.PROTON_PASSWORD }}
        run: |
          proton-drive-cli login
          proton-drive-cli sync --remote /bsw-arch --local ./docs

      - name: Commit changes
        run: |
          git config user.name "Proton Sync Bot"
          git config user.email "bot@bsw-arch.local"
          git add docs/
          git diff --quiet && git diff --staged --quiet || git commit -m "docs: sync from Proton Drive"
          git push
```

---

## 8. Security Considerations

### 8.1 End-to-End Encryption

Proton Drive provides end-to-end encryption, but additional measures:

```python
#!/usr/bin/env python3
"""
Additional encryption layer for sensitive bot configurations
"""

from cryptography.fernet import Fernet
from pathlib import Path
import os

class SecureConfigManager:
    def __init__(self):
        # Load or generate encryption key
        key_file = Path.home() / ".config" / "bsw-arch" / "encryption.key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(self.key)
            key_file.chmod(0o600)

        self.cipher = Fernet(self.key)

    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt sensitive file before sync to Proton Drive"""

        with open(file_path, 'rb') as f:
            plaintext = f.read()

        encrypted = self.cipher.encrypt(plaintext)

        encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted)

        return encrypted_path

    def decrypt_file(self, encrypted_path: Path) -> Path:
        """Decrypt file after sync from Proton Drive"""

        with open(encrypted_path, 'rb') as f:
            encrypted = f.read()

        plaintext = self.cipher.decrypt(encrypted)

        decrypted_path = Path(str(encrypted_path).replace('.encrypted', ''))
        with open(decrypted_path, 'wb') as f:
            f.write(plaintext)

        return decrypted_path

# Usage
config_mgr = SecureConfigManager()

# Before syncing to Proton Drive
encrypted = config_mgr.encrypt_file(Path("api-keys.yaml"))

# After syncing from Proton Drive
decrypted = config_mgr.decrypt_file(Path("api-keys.yaml.encrypted"))
```

### 8.2 Access Control

```yaml
# Kubernetes RBAC for Proton Drive sync
apiVersion: v1
kind: ServiceAccount
metadata:
  name: proton-sync-sa
  namespace: iv-bots
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: proton-sync-role
  namespace: iv-bots
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["proton-drive-credentials"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get"]
  resourceNames: ["proton-drive-config"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: proton-sync-binding
  namespace: iv-bots
subjects:
- kind: ServiceAccount
  name: proton-sync-sa
roleRef:
  kind: Role
  name: proton-sync-role
  apiGroup: rbac.authorization.k8s.io
```

### 8.3 Audit Logging

```python
#!/usr/bin/env python3
"""
Audit logging for Proton Drive syncs
"""

import logging
import json
from datetime import datetime
from pathlib import Path

class ProtonSyncAuditor:
    def __init__(self, log_path="/var/log/proton-sync-audit.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=str(self.log_path),
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def log_sync(self, event_type: str, details: dict):
        """Log sync event"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details
        }

        self.logger.info(json.dumps(audit_entry))

    def log_sync_start(self, remote_path: str, local_path: str):
        """Log sync start"""
        self.log_sync("SYNC_START", {
            "remote": remote_path,
            "local": local_path
        })

    def log_sync_complete(self, files_synced: int, bytes_synced: int):
        """Log sync completion"""
        self.log_sync("SYNC_COMPLETE", {
            "files": files_synced,
            "bytes": bytes_synced
        })

    def log_sync_error(self, error: str):
        """Log sync error"""
        self.log_sync("SYNC_ERROR", {
            "error": error
        })

    def log_file_access(self, file_path: str, accessor: str):
        """Log file access"""
        self.log_sync("FILE_ACCESS", {
            "file": file_path,
            "accessor": accessor
        })
```

---

## 9. Implementation Examples

### 9.1 Complete Setup Script

```bash
#!/bin/bash
# complete-proton-setup.sh
# Complete Proton Drive integration setup for BSW-Arch

set -e

echo "🚀 BSW-Arch Proton Drive Integration Setup"
echo "=========================================="

# Step 1: Install dependencies
echo ""
echo "📦 Step 1: Installing dependencies..."
pip install --break-system-packages \
    proton-drive-cli \
    watchdog \
    python-dotenv \
    cryptography

# Step 2: Configure Proton Drive credentials
echo ""
echo "🔐 Step 2: Configuring Proton Drive..."
mkdir -p ~/.config/proton-drive

read -p "Proton email: " PROTON_EMAIL
read -sp "Proton password: " PROTON_PASSWORD
echo ""
read -p "2FA secret (optional): " PROTON_2FA

cat > ~/.config/proton-drive/credentials.env << EOF
PROTON_USERNAME=$PROTON_EMAIL
PROTON_PASSWORD=$PROTON_PASSWORD
PROTON_2FA_SECRET=$PROTON_2FA
PROTON_DRIVE_ROOT=/bsw-arch
EOF

chmod 600 ~/.config/proton-drive/credentials.env

# Step 3: Test authentication
echo ""
echo "🔑 Step 3: Testing authentication..."
source ~/.config/proton-drive/credentials.env
proton-drive-cli login

# Step 4: Create local documentation directory
echo ""
echo "📁 Step 4: Creating local documentation cache..."
sudo mkdir -p /opt/documentation
sudo chown $USER:$USER /opt/documentation

# Step 5: Initial sync
echo ""
echo "⬇️  Step 5: Performing initial sync..."
proton-drive-cli sync \
    --remote /bsw-arch \
    --local /opt/documentation \
    --recursive

# Step 6: Set up Neo4j
echo ""
echo "🗄️  Step 6: Setting up Neo4j knowledge graph..."
docker run -d \
    --name neo4j-code-graph \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/bsw-arch-secure-password \
    -v $HOME/neo4j/data:/data \
    neo4j:latest

# Wait for Neo4j to start
echo "Waiting for Neo4j to start..."
sleep 10

# Step 7: Index documentation
echo ""
echo "📊 Step 7: Indexing documentation to knowledge graph..."
python3 /opt/documentation/bot-utils/graph_indexer.py /opt/documentation/docs

# Step 8: Install systemd service
echo ""
echo "⚙️  Step 8: Installing systemd service..."
sudo tee /etc/systemd/system/proton-drive-sync.service > /dev/null << 'EOF'
[Unit]
Description=Proton Drive Documentation Sync
After=network-online.target

[Service]
Type=simple
User=$USER
EnvironmentFile=/home/$USER/.config/proton-drive/credentials.env
ExecStart=/usr/bin/python3 /opt/proton-drive-sync.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable proton-drive-sync
sudo systemctl start proton-drive-sync

# Step 9: Verify setup
echo ""
echo "✅ Step 9: Verifying setup..."

echo "  Checking Neo4j..."
curl -s http://localhost:7474 > /dev/null && echo "  ✓ Neo4j running" || echo "  ✗ Neo4j not running"

echo "  Checking sync service..."
systemctl is-active proton-drive-sync > /dev/null && echo "  ✓ Sync service active" || echo "  ✗ Sync service not active"

echo "  Checking documentation..."
[ -d "/opt/documentation/docs" ] && echo "  ✓ Documentation synced" || echo "  ✗ Documentation not found"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Access Neo4j Browser: http://localhost:7474"
echo "2. Login with: neo4j / bsw-arch-secure-password"
echo "3. Start OpenCode: opencode"
echo "4. Try: /graph-explain"
echo ""
echo "Documentation syncs automatically every 15 minutes."
echo "Check status: systemctl status proton-drive-sync"
```

### 9.2 Testing the Integration

```python
#!/usr/bin/env python3
"""
Test Proton Drive integration end-to-end
"""

import subprocess
import sys
from pathlib import Path

def test_proton_auth():
    """Test Proton Drive authentication"""
    print("🔐 Testing Proton Drive authentication...")

    result = subprocess.run(
        ["proton-drive-cli", "list"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("  ✅ Authentication successful")
        return True
    else:
        print(f"  ❌ Authentication failed: {result.stderr}")
        return False

def test_sync():
    """Test documentation sync"""
    print("⬇️  Testing documentation sync...")

    result = subprocess.run([
        "proton-drive-cli", "sync",
        "--remote", "/bsw-arch",
        "--local", "/opt/documentation",
        "--dry-run"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("  ✅ Sync test successful")
        return True
    else:
        print(f"  ❌ Sync test failed: {result.stderr}")
        return False

def test_knowledge_graph():
    """Test knowledge graph connection"""
    print("🗄️  Testing knowledge graph connection...")

    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "bsw-arch-secure-password")
        )

        with driver.session() as session:
            result = session.run("RETURN 1")
            result.single()

        driver.close()
        print("  ✅ Knowledge graph connection successful")
        return True

    except Exception as e:
        print(f"  ❌ Knowledge graph connection failed: {e}")
        return False

def test_documentation():
    """Test documentation files exist"""
    print("📄 Testing documentation files...")

    required_files = [
        "/opt/documentation/docs/architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md",
        "/opt/documentation/docs/guides/setup/IV-BOTS-SETUP.md",
        "/opt/documentation/bot-utils/doc_scanner.py"
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} not found")
            all_exist = False

    return all_exist

def test_iv_bot_integration():
    """Test IV bot can access documentation"""
    print("🤖 Testing IV bot integration...")

    try:
        sys.path.insert(0, "/opt/documentation/bot-utils")
        from doc_scanner import DocScanner

        scanner = DocScanner("/opt/documentation")
        iv_docs = scanner.get_documents_by_domain("IV")

        print(f"  ✅ Found {len(iv_docs)} IV domain documents")
        return True

    except Exception as e:
        print(f"  ❌ IV bot integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Proton Drive Integration")
    print("="*50)
    print("")

    tests = [
        ("Proton Drive Authentication", test_proton_auth),
        ("Documentation Sync", test_sync),
        ("Knowledge Graph Connection", test_knowledge_graph),
        ("Documentation Files", test_documentation),
        ("IV Bot Integration", test_iv_bot_integration)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append((name, False))
        print("")

    # Summary
    print("="*50)
    print("📊 Test Summary")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("")
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Issue: Proton Drive CLI authentication fails

```bash
# Solution 1: Re-login
proton-drive-cli logout
proton-drive-cli login

# Solution 2: Check credentials
cat ~/.config/proton-drive/credentials.env

# Solution 3: Test with verbose logging
proton-drive-cli --verbose list
```

#### Issue: Sync is slow

```bash
# Solution 1: Use selective sync
proton-drive-cli sync \
    --remote /bsw-arch/docs \
    --local /opt/documentation/docs \
    --exclude "*.git" --exclude "node_modules"

# Solution 2: Increase sync threads
proton-drive-cli sync --threads 4

# Solution 3: Check network
ping proton.me
```

#### Issue: Knowledge graph not updating

```python
# Force re-index
python3 /opt/documentation/bot-utils/graph_indexer.py \
    /opt/documentation/docs \
    --force

# Check Neo4j connection
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n)")
    print(result.single()[0])
```

### 10.2 Debug Mode

```bash
# Enable debug logging
export PROTON_DRIVE_DEBUG=1
export OPENCODE_DEBUG=1

# Run sync with verbose output
python3 /opt/proton-drive-sync.py --debug

# Check systemd logs
sudo journalctl -u proton-drive-sync -f
```

---

## Related Documentation

- [IV Bots Setup Guide](../setup/IV-BOTS-SETUP.md) - Complete IV domain bot setup
- [CAG+RAG Solution Architecture](../../architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md) - 2-tier architecture
- [Knowledge Base Architecture](../../architecture/components/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md) - KB design
- [OpenCode Knowledge Graph Guide](./opencode-knowledge-graph-guide.txt) - Complete OpenCode setup

---

## Conclusion

This integration provides:

✅ **Secure Documentation Storage**: End-to-end encrypted with Proton Drive
✅ **FAGAM Compliance**: Proton is Switzerland-based, not FAGAM
✅ **Automated Sync**: Continuous updates to local knowledge base
✅ **Privacy-First AI**: All processing happens locally
✅ **Team Collaboration**: Shared documentation with encryption
✅ **Version Control**: Document history and rollback
✅ **Seamless Integration**: Works with IV bots, CAG+RAG, OpenCode

**Next Steps:**
1. Run complete setup script
2. Test all integrations
3. Configure team access
4. Set up monitoring and alerts

---

*Document Version: 1.0*
*Last Updated: 2025-11-11*
*Integration: Proton Drive + IV Bots + CAG+RAG + OpenCode*
*For support: https://github.com/bsw-arch/bsw-arch/issues*
