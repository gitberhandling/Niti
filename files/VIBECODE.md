# NitiLedger — Vibe Coding Master Prompt

> Copy this file in full and paste it to any AI coding assistant (Cursor, Windsurf, GitHub Copilot, Claude, etc.) as your project context. It contains everything needed to build, run, and extend NitiLedger from scratch.

---

## What Is This Project?

NitiLedger is a **blockchain-based government project transparency and fraud detection system**.

Every government project — its milestones, fund disbursements, and supporting documents — is recorded on an **immutable Hyperledger Fabric ledger**. A fraud detection engine automatically classifies each project as **Green / Amber / Red** using biometric identity checks and an Isolation Forest anomaly model. Role-based dashboards serve citizens, contractors, auditors, and admins.

**Zero licensing cost. 100% open-source stack. On-premise deployment.**

---

## Stack (Never Deviate From This)

| Layer | Technology |
|---|---|
| Blockchain | Hyperledger Fabric v2.5, RAFT consensus, 2-org |
| Smart Contracts | Go |
| Backend API | FastAPI, Python 3.12 |
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Relational DB | PostgreSQL 15 |
| Blockchain State DB | CouchDB 3 |
| Object Storage | MinIO (S3-compatible) |
| Vector DB | Milvus v2.3 (biometric embeddings) |
| Biometrics | DeepFace + OpenCV |
| Fraud / ML | scikit-learn (Isolation Forest) |
| Identity / SSO | Keycloak (OIDC + JWT) |
| Containers | Docker + Docker Compose v2.20+ |
| Production Orchestration | Kubernetes k3s |
| Monitoring | Prometheus + Grafana |
| Logging | Loki |
| CI/CD | GitHub Actions |
| Testing | Pytest (backend, 90%+ coverage), Jest (frontend) |
| API Docs | OpenAPI / Swagger (auto via FastAPI) |

---

## Workspace Layout

```
blockchain-workspace/
├── backend/                  ← FastAPI app + docker-compose.yml (MASTER CONTROL)
│   ├── docker-compose.yml
│   ├── .env / .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/              ← Route handlers (one file per domain)
│       ├── services/         ← Business logic (Fabric, MinIO, fraud, biometric)
│       ├── models/           ← SQLAlchemy ORM models
│       ├── middleware/       ← JWT, RBAC, rate limit, logging
│       ├── db/               ← DB engine + Alembic migrations
│       └── core/             ← Config, security, exceptions
├── frontend/                 ← Next.js App Router
│   └── src/
│       ├── app/              ← One folder per screen/route
│       ├── components/       ← Feature-grouped UI components
│       └── lib/              ← API client, auth helpers, utils
├── chaincode/
│   └── go-contract/
│       └── contracts/        ← project, milestone, document, audit contracts
├── analytics/
│   └── models/               ← Isolation Forest + fraud_rules.yaml
├── infrastructure/
│   ├── helm/                 ← Helm charts for K8s deploy
│   ├── k8s-manifests/        ← Raw K8s YAML
│   └── fabric-network/       ← configtx, crypto-config, org MSPs
└── .github/workflows/        ← CI/CD pipelines
```

---

## Running Locally (Single Command)

```bash
cd blockchain-workspace/backend
cp .env.example .env
docker-compose up --build
```

All services start on these ports:

| Service | Port | Credentials |
|---|---|---|
| FastAPI backend | 8000 | JWT (via Keycloak) |
| Next.js frontend | 3000 | — |
| Keycloak admin | 8080 | admin / admin |
| PostgreSQL | 5432 | admin / admin |
| CouchDB | 5984 | admin / adminpw |
| MinIO console | 9001 | minio / minio123 |
| Grafana | 3001 | admin / admin |
| Milvus | 19530 | default |

---

## User Roles & Permissions

| Role | Can Do |
|---|---|
| **Org Admin** | Create/close projects, add milestones, manage users |
| **Auditor** | View all projects, review fraud alerts, export reports, view audit logs |
| **Citizen** | View public project status and fund utilisation |
| **Contractor** | Submit documents, complete biometric verification, view own project status |
| **System Admin** | Infra monitoring, Keycloak config, Fabric network management |

