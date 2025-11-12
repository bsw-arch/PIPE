#!/usr/bin/env python3
"""
IV Domain Documentation Bot
IntelliVerse - AI/ML/RAG documentation
UK English spelling throughout
"""

from domain_documentation_bot import DomainDocumentationBot
import json


class IVDocumentationBot(DomainDocumentationBot):
    """IV domain documentation bot - AI/ML Systems"""

    def __init__(self):
        iv_standards = {
            "domain": "IV",
            "full_name": "IntelliVerse - AI Memory & Knowledge Systems",
            "uk_english": True,
            "include_badges": True,
            "versioning": "semver",
            "frameworks": ["MLOps", "LLMOps", "RAG", "META-KERAGR"],
            "port_range": "6000-6299",
            "organizations": 13,
            "required_sections": [
                "AI/ML Overview",
                "Model Architecture",
                "Training Pipeline",
                "Inference API",
                "RAG System",
                "Knowledge Graph",
                "Evaluation Metrics",
                "Ethical AI Compliance"
            ],
            "terminology": {
                "ai": "artificial intelligence",
                "ml": "machine learning",
                "rag": "retrieval-augmented generation",
                "llm": "large language model",
                "embedding": "vector embedding"
            },
            "diagram_requirements": {
                "model_architecture": "Mermaid flowchart showing layers",
                "rag_pipeline": "Mermaid sequenceDiagram",
                "knowledge_graph": "Mermaid graph"
            },
            "ai_frameworks": ["CrewAI", "PydanticAI", "LangChain", "Anthropic SDK"],
            "vector_stores": ["Qdrant", "Weaviate", "Chroma"],
            "graph_databases": ["Neo4j", "ArangoDB"],
            "metadata_requirements": {
                "model_type": "LLM|Embedding|Classification|Generation",
                "training_status": "Untrained|Training|Trained|Fine-tuned|Production",
                "rag_status": "Enabled|Disabled|Hybrid",
                "safety_tier": "Restricted|Monitored|Open"
            }
        }

        super().__init__("IV", iv_standards)

    def generate_model_card(self, model_info: dict) -> str:
        """Generate Model Card following ethical AI standards"""

        model_card_prompt = f"""Generate a comprehensive Model Card for this IV AI/ML model:

Model Info:
{json.dumps(model_info, indent=2)}

Model Card Structure (following Google/Hugging Face standards):

# {{Model Name}} Model Card

## Model Details
- **Developer**: BSW-ARCH IV Domain
- **Model Type**: {{LLM|Embedding|etc}}
- **Version**: {{semver}}
- **License**: {{license}}
- **Model Architecture**: [Mermaid diagram]

## Intended Use
### Primary Uses
- Use case 1
- Use case 2

### Out-of-Scope Uses
- What this model should NOT be used for

## Factors
### Relevant Factors
- Languages supported
- Domains
- Demographic considerations

### Evaluation Factors
- Performance across different groups
- Fairness considerations

## Metrics
### Model Performance
| Metric | Value | Benchmark |
|--------|-------|-----------|
| Accuracy | ... | ... |
| F1 Score | ... | ... |
| Latency | ... | ... |

### Ethical Metrics
- Bias assessment
- Fairness indicators
- Safety scores

## Training Data
- Dataset sources
- Dataset size and composition
- Data preprocessing
- Privacy considerations

## Evaluation Data
- Test set composition
- Benchmark datasets

## Ethical Considerations
### Bias and Fairness
- Known biases
- Mitigation strategies

### Privacy
- Data handling
- PII protection

### Safety
- Potential risks
- Safety measures

## Caveats and Recommendations
- Known limitations
- Recommended use cases
- Monitoring requirements

## Technical Specifications
### Compute Infrastructure
- Hardware requirements
- Inference optimisations

### Software
- Dependencies
- API specifications

Use UK English. Follow responsible AI principles."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            messages=[{"role": "user", "content": model_card_prompt}]
        )

        return message.content[0].text

    def generate_rag_system_docs(self, rag_config: dict) -> str:
        """Generate RAG system documentation"""

        rag_prompt = f"""Generate comprehensive RAG system documentation for IV domain:

RAG Configuration:
{json.dumps(rag_config, indent=2)}

Documentation Structure:

# {{RAG System Name}}

## System Overview
- Purpose and capabilities
- Architecture pattern (naive RAG, advanced RAG, modular RAG)
- Integration points

