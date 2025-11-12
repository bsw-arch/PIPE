# IV BOTS - Intelligence/Validation Domain Setup Guide

## Executive Summary

This comprehensive guide provides complete setup instructions for all 44 Intelligence/Validation (IV) domain bots. IV bots handle artificial intelligence, machine learning, data analysis, validation, and knowledge management for the BSW-Arch bot factory.

**Quick Stats:**
- **Domain**: Intelligence & Validation (IV)
- **Total Bots**: 44
- **Network Zone**: 10.100.7.0/24
- **Primary Functions**: AI/ML, RAG, Knowledge Management, Validation, Analytics
- **Integration**: Part of the [2-Tier CAG+RAG Architecture](../../architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md)

---

## Table of Contents

1. [Initial Setup](#1-initial-setup)
2. [Documentation Scanning](#2-documentation-scanning)
3. [Python API Usage](#3-python-api-usage)
4. [IV Bot Categories](#4-iv-bot-categories)
5. [Recommended Workflows](#5-recommended-workflows)
6. [AI/ML Requirements](#6-aiml-requirements)
7. [RAG Implementation](#7-rag-implementation)
8. [Ollama Integration](#8-ollama-integration)
9. [Container Configuration](#9-container-configuration)
10. [Bot Collaboration](#10-bot-collaboration)
11. [Troubleshooting](#11-troubleshooting)
12. [Quick Reference](#12-quick-reference)

---

## 1. Initial Setup

### 1.1 Prerequisites

```bash
# System requirements
- Python 3.11+
- Git 2.40+
- Docker/Kubernetes access
- Network access to 10.100.7.0/24 (IV domain)

# Resource requirements (per bot)
- CPU: 100m-4000m (depending on bot type)
- Memory: 256Mi-16Gi (depending on ML model size)
- Storage: 10Gi minimum
```

### 1.2 Clone Documentation Repository

```bash
# Clone to standard location
cd /opt
git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Verify clone
ls -la /opt/documentation/
cd /opt/documentation
git status
```

### 1.3 Install Python Dependencies

```bash
# Core dependencies for all IV bots
pip install --upgrade pip
pip install pyyaml requests numpy pandas scikit-learn

# AI/ML specific dependencies
pip install sentence-transformers transformers torch

# Optional: LangChain for advanced RAG
pip install langchain langchain-community faiss-cpu

# Verify installation
python3 -c "import yaml, requests, numpy, pandas; print('✓ Core dependencies installed')"
python3 -c "import sentence_transformers; print('✓ ML dependencies installed')"
```

### 1.4 Initial Documentation Scan

```bash
# Scan IV-specific critical documents
cd /opt/documentation/bot-utils
python3 doc_scanner.py --action list --domain IV --priority critical

# Expected output:
# ✓ Found 8 critical IV documents
# 1. BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
# 2. BSW-TECH-AI-INTEGRATION-GUIDE.md
# 3. BSW-TECH-CLAUDE-INTEGRATION-GUIDE.md
# ...
```

---

## 2. Documentation Scanning

### 2.1 Critical Priority Documents (Read First)

These documents are **essential** for IV bot operation:

#### 1. Knowledge Base Architecture
```bash
# Location: docs/architecture/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md
# Topics: Hybrid META-KERAGR design, AI/ML integration, Knowledge graph, RAG patterns
```

**Key Concepts:**
- Hybrid knowledge base architecture
- Vector embeddings + Knowledge graph
- RAG (Retrieval-Augmented Generation) implementation
- Multi-domain knowledge integration

#### 2. AI Integration Guide
```bash
# Location: docs/guides/BSW-TECH-AI-INTEGRATION-GUIDE.md
# Topics: CrewAI framework, Multi-agent AI, Ollama/LLaMA integration
```

**Key Concepts:**
- 50-page comprehensive AI integration guide
- CrewAI framework implementation
- Multi-agent AI coordination patterns
- Ollama and LLaMA integration strategies

#### 3. Claude Integration Guide
```bash
# Location: docs/guides/BSW-TECH-CLAUDE-INTEGRATION-GUIDE.md
# Topics: Claude AI patterns, Multi-agent workflows, MCP tools
```

**Key Concepts:**
- Claude AI integration patterns
- Multi-agent workflows
- MCP (Model Context Protocol) tools
- Subagent orchestration

### 2.2 High Priority Documents (Read After Critical)

#### 4. Comprehensive Bot Factory Architecture
```bash
# Location: docs/architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
# Topics: AI/ML architecture, Bot intelligence, Validation frameworks
```

#### 5. GitHub Docs Consolidation Strategy
```bash
# Location: docs/processes/GITHUB-DOCS-CONSOLIDATION-STRATEGY.md
# Topics: Documentation as training data, Knowledge base updates, Learning patterns
```

### 2.3 Reference Documents (Available as Needed)

- `docs/specifications/bots/*.yaml` - Bot AI configurations
- `docs/specifications/ml-models/*.yaml` - ML model specifications
- `docs/reference/*.md` - Technical references

---

## 3. Python API Usage

### 3.1 Document Scanner API

```python
#!/usr/bin/env python3
"""
IV Bot Documentation Scanner
Access and analyze documentation programmatically
"""

import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from doc_scanner import DocScanner

def main():
    # Initialize scanner
    scanner = DocScanner("/opt/documentation")

    # Get IV-specific documents
    iv_docs = scanner.get_documents_by_domain("IV")
    print(f"Found {len(iv_docs)} IV domain documents")

    # Get guides category (AI integration guides)
    guide_docs = scanner.get_documents_by_category("guides")
    print(f"Found {len(guide_docs)} guide documents")

    # Get knowledge base related documents
    kb_docs = [d for d in scanner.scan_all_documents()
               if 'knowledge-base' in d.get('topics', [])]
    print(f"Found {len(kb_docs)} knowledge base documents")

    # Get AI/ML related documents
    ai_topics = ['ai', 'ml', 'claude', 'ollama', 'llm', 'rag']
    ai_docs = [d for d in scanner.scan_all_documents()
               if any(topic in d.get('topics', []) for topic in ai_topics)]
    print(f"Found {len(ai_docs)} AI/ML documents")

    # Read a specific document
    kb_arch = scanner.read_document("BOTS-KNOWLEDGE-BASE-ARCHITECTURE")
    if kb_arch:
        print(f"✓ Read knowledge base architecture ({len(kb_arch)} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 3.2 GitHub API Client

```python
#!/usr/bin/env python3
"""
GitHub Documentation Client for IV Bots
Monitor and fetch documentation updates
"""

import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from github_api_client import GitHubDocsClient

def main():
    # Initialize client (token from environment or config)
    client = GitHubDocsClient(token=os.getenv("GITHUB_TOKEN"))

    # Check for knowledge base updates
    metadata = client.get_metadata()
    kb_version = metadata.get('knowledge_base', {}).get('version')
    print(f"Knowledge base version: {kb_version}")

    # Fetch training documents
    docs = client.list_directory("docs/architecture")
    print(f"Found {len(docs)} architecture documents")

    # Get AI integration guide
    guide = client.get_document("docs/guides/BSW-TECH-AI-INTEGRATION-GUIDE.md")
    if guide:
        print(f"✓ Fetched AI integration guide ({len(guide)} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 3.3 Embeddings Creation

```python
#!/usr/bin/env python3
"""
Create embeddings-ready chunks for RAG
"""

import sys
sys.path.insert(0, "/opt/documentation/bot-utils")

from create_embeddings_chunks import create_embeddings

def main():
    # Create embeddings-ready chunks
    chunks = create_embeddings("/opt/documentation/docs")

    print(f"Created {len(chunks)} embeddings-ready chunks")

    # Each chunk contains:
    # - id: Unique identifier
    # - source_file: Original document
    # - heading: Section heading
    # - content: Text content (<1000 chars)
    # - token_estimate: Approximate tokens

    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"\nChunk {i+1}:")
        print(f"  ID: {chunk['id']}")
        print(f"  Source: {chunk['source_file']}")
        print(f"  Heading: {chunk['heading']}")
        print(f"  Tokens: ~{chunk['token_estimate']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 4. IV Bot Categories

### 4.1 AI & Machine Learning Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-ai-bot** | AI orchestration and coordination | LangChain, CrewAI |
| **iv-ml-bot** | Machine learning model management | scikit-learn, TensorFlow |
| **iv-llm-bot** | Large Language Model integration (Ollama, Claude) | Ollama, Claude API |
| **iv-training-bot** | Model training and fine-tuning | PyTorch, transformers |
| **iv-inference-bot** | Model inference and prediction | ONNX, TorchServe |

### 4.2 Knowledge Management Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-kb-bot** | Knowledge base management and queries | Neo4j, PostgreSQL |
| **iv-docs-bot** | Documentation analysis and generation | Markdown, AST parsers |
| **iv-learning-bot** | Continuous learning and adaptation | Incremental learning frameworks |
| **iv-memory-bot** | Context and memory management | Redis, distributed cache |
| **iv-index-bot** | Document indexing and search | Elasticsearch, FAISS |

### 4.3 Data Analysis Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-analysis-bot** | Data analysis and insights | pandas, numpy, scipy |
| **iv-metrics-bot** | Metrics collection and analysis | Prometheus client, statsmodels |
| **iv-trends-bot** | Trend analysis and prediction | Prophet, ARIMA |
| **iv-anomaly-bot** | Anomaly detection | Isolation Forest, LOF |
| **iv-correlation-bot** | Correlation analysis | pandas, seaborn |

### 4.4 Validation & Testing Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-validation-bot** | AI/ML model validation | pytest, hypothesis |
| **iv-test-bot** | Test case generation and execution | pytest, unittest |
| **iv-quality-bot** | Quality assurance for AI outputs | Custom validators |
| **iv-accuracy-bot** | Accuracy and precision measurement | scikit-learn metrics |
| **iv-bias-bot** | Bias detection and mitigation | Fairness indicators |

### 4.5 Natural Language Processing Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-nlp-bot** | Natural language processing | spaCy, NLTK |
| **iv-sentiment-bot** | Sentiment analysis | transformers (BERT) |
| **iv-summarize-bot** | Document summarization | transformers (T5, BART) |
| **iv-translate-bot** | Language translation | transformers (MarianMT) |
| **iv-entity-bot** | Entity extraction and recognition | spaCy NER |

### 4.6 RAG & Retrieval Bots (5 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-rag-bot** | Retrieval-Augmented Generation | LangChain, vector stores |
| **iv-embedding-bot** | Vector embeddings generation | sentence-transformers |
| **iv-retrieval-bot** | Document retrieval and ranking | FAISS, Qdrant |
| **iv-context-bot** | Context management and enrichment | Custom context managers |
| **iv-similarity-bot** | Similarity search and matching | cosine similarity, FAISS |

### 4.7 Recommendation & Prediction Bots (4 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-recommend-bot** | Recommendation engine | Collaborative filtering |
| **iv-predict-bot** | Prediction and forecasting | Prophet, LSTM |
| **iv-classify-bot** | Classification tasks | scikit-learn, XGBoost |
| **iv-cluster-bot** | Clustering and segmentation | K-means, DBSCAN |

### 4.8 Conversational AI Bots (4 bots)

| Bot | Purpose | Dependencies |
|-----|---------|--------------|
| **iv-chat-bot** | Conversational interfaces | Rasa, Dialogflow SDK |
| **iv-question-bot** | Question answering | QA transformers |
| **iv-dialog-bot** | Dialog management | State machines |
| **iv-intent-bot** | Intent recognition | Classification models |

### 4.9 Additional Specialized Bots (6+ more)

See [Bot Specifications](../../specifications/bots/iv-bots.yaml) for complete list.

---

## 5. Recommended Workflows

### 5.1 Workflow 1: New IV Bot Initialization

```bash
# Step 1: Clone documentation
cd /opt
git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Step 2: Scan AI/ML documents
cd /opt/documentation/bot-utils
python3 doc_scanner.py --action list --domain IV

# Step 3: Read knowledge base architecture
python3 << 'EOF'
import sys
sys.path.insert(0, "/opt/documentation/bot-utils")
from doc_scanner import DocScanner

scanner = DocScanner("/opt/documentation")

# Read critical documents
kb_arch = scanner.read_document("BOTS-KNOWLEDGE-BASE-ARCHITECTURE")
ai_guide = scanner.read_document("BSW-TECH-AI-INTEGRATION-GUIDE")

print("✓ Loaded critical documentation")
EOF

# Step 4: Load bot-specific AI configs
python3 << 'EOF'
import sys
sys.path.insert(0, "/opt/documentation/bot-utils")
from doc_scanner import DocScanner

scanner = DocScanner("/opt/documentation")

# Replace YOUR-BOT-NAME with actual bot name (e.g., iv-rag-bot)
my_docs = scanner.get_documents_for_bot("iv-YOUR-BOT-NAME")
print(f"Found {len(my_docs)} bot-specific documents")
EOF

# Step 5: Initialize AI models and begin operations
echo "✓ IV Bot initialization complete"
```

### 5.2 Workflow 2: RAG Knowledge Base Query

This workflow demonstrates the complete RAG pipeline using multiple IV bots:

```python
#!/usr/bin/env python3
"""
RAG Knowledge Base Query Workflow
Demonstrates iv-rag-bot + iv-kb-bot + iv-embedding-bot coordination
"""

import asyncio
from typing import List, Dict, Any

class RAGQueryWorkflow:
    def __init__(self):
        self.embedding_bot = IVEmbeddingBot()
        self.retrieval_bot = IVRetrievalBot()
        self.context_bot = IVContextBot()
        self.rag_bot = IVRagBot()
        self.validation_bot = IVValidationBot()

    async def process_query(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG query processing pipeline
        """

        # Step 1: User asks question
        print(f"📝 Question: {question}")

        # Step 2: iv-embedding-bot generates query embedding
        print("🔢 Generating query embedding...")
        query_embedding = await self.embedding_bot.generate_embedding(
            text=question,
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        print(f"  ✓ Embedding shape: {query_embedding.shape}")

        # Step 3: iv-retrieval-bot searches knowledge base
        print("🔍 Searching knowledge base...")
        retrieved_docs = await self.retrieval_bot.similarity_search(
            query_embedding=query_embedding,
            top_k=5,
            include_metadata=True
        )
        print(f"  ✓ Retrieved {len(retrieved_docs)} relevant documents")

        for i, doc in enumerate(retrieved_docs):
            print(f"    {i+1}. {doc['title']} (score: {doc['score']:.3f})")

        # Step 4: iv-context-bot enriches context
        print("📚 Enriching context...")
        enriched_context = await self.context_bot.enrich(
            documents=retrieved_docs,
            include_related=True,
            include_cross_refs=True
        )
        print(f"  ✓ Context enriched with {len(enriched_context['related'])} related docs")

        # Step 5: iv-rag-bot generates response
        print("🤖 Generating RAG response...")
        response = await self.rag_bot.generate_response(
            question=question,
            context=enriched_context,
            llm="ollama:mistral:7b",  # or "claude-3-5-sonnet"
            include_citations=True
        )
        print(f"  ✓ Generated response ({len(response['text'])} chars)")

        # Step 6: iv-validation-bot validates output
        print("✅ Validating response...")
        validation = await self.validation_bot.validate(
            response=response,
            check_hallucinations=True,
            verify_citations=True,
            quality_threshold=0.8
        )

        if validation['is_valid']:
            print("  ✓ Response validated successfully")
        else:
            print(f"  ⚠ Validation warnings: {validation['warnings']}")

        # Step 7: Return response with sources
        return {
            'answer': response['text'],
            'sources': response['citations'],
            'confidence': response['confidence'],
            'validation': validation
        }

# Example usage
async def main():
    workflow = RAGQueryWorkflow()

    result = await workflow.process_query(
        "How does the bot factory handle deployment?"
    )

    print("\n" + "="*70)
    print("📋 FINAL RESULT")
    print("="*70)
    print(f"Answer: {result['answer']}\n")
    print(f"Sources ({len(result['sources'])}):")
    for source in result['sources']:
        print(f"  - {source}")
    print(f"\nConfidence: {result['confidence']:.2%}")
    print(f"Validated: {'✓' if result['validation']['is_valid'] else '✗'}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Expected Output:**
```
📝 Question: How does the bot factory handle deployment?
🔢 Generating query embedding...
  ✓ Embedding shape: (384,)
🔍 Searching knowledge base...
  ✓ Retrieved 5 relevant documents
    1. COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md (score: 0.892)
    2. APKO-DOMAIN-CONTAINERS-STRATEGY.md (score: 0.856)
    3. BSW-GOV-NAMESPACE-ARCHITECTURE-DEPLOYMENT.md (score: 0.834)
    4. CLAUDE-20250901-0011-BSW-MULTI-APPVM-GITOPS.md (score: 0.812)
    5. IAC-ALIGNMENT-REPORT.md (score: 0.789)
📚 Enriching context...
  ✓ Context enriched with 3 related docs
🤖 Generating RAG response...
  ✓ Generated response (542 chars)
✅ Validating response...
  ✓ Response validated successfully

======================================================================
📋 FINAL RESULT
======================================================================
Answer: The bot factory handles deployment through a GitOps-based approach
using ArgoCD. Each bot is containerized using apko with Wolfi base images
(<50MB). Deployments are managed via Kubernetes manifests stored in Git,
with automated rollouts triggered by commits. The architecture supports
multi-cluster deployments across different domains (PIPE, IV, AXIS, etc.).

Sources (5):
  - COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md
  - APKO-DOMAIN-CONTAINERS-STRATEGY.md
  - BSW-GOV-NAMESPACE-ARCHITECTURE-DEPLOYMENT.md
  - CLAUDE-20250901-0011-BSW-MULTI-APPVM-GITOPS.md
  - IAC-ALIGNMENT-REPORT.md

Confidence: 94.2%
Validated: ✓
```

### 5.3 Workflow 3: Continuous Learning

```python
#!/usr/bin/env python3
"""
Continuous Learning Workflow
Automatically updates knowledge base when documentation changes
"""

import asyncio
import hashlib
from datetime import datetime

class ContinuousLearningWorkflow:
    def __init__(self):
        self.docs_bot = IVDocsBot()
        self.learning_bot = IVLearningBot()
        self.embedding_bot = IVEmbeddingBot()
        self.index_bot = IVIndexBot()
        self.validation_bot = IVValidationBot()
        self.metrics_bot = IVMetricsBot()

    async def monitor_and_update(self, interval_minutes: int = 15):
        """
        Continuously monitor documentation for updates
        """

        last_version = None

        while True:
            try:
                # Step 1: iv-docs-bot monitors documentation
                print(f"[{datetime.now()}] 📡 Checking for documentation updates...")

                current_metadata = await self.docs_bot.get_metadata()
                current_version = current_metadata.get('version')

                if current_version != last_version:
                    print(f"  🆕 New version detected: {current_version}")

                    # Detect changes
                    changes = await self.docs_bot.detect_changes(
                        old_version=last_version,
                        new_version=current_version
                    )

                    print(f"  📄 Changes: {len(changes['new'])} new, "
                          f"{len(changes['modified'])} modified, "
                          f"{len(changes['deleted'])} deleted")

                    # Step 2: iv-learning-bot processes updates
                    print("  🧠 Processing updates...")
                    for doc in changes['new'] + changes['modified']:
                        content = await self.docs_bot.read_document(doc)

                        # Extract key concepts
                        concepts = await self.learning_bot.extract_concepts(content)

                        # Update knowledge graph
                        await self.learning_bot.update_knowledge_graph(
                            document=doc,
                            concepts=concepts
                        )

                    print(f"    ✓ Processed {len(changes['new']) + len(changes['modified'])} documents")

                    # Step 3: iv-embedding-bot re-generates embeddings
                    print("  🔢 Regenerating embeddings...")
                    for doc in changes['new'] + changes['modified']:
                        content = await self.docs_bot.read_document(doc)
                        chunks = await self.embedding_bot.create_chunks(content)
                        embeddings = await self.embedding_bot.generate_embeddings(chunks)

                        # Update vector database
                        await self.embedding_bot.upsert_embeddings(
                            doc_id=doc,
                            embeddings=embeddings
                        )

                    print(f"    ✓ Updated embeddings for {len(changes['new']) + len(changes['modified'])} documents")

                    # Step 4: iv-index-bot updates indexes
                    print("  🗂️  Updating indexes...")
                    await self.index_bot.rebuild_indexes(
                        documents=changes['new'] + changes['modified']
                    )
                    print("    ✓ Indexes updated")

                    # Step 5: iv-validation-bot validates knowledge
                    print("  ✅ Validating knowledge...")
                    validation = await self.validation_bot.test_queries(
                        sample_size=10
                    )
                    print(f"    ✓ Query accuracy: {validation['accuracy']:.1%}")

                    # Step 6: iv-metrics-bot tracks improvements
                    print("  📊 Tracking metrics...")
                    await self.metrics_bot.record_update(
                        version=current_version,
                        changes=len(changes['new']) + len(changes['modified']),
                        accuracy=validation['accuracy'],
                        timestamp=datetime.now()
                    )

                    last_version = current_version
                    print(f"  ✅ Knowledge base updated to version {current_version}\n")

                else:
                    print(f"  ℹ️  No changes detected (version: {current_version})\n")

            except Exception as e:
                print(f"  ❌ Error during update: {e}\n")

            # Wait before next check
            await asyncio.sleep(interval_minutes * 60)

# Example usage
async def main():
    workflow = ContinuousLearningWorkflow()
    await workflow.monitor_and_update(interval_minutes=15)

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.4 Workflow 4: Multi-Agent AI Analysis

```python
#!/usr/bin/env python3
"""
Multi-Agent AI Analysis Workflow
Complex analysis using multiple specialized IV bots
"""

import asyncio
from typing import Dict, List, Any

class MultiAgentAnalysisWorkflow:
    def __init__(self):
        self.ai_bot = IVAiBot()  # Orchestrator
        self.analysis_bot = IVAnalysisBot()
        self.metrics_bot = IVMetricsBot()
        self.trends_bot = IVTrendsBot()
        self.anomaly_bot = IVAnomalyBot()
        self.correlation_bot = IVCorrelationBot()
        self.predict_bot = IVPredictBot()
        self.recommend_bot = IVRecommendBot()
        self.docs_bot = IVDocsBot()
        self.validation_bot = IVValidationBot()

    async def analyze_architecture(self, request: str) -> Dict[str, Any]:
        """
        Perform comprehensive architecture analysis
        Example: "Analyze the bot factory architecture and recommend optimizations"
        """

        print(f"🎯 Analysis Request: {request}\n")

        # Step 1: iv-ai-bot orchestrates analysis
        print("🎭 Orchestrating multi-agent analysis...")
        subtasks = await self.ai_bot.decompose_task(request)
        print(f"  ✓ Decomposed into {len(subtasks)} subtasks")

        # Step 2: Parallel analysis by specialized bots
        print("\n📊 Running parallel analysis...")

        analysis_tasks = [
            self.analysis_bot.analyze_architecture(),
            self.metrics_bot.collect_performance_metrics(),
            self.trends_bot.identify_trends(),
            self.anomaly_bot.detect_issues()
        ]

        results = await asyncio.gather(*analysis_tasks)

        architecture_analysis = results[0]
        performance_metrics = results[1]
        trends = results[2]
        anomalies = results[3]

        print(f"  ✓ Architecture analysis: {len(architecture_analysis['components'])} components")
        print(f"  ✓ Performance metrics: {len(performance_metrics)} data points")
        print(f"  ✓ Trends identified: {len(trends)}")
        print(f"  ✓ Anomalies detected: {len(anomalies)}")

        # Step 3: iv-correlation-bot finds relationships
        print("\n🔗 Finding correlations...")
        correlations = await self.correlation_bot.analyze(
            architecture=architecture_analysis,
            metrics=performance_metrics,
            trends=trends,
            anomalies=anomalies
        )
        print(f"  ✓ Found {len(correlations['significant'])} significant correlations")

        # Step 4: iv-predict-bot forecasts impact
        print("\n🔮 Forecasting impact...")
        predictions = await self.predict_bot.forecast(
            historical_data=performance_metrics,
            correlations=correlations,
            forecast_horizon_days=30
        )
        print(f"  ✓ Generated {len(predictions)} predictions")

        # Step 5: iv-recommend-bot generates recommendations
        print("\n💡 Generating recommendations...")
        recommendations = await self.recommend_bot.recommend(
            analysis=architecture_analysis,
            anomalies=anomalies,
            predictions=predictions,
            correlations=correlations
        )
        print(f"  ✓ Generated {len(recommendations)} recommendations")

        # Step 6: iv-docs-bot generates report
        print("\n📝 Generating report...")
        report = await self.docs_bot.generate_report(
            request=request,
            architecture=architecture_analysis,
            metrics=performance_metrics,
            trends=trends,
            anomalies=anomalies,
            correlations=correlations,
            predictions=predictions,
            recommendations=recommendations
        )
        print(f"  ✓ Report generated ({len(report)} words)")

        # Step 7: iv-validation-bot reviews
        print("\n✅ Validating recommendations...")
        validation = await self.validation_bot.validate_recommendations(
            recommendations=recommendations,
            feasibility_check=True,
            alignment_check=True
        )
        print(f"  ✓ Validation complete (score: {validation['score']:.1%})")

        return {
            'report': report,
            'recommendations': recommendations,
            'validation': validation,
            'metrics': {
                'components_analyzed': len(architecture_analysis['components']),
                'anomalies_detected': len(anomalies),
                'recommendations_generated': len(recommendations),
                'validation_score': validation['score']
            }
        }

# Example usage
async def main():
    workflow = MultiAgentAnalysisWorkflow()

    result = await workflow.analyze_architecture(
        "Analyze the bot factory architecture and recommend optimizations"
    )

    print("\n" + "="*70)
    print("📋 ANALYSIS RESULTS")
    print("="*70)
    print(f"Components Analyzed: {result['metrics']['components_analyzed']}")
    print(f"Anomalies Detected: {result['metrics']['anomalies_detected']}")
    print(f"Recommendations: {result['metrics']['recommendations_generated']}")
    print(f"Validation Score: {result['metrics']['validation_score']:.1%}")
    print("\nTop 3 Recommendations:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"  {i}. {rec['title']}")
        print(f"     Priority: {rec['priority']} | Impact: {rec['impact']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.5 Workflow 5: Model Training & Deployment

```bash
#!/bin/bash
# Model Training and Deployment Workflow
# Orchestrates iv-training-bot, iv-validation-bot, iv-metrics-bot

echo "🚀 Model Training & Deployment Workflow"
echo "========================================"

# Step 1: Training data preparation
echo ""
echo "📦 Step 1: Preparing training data..."
python3 << 'EOF'
from iv_bots import IVDocsBot, IVNlpBot, IVQualityBot

docs_bot = IVDocsBot()
nlp_bot = IVNlpBot()
quality_bot = IVQualityBot()

# Extract training data from documentation
training_data = docs_bot.extract_training_data(
    domains=["IV", "AXIS", "PIPE"],
    include_code=True,
    include_specs=True
)

# Preprocess text
preprocessed = nlp_bot.preprocess(training_data)

# Validate data quality
quality_report = quality_bot.validate_data(preprocessed)

print(f"✓ Training data prepared: {len(training_data)} samples")
print(f"✓ Quality score: {quality_report['score']:.1%}")
EOF

# Step 2: Model training
echo ""
echo "🧠 Step 2: Training model..."
python3 << 'EOF'
from iv_bots import IVTrainingBot

training_bot = IVTrainingBot()

# Load base model (fine-tune Mistral 7B)
model = training_bot.load_base_model("mistral:7b")

# Train on BSW-Arch specific data
training_result = training_bot.train(
    model=model,
    training_data="./training_data.json",
    validation_split=0.2,
    epochs=3,
    batch_size=4,
    learning_rate=2e-5
)

print(f"✓ Training complete")
print(f"  Final loss: {training_result['final_loss']:.4f}")
print(f"  Training time: {training_result['duration_mins']:.1f} minutes")
EOF

# Step 3: Model evaluation
echo ""
echo "📊 Step 3: Evaluating model..."
python3 << 'EOF'
from iv_bots import IVAccuracyBot, IVBiasBot, IVValidationBot

accuracy_bot = IVAccuracyBot()
bias_bot = IVBiasBot()
validation_bot = IVValidationBot()

# Measure accuracy
accuracy = accuracy_bot.measure(
    model_path="./trained_model",
    test_set="./test_data.json"
)

# Check for biases
bias_report = bias_bot.check_bias(
    model_path="./trained_model",
    test_cases="./bias_test_cases.json"
)

# Validate outputs
validation = validation_bot.validate_outputs(
    model_path="./trained_model",
    sample_size=100
)

print(f"✓ Evaluation complete")
print(f"  Accuracy: {accuracy['accuracy']:.1%}")
print(f"  Bias score: {bias_report['score']:.2f} (lower is better)")
print(f"  Output quality: {validation['quality_score']:.1%}")
EOF

# Step 4: Model deployment
echo ""
echo "🚢 Step 4: Deploying model..."

# Package model in container
docker build -t iv-bot-model:latest -f Dockerfile.model .

# Deploy to Kubernetes
kubectl apply -f k8s/iv-bot-model-deployment.yaml

# Verify deployment
kubectl rollout status deployment/iv-bot-model -n iv-bots

echo "✓ Model deployed successfully"

# Step 5: Monitoring setup
echo ""
echo "👀 Step 5: Setting up monitoring..."
python3 << 'EOF'
from iv_bots import IVMetricsBot, IVQualityBot

metrics_bot = IVMetricsBot()
quality_bot = IVQualityBot()

# Configure metrics collection
metrics_bot.configure_monitoring(
    model_name="iv-bot-model",
    track_latency=True,
    track_throughput=True,
    track_error_rate=True,
    alert_threshold=0.95
)

# Configure quality monitoring
quality_bot.configure_monitoring(
    model_name="iv-bot-model",
    sample_rate=0.1,  # Check 10% of requests
    quality_threshold=0.8
)

print("✓ Monitoring configured")
EOF

# Step 6: Continuous improvement
echo ""
echo "🔄 Step 6: Enabling continuous improvement..."
python3 << 'EOF'
from iv_bots import IVLearningBot, IVTrainingBot, IVValidationBot

learning_bot = IVLearningBot()
training_bot = IVTrainingBot()
validation_bot = IVValidationBot()

# Enable feedback collection
learning_bot.enable_feedback_collection(
    model_name="iv-bot-model",
    collection_rate=1.0
)

# Schedule periodic retraining
training_bot.schedule_retraining(
    model_name="iv-bot-model",
    frequency="weekly",
    min_new_samples=1000
)

# Enable validation checks
validation_bot.enable_continuous_validation(
    model_name="iv-bot-model",
    check_interval_minutes=60
)

print("✓ Continuous improvement enabled")
EOF

echo ""
echo "✅ Model Training & Deployment Complete!"
echo "========================================"
```

---

## 6. AI/ML Requirements

### 6.1 LLM Integration Options

#### Option 1: Ollama (Self-Hosted) - **RECOMMENDED**

```yaml
Ollama_Configuration:
  advantages:
    - Full control over deployment
    - No external API dependencies
    - FAGAM compliant
    - Cost-effective for high volume

  disadvantages:
    - Requires GPU for optimal performance
    - Higher resource usage
    - Self-managed updates

  recommended_models:
    - mistral:7b: "General purpose, good balance"
    - llama3.1:8b: "Strong reasoning capabilities"
    - codellama:7b: "Code generation and analysis"

  container_setup:
    base_image: "cgr.dev/chainguard/wolfi-base:latest"
    size_estimate: "4-8GB (with model weights)"
    requires_approval: true  # Exceeds 50MB limit
```

**Setup Instructions:**
```dockerfile
# Dockerfile for IV bot with Ollama
FROM cgr.dev/chainguard/wolfi-base:latest

# Install dependencies
RUN apk add --no-cache curl python-3.11 py3-pip

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml requests langchain

# Pull Mistral 7B model
RUN ollama pull mistral:7b

# Copy bot code
COPY . /app
WORKDIR /app

CMD ["python3", "main.py"]
```

#### Option 2: Claude API (Anthropic)

```yaml
Claude_Configuration:
  advantages:
    - High quality responses
    - No infrastructure management
    - Regular model updates
    - MCP (Model Context Protocol) support

  disadvantages:
    - External dependency
    - API costs (pay per token)
    - Rate limits
    - Requires internet connectivity

  recommended_models:
    - claude-3-5-sonnet: "Best for complex reasoning"
    - claude-3-haiku: "Fast, cost-effective"

  authentication:
    method: "API key"
    storage: "Kubernetes secrets"
```

**Setup Instructions:**
```python
# Using Claude API in IV bots
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "How does the bot factory handle deployment?"
        }
    ],
    # Use RAG context
    system="You are an expert on the BSW-Arch bot factory. "
           "Answer based on the provided documentation context."
)

print(response.content[0].text)
```

#### Option 3: Hybrid Approach (Recommended for Production)

```yaml
Hybrid_Strategy:
  use_claude_for:
    - Complex reasoning and planning
    - Multi-step problem solving
    - Code generation and review
    - When accuracy is critical

  use_ollama_for:
    - High-volume, simple tasks
    - Document summarization
    - Entity extraction
    - When cost is a concern

  use_local_embeddings_for:
    - All RAG operations
    - Similarity search
    - Document clustering
```

**Implementation:**
```python
class HybridLLMStrategy:
    def __init__(self):
        self.ollama = OllamaClient()
        self.claude = AnthropicClient()
        self.embeddings = LocalEmbeddingsModel()

    async def select_llm(self, task_type: str, complexity: str):
        """Intelligently select LLM based on task requirements"""

        if task_type == "embeddings":
            return self.embeddings
        elif complexity == "high" or task_type in ["reasoning", "planning"]:
            return self.claude
        else:
            return self.ollama
```

### 6.2 Knowledge Base Architecture

See [CAG+RAG Solution Architecture](../../architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md) for complete details.

```yaml
Knowledge_Base_Layers:
  Layer_1_Git_Repository:
    description: "Raw documentation in Markdown"
    technology: "Git, GitHub"
    properties:
      - Version controlled
      - Single source of truth
      - Collaborative editing

  Layer_2_KERAGR_Intelligence:
    description: "Vector embeddings + Knowledge graph"
    technologies:
      vector_store: "FAISS, Qdrant, or ChromaDB"
      graph_store: "Neo4j"
      embeddings: "sentence-transformers"
    properties:
      - Semantic search
      - Relationship traversal
      - Contextual understanding

  Layer_3_API_Service:
    description: "Query interfaces"
    technologies:
      rest_api: "FastAPI"
      graphql: "Strawberry GraphQL"
      websocket: "Socket.IO"
    properties:
      - RESTful queries
      - Complex GraphQL queries
      - Real-time updates

  Layer_4_Bot_Integration:
    description: "Bot access layer"
    technologies:
      sdk: "Python SDK"
      direct_access: "For trusted bots"
      cache: "Redis"
    properties:
      - High performance
      - Caching layer
      - Access control
```

### 6.3 Embeddings Strategy

```yaml
Embeddings_Configuration:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  properties:
    dimensions: 384
    inference_speed: "Fast (~1ms per sentence)"
    quality: "Good for documentation"

  chunking_strategy:
    method: "Semantic chunking by heading"
    max_chunk_size: 1000  # characters
    overlap: 100  # characters
    preserve_structure: true

  vector_database_options:
    option_1:
      name: "Qdrant"
      pros: ["Open source", "FAGAM compliant", "Feature-rich"]
      cons: ["Additional service to manage"]

    option_2:
      name: "pgvector"
      pros: ["PostgreSQL extension", "Familiar SQL", "Integrated"]
      cons: ["Less specialized", "Lower performance"]

    option_3:
      name: "ChromaDB"
      pros: ["Embedded", "Easy to use", "Python-native"]
      cons: ["Less scalable", "Fewer features"]
```

### 6.4 FAGAM Compliance

**PROHIBITED** (FAGAM companies - Do NOT use):
- ❌ OpenAI API (ChatGPT, GPT-4)
- ❌ Google Gemini / Vertex AI
- ❌ Amazon Bedrock
- ❌ Microsoft Azure OpenAI
- ❌ Facebook/Meta hosted services

**ALLOWED**:
- ✅ Anthropic Claude (not FAGAM)
- ✅ Ollama (open source, self-hosted)
- ✅ HuggingFace models (open source)
- ✅ LLaMA (Meta, but open weights)
- ✅ Mistral (open source)
- ✅ Local embeddings models

### 6.5 Container Requirements for AI Bots

```yaml
Container_Requirements:
  without_ml_model:
    base: "Wolfi + Python"
    size: "25-50MB"
    resources:
      cpu: "100m-250m"
      memory: "256Mi-512Mi"
    compliant: true

  with_small_ml_model:
    base: "Wolfi + Python + model weights"
    size: "100-200MB"
    resources:
      cpu: "500m-1000m"
      memory: "1Gi-2Gi"
    compliant: false  # Exceeds 50MB, needs approval
    approval_required: true

  with_large_ml_model:
    base: "Wolfi + Python + Ollama + model"
    size: "4-8GB"
    resources:
      cpu: "2000m-4000m"
      memory: "8Gi-16Gi"
      gpu: "Optional but recommended"
    compliant: false  # Separate deployment strategy
    deployment: "Dedicated nodes with GPU"
```

---

## 7. RAG Implementation

### 7.1 RAG System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Query                                                 │
│      │                                                       │
│      ▼                                                       │
│  Query Embedding (iv-embedding-bot)                         │
│      │                                                       │
│      ▼                                                       │
│  Vector Search (iv-retrieval-bot)                           │
│      │                                                       │
│      ▼                                                       │
│  Context Builder (iv-context-bot)                           │
│      │                                                       │
│      ▼                                                       │
│  LLM Generation (iv-rag-bot)                                │
│      │                                                       │
│      ▼                                                       │
│  Validation (iv-validation-bot)                             │
│      │                                                       │
│      ▼                                                       │
│  Response                                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Complete RAG Implementation

See the complete implementation in [Workflow 5.2](#52-workflow-2-rag-knowledge-base-query) above.

Key components:
1. **Query Embedding**: Convert user question to vector
2. **Similarity Search**: Find relevant documents
3. **Context Building**: Enrich with related content
4. **Response Generation**: LLM creates answer with context
5. **Validation**: Check for hallucinations and accuracy

---

## 8. Ollama Integration

### 8.1 Ollama Container Setup

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install Ollama and dependencies
RUN apk add --no-cache \
    curl \
    python-3.11 \
    py3-pip

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml requests

# Pull Mistral 7B model
RUN ollama pull mistral:7b

# Copy bot code
COPY . /app
WORKDIR /app

# Run bot with Ollama
CMD ["python3", "main.py"]
```

### 8.2 Using Ollama in Python

```python
#!/usr/bin/env python3
"""
Ollama Integration for IV Bots
"""

import requests
import json
from typing import Optional, Dict, Any

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def query(self, prompt: str, context: str = "",
              model: str = "mistral:7b") -> str:
        """
        Query Ollama LLM with optional context
        """

        # Build full prompt with context
        full_prompt = f"""Context:
{context}

Question: {prompt}

Answer based only on the provided context:"""

        # Call Ollama API
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
        )

        response.raise_for_status()
        return response.json()['response']

    def embed(self, text: str, model: str = "mistral:7b") -> list:
        """
        Generate embeddings using Ollama
        """

        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": model,
                "prompt": text
            }
        )

        response.raise_for_status()
        return response.json()['embedding']

# Example usage
if __name__ == "__main__":
    client = OllamaClient()

    context = """
    The BSW-Arch bot factory consists of 185 bots across 4 domains:
    AXIS (45), PIPE (48), ECO (48), and IV (44).
    All containers must be <50MB using apko + Wolfi base images.
    """

    answer = client.query(
        prompt="How many bots are in the factory?",
        context=context
    )

    print(f"Answer: {answer}")
```

---

## 9. Container Configuration

### 9.1 Dockerfile for IV Bots

```dockerfile
FROM cgr.dev/chainguard/wolfi-base:latest

# Install AI/ML dependencies
RUN apk add --no-cache \
    git \
    python-3.11 \
    py3-pip \
    py3-numpy \
    py3-scipy

# Clone documentation
WORKDIR /opt
RUN git clone https://github.com/bsw-arch/bsw-arch.git documentation

# Install Python dependencies
RUN pip install --no-cache-dir \
    pyyaml \
    requests \
    sentence-transformers \
    transformers \
    torch --index-url https://download.pytorch.org/whl/cpu

# Add bot-utils to Python path
ENV PYTHONPATH="/opt/documentation/bot-utils:$PYTHONPATH"
ENV DOCS_PATH="/opt/documentation/docs"

# Copy IV bot code
COPY . /app
WORKDIR /app

# Create data directory for embeddings
RUN mkdir -p /app/data

# Install bot dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf ~/.cache/pip

# Non-root user
RUN addgroup -g 65532 nonroot && \
    adduser -u 65532 -G nonroot -s /bin/sh -D nonroot && \
    chown -R nonroot:nonroot /app

USER nonroot

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)"

# Run bot
CMD ["python3", "main.py"]
```

### 9.2 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iv-rag-bot
  namespace: iv-bots
  labels:
    app: iv-rag-bot
    domain: iv
    category: rag
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
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DOCS_PATH
          value: "/opt/documentation/docs"
        - name: PYTHONPATH
          value: "/opt/documentation/bot-utils"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## 10. Bot Collaboration

### 10.1 Knowledge Query Pipeline

```
User asks question
  ↓
iv-nlp-bot (parse and understand)
  ↓
iv-embedding-bot (create query vector)
  ↓
iv-retrieval-bot (search knowledge base)
  ↓
iv-context-bot (build context)
  ↓
iv-rag-bot (generate answer with LLM)
  ↓
iv-validation-bot (validate response)
  ↓
Return answer to user
```

### 10.2 Continuous Learning Loop

```
Documentation updated (Git)
  ↓
iv-docs-bot (detect changes)
  ↓
iv-learning-bot (process updates)
  ↓
iv-embedding-bot (create embeddings)
  ↓
iv-index-bot (update indexes)
  ↓
iv-validation-bot (test knowledge)
  ↓
Knowledge base updated
```

### 10.3 Multi-Domain Intelligence

```
Complex analysis request
  ↓
iv-ai-bot (orchestrate)
  ├→ iv-analysis-bot (analyze architecture)
  ├→ iv-metrics-bot (analyze metrics)
  ├→ iv-trends-bot (identify trends)
  └→ iv-anomaly-bot (detect issues)
  ↓
iv-correlation-bot (find relationships)
  ↓
iv-predict-bot (forecast impact)
  ↓
iv-recommend-bot (generate recommendations)
  ↓
iv-docs-bot (create report)
```

### 10.4 Cross-Domain AI Support

```yaml
Cross_Domain_Collaboration:
  AXIS_Needs:
    - Architecture validation
    - IV bots: iv-validation-bot, iv-recommend-bot

  PIPE_Needs:
    - Test generation
    - IV bots: iv-test-bot, iv-quality-bot

  ECO_Needs:
    - Resource prediction
    - IV bots: iv-predict-bot, iv-recommend-bot
```

---

## 11. Troubleshooting

### 11.1 Common Issues and Solutions

#### Issue: Embeddings Generation Slow

**Solutions:**
```bash
# Option 1: Use GPU if available
docker run --gpus all iv-embedding-bot:latest

# Option 2: Use smaller/faster model
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fastest
EOF

# Option 3: Batch processing
python3 << 'EOF'
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
EOF
```

#### Issue: RAG Responses Inaccurate

**Solutions:**
```python
# Increase retrieved chunks
chunks = retrieval_bot.retrieve(query, top_k=10)  # Increase from 5

# Improve chunking strategy
chunks = create_chunks(
    documents=docs,
    max_size=500,  # Smaller chunks
    overlap=200     # More overlap
)

# Fine-tune embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
model.fit(domain_specific_data)
```

#### Issue: Ollama Out of Memory

**Solutions:**
```bash
# Use quantized model
ollama pull mistral:7b-q4

# Increase memory limits (Kubernetes)
resources:
  limits:
    memory: "8Gi"

# Use CPU mode (slower but works)
export OLLAMA_NUM_GPU=0
```

#### Issue: Knowledge Base Outdated

**Solutions:**
```bash
# Check documentation version
curl https://raw.githubusercontent.com/bsw-arch/bsw-arch/main/docs/metadata.json

# Manually re-index
python3 << 'EOF'
from iv_bots import IVLearningBot
bot = IVLearningBot()
bot.reindex_all()
EOF

# Set up auto-update CronJob
kubectl apply -f k8s/cronjob-kb-update.yaml
```

---

## 12. Quick Reference

### 12.1 Important URLs

- **Documentation Repository**: https://github.com/bsw-arch/bsw-arch
- **Ollama**: https://ollama.com
- **Anthropic Claude**: https://www.anthropic.com
- **Sentence Transformers**: https://www.sbert.net
- **HuggingFace**: https://huggingface.co
- **Qdrant Vector DB**: https://qdrant.tech
- **CrewAI**: https://www.crewai.com

### 12.2 Codeberg Organizations

- IV Bots: https://codeberg.org/IV-Bots
- AXIS Bots: https://codeberg.org/AXIS-Bots
- PIPE Bots: https://codeberg.org/PIPE-Bots
- ECO Bots: https://codeberg.org/ECO-Bots

### 12.3 Deployment Checklist

**Pre-Deployment:**
- [ ] Documentation repository cloned to /opt/documentation
- [ ] Python AI/ML dependencies installed
- [ ] Bot-utils in PYTHONPATH
- [ ] AI/ML documents scanned
- [ ] Knowledge base architecture understood

**AI/ML Setup:**
- [ ] LLM chosen (Ollama, Claude, or both)
- [ ] Embedding model selected and tested
- [ ] Vector database configured
- [ ] Knowledge base indexed
- [ ] RAG pipeline tested

**Configuration:**
- [ ] Container size validated (<50MB for non-ML)
- [ ] Resource limits set appropriately
- [ ] FAGAM compliance verified
- [ ] Using only approved AI services

**Data & Training:**
- [ ] Training data prepared
- [ ] Model fine-tuned if needed
- [ ] Validation set created
- [ ] Bias checked and mitigated
- [ ] Quality thresholds defined

**Integration:**
- [ ] DocScanner API tested
- [ ] Embeddings generation working
- [ ] Retrieval accuracy validated
- [ ] LLM integration functional
- [ ] Cross-bot communication tested

**Monitoring:**
- [ ] Inference metrics tracked
- [ ] Quality metrics collected
- [ ] User feedback enabled
- [ ] Error logging configured
- [ ] Alerting set up

**Production:**
- [ ] Health checks passing
- [ ] Scaling tested
- [ ] Fallback strategies defined
- [ ] Documentation complete
- [ ] Runbooks created

---

## Related Documentation

- [CAG+RAG Solution Architecture](../../architecture/CAG-RAG-SOLUTION-ARCHITECTURE.md) - Complete 2-tier architecture
- [Knowledge Base Architecture](../../architecture/components/BOTS-KNOWLEDGE-BASE-ARCHITECTURE.md) - Detailed KB design
- [AI Integration Guide](../development/BSW-TECH-AI-INTEGRATION-GUIDE.md) - AI/ML integration patterns
- [Comprehensive Bot Factory Architecture](../../architecture/COMPREHENSIVE-BOT-FACTORY-ARCHITECTURE-ANALYSIS.md) - Overall architecture

---

*Document Version: 1.0.0*
*Last Updated: 2025-11-10*
*Domain: IV (Intelligence/Validation)*
*Total Bots: 44*
*For support: https://github.com/bsw-arch/bsw-arch/issues*