All routes are protected by `auth_middleware.py` (JWT validation) then `rbac_middleware.py` (role check). A role mismatch returns `HTTP 403 { "error": "insufficient_role" }`.

---

## Core Data Models

### PostgreSQL Tables

```sql
-- Users (synced from Keycloak)
users: id, keycloak_id, email, role, org_id, created_at, is_active

-- Mirror of on-chain project state (read-optimised)
projects_mirror: id, chain_project_id, name, status, budget, dept_id, last_synced

-- Append-only, never DELETE or UPDATE
audit_logs: id, actor_id, action, entity_type, entity_id, timestamp, metadata (JSONB)

-- Fraud classification results
fraud_alerts: id, project_id, contractor_id, severity (green|amber|red), reason, created_at, resolved_at

-- Off-chain file registry
document_registry: id, project_id, milestone_id, sha256_hash, minio_key, uploaded_by, uploaded_at
```

### On-Chain (Hyperledger Fabric / CouchDB World State)

```go
// Project
type Project struct {
    ProjectID    string      `json:"projectID"`
    Name         string      `json:"name"`
    Department   string      `json:"department"`
    Status       string      `json:"status"`       // active | closed
    TotalBudget  float64     `json:"totalBudget"`
    Disbursed    float64     `json:"disbursed"`
    CreatedAt    time.Time   `json:"createdAt"`
    UpdatedAt    time.Time   `json:"updatedAt"`
    Milestones   []Milestone `json:"milestones"`
}

// Milestone
type Milestone struct {
    MilestoneID           string    `json:"milestoneID"`
    ProjectID             string    `json:"projectID"`
    Title                 string    `json:"title"`
    Status                string    `json:"status"`       // pending | verified | rejected
    CompletionPercentage  int       `json:"completionPercentage"`
    EvidenceHash          string    `json:"evidenceHash"` // SHA-256 of uploaded file
    VerifiedBy            string    `json:"verifiedBy"`
    VerifiedAt            time.Time `json:"verifiedAt"`
}
```

---

## API Endpoints Reference

### Authentication
```
POST /auth/token          — Exchange Keycloak OIDC code for JWT (public)
```

### Projects
```
GET    /projects                — List projects (filterable by dept, status, fraud severity)
POST   /projects                — Create project on-chain (Admin only)
GET    /projects/{id}           — Project detail + milestones + documents
PATCH  /projects/{id}/status    — Update status (Admin only)
POST   /projects/{id}/milestones — Add milestone (Admin only)
```

### Documents
```
POST   /documents/upload-url    — Generate 15-min signed MinIO URL (Contractor)
POST   /documents/verify        — Compute SHA-256 and anchor hash on-chain (Contractor)
GET    /documents/{id}          — Get document metadata + on-chain hash
```

### Biometric
```
POST   /biometric/verify        — 1:1 face match + 1:N duplicate check (Contractor)
GET    /biometric/status/{id}   — Get verification result
```

### Fraud
```
GET    /fraud/alerts            — List alerts (Auditor, Admin)
GET    /fraud/alerts/{id}       — Alert detail with comparison view
PATCH  /fraud/alerts/{id}/resolve — Approve/Escalate alert (Auditor)
```

### Audit & Reporting
```
GET    /audit/logs              — Immutable audit log with filters (Auditor)
GET    /reports/export          — Export JSON proof report for a project (Admin)
POST   /webhooks/register       — Register downstream webhook endpoint (Admin)
```

---

## Blockchain Endorsement Policy

```
AND('Org1MSP.peer', 'Org2MSP.peer')
```

Both organisations must endorse every transaction. Single-org requests are rejected. This is defined in `infrastructure/fabric-network/configtx.yaml`.

---

## Document Upload Flow (Step by Step)

```
Contractor          Backend              MinIO           Fabric
    |                   |                   |               |
    |-- POST /documents/upload-url -------->|               |
    |<-- { signedUrl, documentId } --------|               |
    |                   |                   |               |
    |-- PUT signedUrl (file binary) ------->|               |
    |                   |                   |               |
    |-- POST /documents/verify ------------>|               |
    |                   |-- compute SHA-256 |               |
    |                   |-- store metadata in PostgreSQL    |
    |                   |-- InvokeChaincode(AnchorHash) --->|
    |                   |<-- txID ----------------------------|
    |<-- { txID, sha256Hash, documentId } --|               |
```

