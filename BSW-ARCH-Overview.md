# BSW-ARCH: Enterprise Architecture AI Factory Overview

**Document**: BSW-ARCH-Overview.md
**Version**: v3.0.0
**AppVM**: bsw-arch
**Status**: Production Ready
**Last Updated**: 2025-09-21 11:45 UTC
**Semantic Version**: v3.0.0 (Major: Production release, Minor: Core features, Patch: Documentation)

## BSW-ARCH Mission Statement

The **BSW-ARCH AppVM** serves as the **Enterprise Architecture AI Factory Pipeline** within the Dutch Ministry of Finance's Beter Samen Werken (Working Better Together) initiative. This AppVM orchestrates AI-powered enterprise architecture generation through KERAGR (Knowledge Enhanced RAG) and CrewAI multi-agent systems.

## BSW-ARCH Core Purpose

### Primary Functions
- **🏗️ Enterprise Architecture Generation**: AI-powered creation of TOGAF/Zachman/ArchiMate artifacts
- **🤖 Multi-Agent Coordination**: CrewAI orchestration across Core and Business domains
- **📊 KERAGR Integration**: Knowledge Enhanced RAG for intelligent architecture decisions
- **🔄 Cross-Domain Coordination**: Orchestrates 43 Codeberg organisations across 4 domains
- **📈 ArchOps Automation**: Agentic AI workflows for EA artifact generation

### BSW-ARCH Domain Responsibilities
```
BSW-ARCH (Autonomous) ↔ Core Domain (BNI/BNP/AXIS/PIPE/IV) ↔ Business Domain
```

#### Core Domain Coordination
- **BNI (Personal Space)**: Individual workspace architecture patterns
- **BNP (Professional Space)**: Collaborative environment architecture
- **AXIS (AI Architecture)**: 13 organisations for AI-augmented IT architecture
- **PIPE (AI Interfacing)**: 13 organisations for intelligent integration patterns
- **IV (AI Memory)**: 13 organisations for knowledge management architecture

#### Business Domain Services
- **Architecture Consulting**: Enterprise architecture guidance and frameworks
- **Solution Design**: Technical solution architecture for business requirements
- **Compliance Frameworks**: Dutch Ministry standards and EU Digital Sovereignty
- **Innovation Patterns**: Emerging technology evaluation and integration

## BSW-ARCH Technical Architecture

### Service Portfolio (21 Python Services)
```
📊 Memory Distribution:
├── BSW-ARCH Domain (18%): 106.7MB
├── AXIS Domain (12.3%): 72.7MB
├── PIPE Domain (12.8%): 76.0MB
├── IV Domain (12.8%): 75.6MB
└── Coordination Services (44%): 260.5MB
```

### Container Infrastructure (13 Containers)
```
🐳 Container Stack:
├── Core Monitoring: Grafana (512MB), Prometheus (256MB), PostgreSQL (384MB)
├── Domain Coordinators: AXIS/PIPE/IV (128MB each)
├── Infrastructure: Vault (256MB), Zot Registry (192MB)
└── Storage Cluster: MinIO 5-node (256MB each)
```

### Network Architecture
```
🌐 Service Endpoints:
├── BSW Services: 3000-3999 range
├── AXIS Services: 4000-4999 range
├── PIPE Services: 5000-5999 range
├── IV Services: 6000-6999 range
├── Monitoring: 7000-7999 range
├── Management: 8000-8999 range
└── Storage: 9000-9999 range
```

## BSW-ARCH Operational Status

### Production Metrics (2025-09-20)
- **🎯 Service Health**: 100% (11/11 services responding)
- **💾 Memory Usage**: 4.5GB/7.9GB (57% utilization)
- **💽 Swap Usage**: 892MB/1024MB (87% - monitored)
- **🐳 Container Efficiency**: 100% (13/13 containers running)
- **📊 Average Response Time**: 42.3ms across all services