## Architecture Diagram
[Mermaid sequence diagram showing: Query → Retrieval → Augmentation → Generation → Response]

## Components

### 1. Document Processing
- Document loaders
- Text splitting strategy
- Chunk size and overlap
- Metadata extraction

### 2. Embedding Generation
- Embedding model
- Vector dimensions
- Normalisation strategy

### 3. Vector Store
- Database type (Qdrant/Weaviate)
- Index configuration
- Similarity metric (cosine/euclidean)
- Collection schema

### 4. Retrieval Strategy
- Retrieval algorithm (semantic/hybrid/dense)
- Top-k configuration
- Reranking approach
- Context window management

### 5. Augmentation
- Prompt template
- Context injection strategy
- Metadata utilisation

### 6. Generation
- LLM model
- Temperature and parameters
- Response formatting
- Streaming support

## API Endpoints

### Query Endpoint
```python
POST /rag/query
{
  "query": "...",
  "top_k": 5,
  "filters": {...}
}
```

### Document Ingestion
```python
POST /rag/ingest
{
  "documents": [...],
  "metadata": {...}
}
```

## Performance Optimisations
- Caching strategy
- Batch processing
- Async operations
- Resource management

## Evaluation Metrics
- Retrieval precision/recall
- Answer relevance
- Faithfulness score
- Context utilisation

## Monitoring
- Query latency
- Retrieval quality
- Token usage
- Error rates

## Knowledge Graph Integration
[Mermaid graph showing entity relationships]

Use UK English. Include code examples."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            messages=[{"role": "user", "content": rag_prompt}]
        )

        return message.content[0].text

    def generate_mlops_pipeline_docs(self, pipeline_config: dict) -> str:
        """Generate MLOps pipeline documentation"""

        mlops_prompt = f"""Generate MLOps pipeline documentation for IV domain:

Pipeline Configuration:
{json.dumps(pipeline_config, indent=2)}

MLOps Pipeline Documentation:

# {{Pipeline Name}} MLOps Pipeline

## Pipeline Overview
- ML lifecycle stage (training/inference/monitoring)
- Automation level
- Orchestration tool

## Pipeline Stages

### 1. Data Preparation
- Data sources
- Data validation
- Feature engineering
- Data versioning (DVC)

### 2. Model Training
- Training framework
- Hyperparameter tuning
- Experiment tracking
- Model versioning

### 3. Model Evaluation
- Evaluation metrics
- Validation strategy
- A/B testing setup
- Performance benchmarks

### 4. Model Registry
- Model artefact storage
- Metadata tracking
- Version control
- Model lineage

### 5. Model Deployment
- Deployment target
- Serving infrastructure
- Scaling strategy
- Rollback mechanism

### 6. Model Monitoring
- Performance drift detection
- Data drift detection
- Model explainability
- Alerting rules

## Pipeline Diagram
[Mermaid flowchart showing complete MLOps workflow]

## Continuous Training
- Retraining triggers
- Automated retraining
- Model comparison
- Promotion criteria

## Responsible AI Integration
- Bias detection
- Fairness monitoring
- Privacy compliance
- Safety checks

## Infrastructure
- Compute resources
- Storage requirements
- Network configuration
- Cost optimisation

Use UK English. Be specific about tools and metrics."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=14000,
            messages=[{"role": "user", "content": mlops_prompt}]
        )

        return message.content[0].text


if __name__ == "__main__":
    bot = IVDocumentationBot()

    # Test Model Card generation
    model_info = {
        "name": "BSW-KERAGR-Embedding-v1",
        "type": "Embedding Model",
        "architecture": "Sentence-BERT",
        "vector_dimensions": 768,
        "training_data": "BSW architecture documents, 10K documents",
        "use_cases": ["Document similarity", "RAG retrieval", "Semantic search"]
    }

    model_card = bot.generate_model_card(model_info)
    print("=== IV Model Card ===")
    print(model_card[:1500] + "..." if len(model_card) > 1500 else model_card)

    # Test RAG system docs
    rag_config = {
        "name": "BSW-AXIS-RAG",
        "embedding_model": "text-embedding-3-large",
        "vector_store": "Qdrant",
        "llm": "claude-3-5-sonnet-20241022",
        "chunk_size": 512,
        "top_k": 5
    }

    rag_docs = bot.generate_rag_system_docs(rag_config)
    print("\n=== IV RAG System Documentation ===")
    print(rag_docs[:1500] + "..." if len(rag_docs) > 1500 else rag_docs)