---

## Biometric Verification Flow

```
1. Contractor opens /biometric/verify in browser
2. CameraCapture.tsx uses navigator.mediaDevices.getUserMedia()
3. Captured frame sent to POST /biometric/verify as base64
4. Backend:
   a. Extracts face embedding via DeepFace (ArcFace model)
   b. 1:1 match: compare embedding vs ID document photo (threshold > 0.70)
   c. 1:N check: Milvus ANN search across all registered embeddings
   d. Returns: { matchScore, isDuplicate, status: 'green'|'amber'|'red' }
5. Result stored in fraud_alerts table
6. If Red: webhook fires to admin
```

---

## Fraud Detection Rules

Defined in `analytics/models/fraud_rules.yaml`. The engine runs on every milestone submission.

```yaml
rules:
  - id: R001
    name: duplicate_contractor
    description: Same face found in Milvus for different contractor ID
    severity: red

  - id: R002
    name: budget_overshoot
    description: Disbursed amount exceeds totalBudget by more than 5%
    severity: red

  - id: R003
    name: milestone_backdating
    description: Milestone completion date is before project creation date
    severity: red

  - id: R004
    name: rapid_milestone_completion
    description: All milestones marked complete within 24 hours of project creation
    severity: amber

  - id: R005
    name: document_hash_mismatch
    description: Re-submitted document hash differs from original on-chain hash
    severity: amber

  - id: R006
    name: low_biometric_confidence
    description: 1:1 face match score between 0.50 and 0.70
    severity: amber
```

The Isolation Forest model in `analytics/models/isolation_forest.py` runs as a second pass, flagging statistical outliers in project spending patterns.

---

## Screens to Build (Frontend)

| Route | Component | Role Access |
|---|---|---|
| `/login` | SSO login card, Keycloak redirect | Public |
| `/dashboard` | KPI cards, activity feed, donut chart | Admin, Auditor |
| `/projects` | Filterable table, status badges | All |
| `/projects/[id]` | Detail, milestone timeline, doc tab, fraud tab, audit tab | All |
| `/documents/upload` | 4-step wizard, drag-drop, hash preview | Contractor |
| `/biometric/verify` | Split-panel camera capture + result | Contractor |
| `/fraud/alerts` | Alert queue, severity tabs, side-by-side comparison | Auditor, Admin |
| `/audit/logs` | Timeline view, export to JSON | Auditor |

**Design tokens:** Primary `#1F5C99`, Action `#2E75B6`, Green `#217346`, Amber `#C17F24`, Red `#CC0000`, Background `#F4F7FB`.

**Status badge pattern:**
```tsx
// Green = verified, Amber = under review, Red = flagged
<StatusBadge status="green" />   // bg-green-100 text-green-800
<StatusBadge status="amber" />   // bg-amber-100 text-amber-800
<StatusBadge status="red"   />   // bg-red-100   text-red-800
```

---

## Smart Contract Functions to Implement

```go
// project_contract.go
CreateProject(ctx, projectID, name, dept, budget string) error
GetProject(ctx, projectID string) (*Project, error)
UpdateProjectStatus(ctx, projectID, status string) error
ListProjects(ctx) ([]*Project, error)

// milestone_contract.go
AddMilestone(ctx, projectID, milestoneID, title string) error
UpdateMilestoneStatus(ctx, milestoneID, status, verifiedBy string) error

// document_contract.go
AnchorDocumentHash(ctx, documentID, projectID, sha256Hash string) error
VerifyDocumentHash(ctx, documentID, sha256Hash string) (bool, error)

// audit_contract.go
AppendAuditEntry(ctx, actorID, action, entityID string) error
GetAuditTrail(ctx, entityID string) ([]*AuditEntry, error)
```

All functions must:
- Validate caller MSP matches required org
- Write a corresponding audit entry via `AppendAuditEntry`
- Return structured errors, never panic

---

## Environment Variables (.env.example)

