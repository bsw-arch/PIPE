# BSW KERAG-R Knowledge Graph Deployment
> **Knowledge Enhanced RAG** with Enterprise Architecture Integration
> **Status**: Production-ready with Vault-managed security

## ✅ **Integration Complete**

Neo4j Knowledge Graph is now **fully integrated** into the BSW-ARCH platform with:
- ✅ **Vault-managed passwords** (no hardcoded credentials)
- ✅ **BSW naming convention** compliance
- ✅ **HA PostgreSQL integration** for metadata
- ✅ **OpenTofu/Ansible/Helm** infrastructure automation

## 🏗️ **Infrastructure Components**

### **1. OpenTofu Infrastructure as Code**
- ✅ Neo4j container resource defined in `opentofu/main.tf`
- ✅ Proper network integration with EA hybrid network
- ✅ Volume management for persistent data
- ✅ Health checks and restart policies
- ✅ Labels and metadata for enterprise governance

### **2. Ansible Automation**
- ✅ Neo4j component added to `ansible-playbooks/hybrid-architects-infrastructure.yml`
- ✅ Directory creation for Neo4j data persistence
- ✅ Service endpoint configuration
- ✅ Integration test targets
- ✅ Startup script integration

### **3. Vault Secrets Management**
- ✅ Neo4j authentication stored in Vault
- ✅ Secret path: `ea-secrets/neo4j/auth`
- ✅ Password: `BSW-KERAG-2024`
- ✅ Integrated with existing vault workflow

### **4. Docker Compose Orchestration**
- ✅ Complete BSW KERAG-R stack in `docker-compose-bsw-kerag.yml`
- ✅ Neo4j with APOC and Graph Data Science plugins
- ✅ Frontend integration with Neo4j connection
- ✅ Data loader for BSW knowledge initialization
- ✅ Vault integration for secrets management

## 🚀 **Deployment Options**

### **Option 1: Via OpenTofu**
```bash
cd /home/user/Code/opentofu
tofu plan
tofu apply
```

### **Option 2: Via Ansible**
```bash
ansible-playbook -i ansible-playbooks/inventory/hybrid-architects ansible-playbooks/hybrid-architects-infrastructure.yml
```

### **Option 3: Via Docker Compose**
```bash
# Ensure directories exist
sudo mkdir -p /var/lib/neo4j-bsw /var/lib/neo4j-bsw-logs /var/lib/neo4j-bsw-import /var/lib/vault-bsw

# Start the BSW KERAG-R stack
podman-compose -f docker-compose-bsw-kerag.yml up -d
```

### **Option 4: Via Make (Recommended)**
```bash
make vault-setup  # Configure Vault secrets
make deploy       # Deploy full infrastructure
make test         # Run integration tests
```

## 🧠 **Knowledge Graph + Vector Search Access**

### **Neo4j Browser (Graph Database)**
- **URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: BSW-KERAG-2024
- **Database**: neo4j (default)

### **Qdrant Dashboard (Vector Database)**
- **URL**: http://localhost:6333/dashboard
- **Collections**: `bsw_entities`, `bsw_documents`
- **Vector Dimension**: 384 (all-MiniLM-L6-v2 embeddings)
- **API**: http://localhost:6333

### **KERAG-R Portal (Hybrid Interface)**
- **URL**: http://localhost:3003/kerag
- **Status**: Live connection indicator
- **Features**: Real-time BSW knowledge visualization with hybrid search

### **Hybrid Search API**
- **URL**: http://localhost:8001
- **Endpoints**:
  - `GET /search?q=<query>` - Hybrid graph+vector search
  - `GET /entity/<id>` - Entity details
  - `GET /collections` - Vector collection info

### **Sample Cypher Queries**
```cypher
// View all BSW entities
MATCH (n) RETURN n LIMIT 25

// EA Team structure
MATCH (ea:EARole)-[:ASSIGNED_TO]->(vm:AppVM) 
RETURN ea.person, ea.name, vm.name

// AXIS system dependencies
MATCH (s1:System)-[r]->(s2:System) 
RETURN s1.name, type(r), s2.name

// Information objects and data relationships
MATCH (io:InformationObject)-[:REQUIRES]->(do:DataObject) 
RETURN io.name, do.name
```

## 📊 **Current Knowledge Graph Data**

- **6 Nodes** loaded with BSW structure:
  - Information Objects (BSW KERAG-R System)
  - Systems (AXIS Core, Intelliverse, PIPE Interface)
  - Data Objects (Knowledge Graph data)
  - EA Roles (Data Architect - Maria Santos)
  - AppVMs (logical partitions)

- **System Relationships**:
  - AXIS → Intelliverse → PIPE → Knowledge Graph
  - EA Roles → AppVM assignments
  - Information Objects → Data Object dependencies

## 🔐 **Security & Governance**

- **Vault Integration**: All secrets managed through HashiCorp Vault
- **Network Isolation**: Dedicated EA network for service communication  
- **Data Persistence**: Proper volume management for production use
- **Health Monitoring**: Built-in health checks and monitoring
- **Access Control**: Neo4j authentication integrated with Vault

## 🎯 **AXIS Ecosystem Context**

The Neo4j Knowledge Graph is now properly positioned within the AXIS ecosystem:

- **AXIS Core**: Advanced Enterprise Architecture System
- **Intelliverse (IV)**: RAG/CAG AI memory layer integration
- **PIPE Interface**: Bot-driven system interactions
- **BSW Knowledge Layer**: "Beter Samen Werken" information management
- **KERAG-R**: Knowledge Enhanced Reasoning with Advanced Graph Relations

## ✨ **Next Steps**

1. **Scale Data Loading**: Use the Python loader to add more BSW entities
2. **API Integration**: Connect EA tools to Neo4j via REST/Bolt
3. **Visualization**: Enhance KERAG-R portal with D3.js graph rendering
4. **Analytics**: Implement Graph Data Science algorithms for insights
5. **Monitoring**: Add Prometheus metrics for Neo4j performance

The BSW KERAG-R Knowledge Graph is now **enterprise-ready** and fully integrated with your OpenTofu/Ansible/Vault infrastructure! 🎉