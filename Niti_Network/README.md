# NitiLedger

> Blockchain-based government project transparency and fraud detection system.

## 🚀 Quick Start (Sprint 1)

```bash
cd Niti_Network/backend
docker-compose up --build
```

All services will boot. Wait ~90 seconds for Keycloak and Milvus to initialise.

## 📡 Service Endpoints

| Service | URL | Credentials |
|---|---|---|
| **FastAPI Docs** | http://localhost:8000/docs | JWT (via Keycloak) |
| **FastAPI Health** | http://localhost:8000/health | Public |
| **Next.js Frontend** | http://localhost:3000 | — |
| **Keycloak Admin** | http://localhost:8080 | admin / admin |
| **PostgreSQL** | localhost:5432 | admin / admin |
| **CouchDB** | http://localhost:5984 | admin / adminpw |
| **MinIO Console** | http://localhost:9001 | minio / minio123 |
| **Grafana** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9090 | — |
| **Milvus** | localhost:19530 | — |

## 🏗️ Project Structure

```
Niti_Network/
├── backend/               ← FastAPI + docker-compose (START HERE)
│   ├── docker-compose.yml ← Master: all 10 services
│   ├── .env               ← Local dev environment variables
│   ├── Dockerfile         ← Multi-stage Python 3.12 image
│   ├── requirements.txt
│   └── app/
│       ├── main.py        ← FastAPI app factory
│       ├── api/           ← auth, projects, milestones, documents, biometric, fraud, audit
│       ├── services/      ← fabric_client, minio_service, biometric_service, hash_service, keycloak_service
│       ├── models/        ← SQLAlchemy ORM models (users, projects_mirror, audit_logs, fraud_alerts, document_registry)
│       ├── middleware/    ← auth_middleware, rbac_middleware, rate_limit, logging_middleware
│       └── core/          ← config, security, exceptions
├── frontend/              ← Next.js 14 (Sprint 2 UI)
├── chaincode/go-contract/ ← Go smart contracts (project, milestone, document, audit)
├── analytics/             ← Isolation Forest ML model + fraud_rules.yaml
├── infrastructure/
│   ├── fabric-network/    ← configtx.yaml, crypto-config.yaml, docker-compose.fabric.yml
│   ├── helm/              ← K8s Helm charts (production)
│   └── k8s-manifests/     ← Raw K8s YAML (production)
└── .github/workflows/     ← backend-ci, frontend-ci, chaincode-ci
```

## 🔐 User Roles

| Role | Permissions |
|---|---|
| `org_admin` | Create projects, add milestones, manage users |
| `auditor` | View all projects, review fraud alerts, export reports |
| `citizen` | View public project status |
| `contractor` | Upload documents, biometric verification |
| `system_admin` | Full infrastructure access |

## 🔬 Running Tests

```bash
# Backend (inside container)
docker exec niti-backend pytest --cov=app -v

# Frontend
cd frontend && npm test

# Chaincode
cd chaincode/go-contract && go test ./... -v
```

## 🌐 Sprint Roadmap

| Sprint | Status | Focus |
|---|---|---|
| **Sprint 1** | ✅ Complete | Docker, backend scaffold, auth, RBAC, DB, chaincode |
| **Sprint 2** | 🔜 Next | Real Fabric peer wiring, document upload flow, hash anchoring |
| **Sprint 3** | 🔜 Planned | Biometric DeepFace, Milvus ANN search, Isolation Forest |
| **Sprint 4** | 🔜 Planned | Audit logs, proof export, Prometheus/Grafana, K8s deploy |

## ⚙️ Tech Stack

Hyperledger Fabric v2.5 · FastAPI · Next.js 14 · PostgreSQL 15 · CouchDB 3 · MinIO · Milvus v2.3 · DeepFace · scikit-learn · Keycloak · Docker Compose · Kubernetes k3s · Prometheus · Grafana
