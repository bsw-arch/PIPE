#!/bin/bash
# Initialize databases for CAG+RAG system

set -e

echo "================================"
echo "CAG+RAG Database Initialization"
echo "================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-cag}"
POSTGRES_DB="${POSTGRES_DB:-cag_db}"

NEO4J_HOST="${NEO4J_HOST:-localhost}"
NEO4J_PORT="${NEO4J_PORT:-7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"

MONGODB_HOST="${MONGODB_HOST:-localhost}"
MONGODB_PORT="${MONGODB_PORT:-27017}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Initialize PostgreSQL
init_postgres() {
    log_info "Initializing PostgreSQL..."

    if ! command_exists psql; then
        log_warn "psql not found, skipping PostgreSQL initialization"
        return
    fi

    # Create tables
    PGPASSWORD="${POSTGRES_PASSWORD}" psql \
        -h "${POSTGRES_HOST}" \
        -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        <<EOF
-- Create user contexts table
CREATE TABLE IF NOT EXISTS user_contexts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    context_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, session_id)
);

-- Create interaction history table
CREATE TABLE IF NOT EXISTS interaction_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    query_type VARCHAR(50),
    domains TEXT[],
    response_preview TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_contexts_user_id ON user_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_contexts_session_id ON user_contexts(session_id);
CREATE INDEX IF NOT EXISTS idx_interaction_history_user_id ON interaction_history(user_id);
CREATE INDEX IF NOT EXISTS idx_interaction_history_created_at ON interaction_history(created_at);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${POSTGRES_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${POSTGRES_USER};
EOF

    log_info "PostgreSQL initialized successfully"
}

# Initialize Neo4j
init_neo4j() {
    log_info "Initializing Neo4j..."

    if ! command_exists cypher-shell; then
        log_warn "cypher-shell not found, skipping Neo4j initialization"
        return
    fi

    # Create constraints and indexes
    cypher-shell \
        -a "bolt://${NEO4J_HOST}:${NEO4J_PORT}" \
        -u "${NEO4J_USER}" \
        -p "${NEO4J_PASSWORD}" \
        <<EOF
// Create constraints
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE;

// Create indexes
CREATE INDEX entity_domain IF NOT EXISTS FOR (e:Entity) ON (e.domain);
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);

// Create sample domains
MERGE (d1:Domain {name: 'AXIS', description: 'Architecture domain'});
MERGE (d2:Domain {name: 'PIPE', description: 'Pipeline domain'});
MERGE (d3:Domain {name: 'ECO', description: 'Ecological domain'});
MERGE (d4:Domain {name: 'IV', description: 'Intelligence/Validation domain'});

RETURN 'Neo4j initialized' AS status;
EOF

    log_info "Neo4j initialized successfully"
}

# Initialize MongoDB
init_mongodb() {
    log_info "Initializing MongoDB..."

    if ! command_exists mongosh; then
        log_warn "mongosh not found, skipping MongoDB initialization"
        return
    fi

    # Create collections and indexes
    mongosh "mongodb://${MONGODB_HOST}:${MONGODB_PORT}/cag_rag" <<EOF
// Create collections for each domain
db.createCollection('AXIS_documents');
db.createCollection('PIPE_documents');
db.createCollection('ECO_documents');
db.createCollection('IV_documents');

// Create text indexes for full-text search
db.AXIS_documents.createIndex({
    title: 'text',
    content: 'text',
    tags: 'text'
});

db.PIPE_documents.createIndex({
    title: 'text',
    content: 'text',
    tags: 'text'
});

db.ECO_documents.createIndex({
    title: 'text',
    content: 'text',
    tags: 'text'
});

db.IV_documents.createIndex({
    title: 'text',
    content: 'text',
    tags: 'text'
});

// Create metadata indexes
db.AXIS_documents.createIndex({ 'metadata.category': 1 });
db.PIPE_documents.createIndex({ 'metadata.category': 1 });
db.ECO_documents.createIndex({ 'metadata.category': 1 });
db.IV_documents.createIndex({ 'metadata.category': 1 });

print('MongoDB initialized');
EOF

    log_info "MongoDB initialized successfully"
}

# Main execution
main() {
    log_info "Starting database initialization..."
    echo

    # Check required environment variables
    if [ -z "${POSTGRES_PASSWORD}" ]; then
        log_error "POSTGRES_PASSWORD not set"
        exit 1
    fi

    if [ -z "${NEO4J_PASSWORD}" ]; then
        log_error "NEO4J_PASSWORD not set"
        exit 1
    fi

    # Initialize databases
    init_postgres
    echo
    init_neo4j
    echo
    init_mongodb
    echo

    log_info "Database initialization complete!"
}

# Run main
main