### Memory Optimization Results
- **🧹 Memory Leaks**: Successfully mitigated (surgical-precision-monitoring)
- **🛡️ Container Limits**: Enforced across all 13 containers
- **🔄 Auto-GC**: Garbage collection automation implemented
- **📈 Memory Recovery**: 600MB system memory freed through optimizations

## BSW-ARCH Security & Compliance

### Dutch Ministry of Finance Standards
- **🇪🇺 EU Digital Sovereignty**: Complete European data residency
- **🔒 Security Classification**: Government Domain 3 (Qubes OS)
- **📋 Compliance**: GDPR, Dutch Government IT Standards
- **🌍 Language**: UK English (mandatory for all documentation)

### Security Implementation
- **🔐 Vault Integration**: All passwords stored in HashiCorp Vault
- **🛡️ Container Security**: Chainguard distroless containers with memory limits
- **🔒 Network Isolation**: Qubes AppVM network segregation
- **📊 Monitoring**: Real-time security and performance monitoring

## BSW-ARCH Quick Start Guide

### Prerequisites
- Qubes OS AppVM: bsw-arch
- Network access to Codeberg (git@codeberg.org)
- HashiCorp Vault configured
- Container runtime (Podman)

### Deployment Commands
```bash
# 1. Navigate to BSW-ARCH directory
cd /home/user/Projects/EA/bsw-infrastructure/bsw-infra

# 2. Deploy complete infrastructure
./src/scripts/deploy-complete-bsw-arch.sh

# 3. Verify service health
curl http://localhost:3111/health

# 4. Access monitoring dashboard
curl http://localhost:3000  # Grafana
```

### Service Management
```bash
# Start memory monitoring
python3 /home/user/Code/bsw-memory-monitor.py &

# Check service status
podman ps --format "table {{.Names}} {{.Status}} {{.Ports}}"

# Apply memory optimization
kill -SIGUSR1 <service-pid>  # Manual garbage collection
```

## BSW-ARCH Documentation Index

### Core Documentation
- **BSW-ARCH-Overview.md** (this document): Main system overview
- **BSW-ARCH-Memory-Optimization.md**: Memory management and leak prevention
- **BSW-ARCH-Service-Architecture.md**: Detailed service architecture
- **BSW-ARCH-Container-Orchestration.md**: Container management and limits
- **BSW-ARCH-Troubleshooting.md**: Problem resolution guide

### Technical Specifications
- **BSW-ARCH-API-Reference.md**: Complete API documentation
- **BSW-ARCH-Network-Architecture.md**: Network topology and security
- **BSW-ARCH-Security-Guide.md**: Security implementation details
- **BSW-ARCH-Performance-Tuning.md**: Performance optimization guide
- **BSW-ARCH-Monitoring-Guide.md**: Monitoring and alerting setup

### Operational Guides
- **BSW-ARCH-Deployment-Guide.md**: Step-by-step deployment instructions
- **BSW-ARCH-Backup-Recovery.md**: Backup and disaster recovery procedures
- **BSW-ARCH-Scaling-Guide.md**: Horizontal and vertical scaling strategies
- **BSW-ARCH-Integration-Guide.md**: Cross-domain integration patterns

## BSW-ARCH Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Monitor memory usage and service health
- **Weekly**: Review container resource utilization
- **Monthly**: Update security patches and dependencies
- **Quarterly**: Performance review and optimization

### Troubleshooting Contacts
- **Memory Issues**: Check BSW-ARCH-Memory-Optimization.md
- **Service Failures**: Refer to BSW-ARCH-Troubleshooting.md
- **Container Problems**: See BSW-ARCH-Container-Orchestration.md
- **Network Issues**: Consult BSW-ARCH-Network-Architecture.md

---

**🎯 BSW-ARCH: Enabling Dutch Ministry of Finance digital transformation through AI-powered enterprise architecture generation and cross-domain coordination.**