```env
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=niti_ledger
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=niti-ledger
KEYCLOAK_CLIENT_ID=backend-client
KEYCLOAK_CLIENT_SECRET=change-me

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_BUCKET=niti-documents

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION=contractor_faces

# Hyperledger Fabric
FABRIC_CHANNEL=niti-channel
FABRIC_CHAINCODE=niti-contract
FABRIC_ORG1_MSP=Org1MSP
FABRIC_ORG2_MSP=Org2MSP
FABRIC_PEER_ENDPOINT=peer0.org1.example.com:7051

# App
APP_ENV=development
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=http://localhost:3000
```

---

## Testing Checklist

### Backend (Pytest)
- [ ] `test_auth.py` — JWT validation, role extraction, 401/403 responses
- [ ] `test_projects.py` — CRUD, endorsement policy, duplicate ID handling
- [ ] `test_documents.py` — Signed URL generation, hash anchoring, hash mismatch
- [ ] `test_fraud.py` — Rule engine triggers (R001–R006), severity classification
- [ ] `test_biometric.py` — 1:1 match above/below threshold, 1:N duplicate detection
- Target: **90%+ line coverage** (`pytest --cov=app --cov-report=term-missing`)

### Frontend (Jest + React Testing Library)
- [ ] `ProjectTable.test.tsx` — renders rows, filter chips, status badges
- [ ] `UploadZone.test.tsx` — file drop, hash preview display, submit flow

### Integration
- [ ] Fabric test network spins up and chaincode deploys cleanly
- [ ] End-to-end: create project → add milestone → upload document → verify hash on-chain

---

## Sprint Milestones

| Sprint | What Gets Built | Definition of Done |
|---|---|---|
| **Sprint 1** | Docker Compose, Fabric network, Keycloak SSO, RBAC | `docker-compose up` starts all services; login works; role enforcement tested |
| **Sprint 2** | Smart contracts, project/milestone APIs, document upload + hash anchoring | Project creates on-chain; document hash verifiable from Fabric CLI |
| **Sprint 3** | Biometric verification, fraud rule engine, Isolation Forest, alert dashboard | Red alert fires for duplicate face; Green/Amber/Red visible in UI |
| **Sprint 4** | Audit logs, JSON proof export, load testing, Prometheus/Grafana, K8s deploy | 500 TPS on Caliper; all dashboards live; Helm deploy to k3s succeeds |

---

## Vibe Coding Instructions for AI

When I say **"build X"**, follow these rules:

1. **Never invent a new library.** Use only what is listed in the stack above.
2. **All API routes need middleware** — every handler goes through `auth_middleware` then `rbac_middleware`. Never bypass.
3. **On-chain = immutable.** Never add a delete or update function to the audit contract.
4. **Hash before chain.** Documents always go to MinIO first; only the SHA-256 hash goes on-chain.
5. **Structured errors.** All API errors return `{ "error": "snake_case_code", "detail": "human message" }`.
6. **ENV over hardcode.** Credentials, URLs, secrets always come from `.env` via `core/config.py`.
7. **Type everything.** Python: use Pydantic models for all request/response. TypeScript: no `any`.
8. **Test as you go.** Every new service function needs at least one Pytest unit test.
9. **docker-compose.yml is the source of truth** for local service config — do not create separate config files per service.
10. **Green/Amber/Red is sacred.** This classification must be consistent across the fraud engine, the biometric service, the API response, and the frontend badge. Never use different terminology.

---

## Quick Reference Commands

```bash
# Start everything locally
cd backend && docker-compose up --build

# Run backend tests
docker exec niti-backend pytest --cov=app -v

# Run frontend tests
cd frontend && npm test

# Deploy chaincode (after Fabric network is up)
cd infrastructure/fabric-network
./scripts/deploy-chaincode.sh

# Apply K8s manifests (staging)
kubectl apply -f infrastructure/k8s-manifests/

# Helm deploy (production)
helm upgrade --install niti-backend infrastructure/helm/backend/
helm upgrade --install niti-frontend infrastructure/helm/frontend/

# View Fabric ledger state
peer chaincode query -C niti-channel -n niti-contract -c '{"Args":["ListProjects"]}'

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

*End of vibe coding master prompt. Paste this entire file as context when starting a new coding session.*
