#!/usr/bin/env python3
"""
Shared Configuration Management
Centralised configuration for all services
"""

import os
from typing import List, Optional, Any, Dict
from pathlib import Path
import yaml
import logging
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

logger = logging.getLogger(__name__)


# ============================================================================
# Base Configuration
# ============================================================================

class BaseConfig(BaseSettings):
    """Base configuration with common settings"""

    # Service identification
    service_name: str = Field(..., description="Service name")
    environment: str = Field(default="development", description="Environment: development/staging/production")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json/text")

    # Networking
    host: str = Field(default="0.0.0.0", description="Service host")
    port: int = Field(..., description="Service port")

    # Security
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# ============================================================================
# CAG Service Configuration
# ============================================================================

class CAGServiceConfig(BaseConfig):
    """CAG Layer Service Configuration"""

    service_name: str = "cag-service"
    port: int = 8001

    # Database connections
    postgres_host: str = Field(default="postgresql", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="cag_db", description="PostgreSQL database name")
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: str = Field(default="changeme", description="PostgreSQL password")

    # Redis connection
    redis_host: str = Field(default="redis-master", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str = Field(default="changeme", description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    # Kafka connection
    kafka_brokers: List[str] = Field(
        default=["cag-rag-kafka-kafka-bootstrap.kafka:9092"],
        description="Kafka broker addresses"
    )
    kafka_topic_prefix: str = Field(default="cag", description="Kafka topic prefix")

    # ML Models
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    model_cache_dir: str = Field(
        default="/models",
        description="Directory for cached models"
    )

    # Context Management
    context_history_limit: int = Field(
        default=20,
        description="Maximum context history entries to keep"
    )
    context_cache_ttl: int = Field(
        default=3600,
        description="Context cache TTL in seconds"
    )

    @property
    def postgres_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"


# ============================================================================
# RAG Service Configuration
# ============================================================================

class RAGServiceConfig(BaseConfig):
    """RAG Layer Service Configuration"""

    service_name: str = "rag-service"
    port: int = 8002

    # Vector Store (FAISS)
    vector_store_path: str = Field(
        default="/data/vector_store",
        description="Path to FAISS vector store"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model"
    )
    embedding_dimension: int = Field(default=384, description="Embedding dimension")

    # Graph Store (Neo4j)
    neo4j_uri: str = Field(default="bolt://neo4j:7687", description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="changeme", description="Neo4j password")

    # Document Store (MongoDB)
    mongodb_uri: str = Field(
        default="mongodb://mongodb:27017",
        description="MongoDB connection URI"
    )
    mongodb_db: str = Field(default="rag_db", description="MongoDB database name")

    # LLM Configuration
    llm_model: str = Field(
        default="meta-llama/Llama-2-7b-chat-hf",
        description="LLM model name"
    )
    llm_use_4bit: bool = Field(
        default=True,
        description="Use 4-bit quantization for LLM"
    )
    llm_device: str = Field(default="cuda", description="Device: cuda/cpu")
    llm_max_memory_gb: int = Field(default=40, description="Max memory for LLM in GB")
    model_cache_dir: str = Field(default="/models", description="Model cache directory")

    # Generation defaults
    default_max_tokens: int = Field(default=512, ge=50, le=2048)
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    default_top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    default_top_k: int = Field(default=10, ge=1, le=100)

    # Retrieval configuration
    vector_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    graph_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    enable_hybrid_retrieval: bool = Field(default=True)

    @field_validator('vector_weight', 'graph_weight')
    @classmethod
    def validate_weights(cls, v, info):
        """Validate weights are between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{info.field_name} must be between 0.0 and 1.0")
        return v


# ============================================================================
# MCP Service Configuration
# ============================================================================

class MCPServiceConfig(BaseConfig):
    """MCP Master Control Plane Configuration"""

    service_name: str = "mcp-server"
    port: int = 8000

    # Downstream services
    cag_service_url: str = Field(
        default="http://cag-service:8001",
        description="CAG service URL"
    )
    rag_service_url: str = Field(
        default="http://rag-service:8002",
        description="RAG service URL"
    )

    # Timeouts
    cag_timeout: int = Field(default=30, description="CAG service timeout (seconds)")
    rag_timeout: int = Field(default=120, description="RAG service timeout (seconds)")
    health_check_timeout: int = Field(default=5, description="Health check timeout (seconds)")

    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Retry delay in seconds")

    # Circuit breaker
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker")
    circuit_breaker_threshold: int = Field(default=5, description="Failure threshold")
    circuit_breaker_timeout: int = Field(default=60, description="Circuit breaker timeout")


# ============================================================================
# Configuration Loader
# ============================================================================

class ConfigLoader:
    """Load configuration from multiple sources"""

    @staticmethod
    def load_from_yaml(file_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Args:
            file_path: Path to YAML config file

        Returns:
            Configuration dictionary
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return {}

        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {file_path}")
            return config or {}
        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {e}")
            return {}

    @staticmethod
    def load_cag_config(config_file: Optional[str] = None) -> CAGServiceConfig:
        """
        Load CAG service configuration

        Args:
            config_file: Optional path to config file

        Returns:
            CAGServiceConfig instance
        """
        config_dict = {}

        # Load from YAML if provided
        if config_file:
            config_dict = ConfigLoader.load_from_yaml(config_file)

        # Environment variables override YAML
        return CAGServiceConfig(**config_dict)

    @staticmethod
    def load_rag_config(config_file: Optional[str] = None) -> RAGServiceConfig:
        """
        Load RAG service configuration

        Args:
            config_file: Optional path to config file

        Returns:
            RAGServiceConfig instance
        """
        config_dict = {}

        if config_file:
            config_dict = ConfigLoader.load_from_yaml(config_file)

        return RAGServiceConfig(**config_dict)

    @staticmethod
    def load_mcp_config(config_file: Optional[str] = None) -> MCPServiceConfig:
        """
        Load MCP service configuration

        Args:
            config_file: Optional path to config file

        Returns:
            MCPServiceConfig instance
        """
        config_dict = {}

        if config_file:
            config_dict = ConfigLoader.load_from_yaml(config_file)

        return MCPServiceConfig(**config_dict)


# ============================================================================
# Configuration Validation
# ============================================================================

def validate_config(config: BaseConfig) -> bool:
    """
    Validate configuration

    Args:
        config: Configuration to validate

    Returns:
        True if valid, raises exception otherwise
    """
    # Check environment
    if config.environment not in ["development", "staging", "production"]:
        raise ValueError(f"Invalid environment: {config.environment}")

    # Check log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level.upper() not in valid_log_levels:
        raise ValueError(f"Invalid log level: {config.log_level}")

    # Check port range
    if not 1 <= config.port <= 65535:
        raise ValueError(f"Invalid port: {config.port}")

    logger.info(f"Configuration validated for {config.service_name}")
    return True


# ============================================================================
# Environment Detection
# ============================================================================

def get_environment() -> str:
    """
    Detect current environment from environment variable

    Returns:
        Environment string: development/staging/production
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env in ["prod", "production"]:
        return "production"
    elif env in ["stage", "staging"]:
        return "staging"
    else:
        return "development"


def is_production() -> bool:
    """Check if running in production"""
    return get_environment() == "production"


def is_development() -> bool:
    """Check if running in development"""
    return get_environment() == "development"


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Load CAG configuration
    print("=== CAG Service Configuration ===")
    cag_config = ConfigLoader.load_cag_config()
    print(f"Service: {cag_config.service_name}")
    print(f"Port: {cag_config.port}")
    print(f"PostgreSQL URL: {cag_config.postgres_url}")
    print(f"Redis URL: {cag_config.redis_url}")
    print(f"Kafka Brokers: {cag_config.kafka_brokers}")

    print("\n=== RAG Service Configuration ===")
    rag_config = ConfigLoader.load_rag_config()
    print(f"Service: {rag_config.service_name}")
    print(f"Port: {rag_config.port}")
    print(f"LLM Model: {rag_config.llm_model}")
    print(f"Use 4-bit: {rag_config.llm_use_4bit}")
    print(f"Neo4j URI: {rag_config.neo4j_uri}")

    print("\n=== MCP Service Configuration ===")
    mcp_config = ConfigLoader.load_mcp_config()
    print(f"Service: {mcp_config.service_name}")
    print(f"Port: {mcp_config.port}")
    print(f"CAG URL: {mcp_config.cag_service_url}")
    print(f"RAG URL: {mcp_config.rag_service_url}")

    print(f"\n=== Environment ===")
    print(f"Current: {get_environment()}")
    print(f"Is Production: {is_production()}")
    print(f"Is Development: {is_development()}")
