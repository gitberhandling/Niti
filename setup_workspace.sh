#!/bin/bash
set -e

echo "🚀 Creating NitiLedger workspace..."

# Root
mkdir -p blockchain-workspace
cd blockchain-workspace

# ─── BACKEND ───────────────────────────────────────────────
mkdir -p backend/app/{api,services,models,middleware,db/migrations/versions,core}
mkdir -p backend/tests

touch backend/docker-compose.yml
touch backend/.env backend/.env.example
touch backend/Dockerfile backend/requirements.txt

touch backend/app/main.py
touch backend/app/api/__init__.py
touch backend/app/api/{auth,projects,milestones,documents,biometric,fraud,audit,reports}.py
touch backend/app/services/{fabric_client,minio_service,keycloak_service,fraud_engine,biometric_service,hash_service,webhook_service}.py
touch backend/app/models/{user,project,milestone,document,fraud_alert,audit_log}.py
touch backend/app/middleware/{auth_middleware,rbac_middleware,rate_limit,logging_middleware}.py
touch backend/app/db/database.py
touch backend/app/db/migrations/env.py
touch backend/app/core/{config,security,exceptions}.py

touch backend/tests/{conftest,test_auth,test_projects,test_documents,test_fraud,test_biometric}.py

# ─── FRONTEND ──────────────────────────────────────────────
mkdir -p frontend/src/app/{login,dashboard,"projects/[id]","documents/upload","biometric/verify","fraud/alerts","audit/logs"}
mkdir -p frontend/src/components/{layout,projects,documents,biometric,fraud,shared}
mkdir -p frontend/src/lib
mkdir -p frontend/src/types
mkdir -p frontend/__tests__

touch frontend/Dockerfile frontend/package.json frontend/next.config.js
touch frontend/tailwind.config.js frontend/tsconfig.json

touch frontend/src/app/login/page.tsx
touch frontend/src/app/dashboard/page.tsx
touch frontend/src/app/projects/page.tsx
touch frontend/src/app/projects/\[id\]/page.tsx
touch frontend/src/app/documents/upload/page.tsx
touch frontend/src/app/biometric/verify/page.tsx
touch frontend/src/app/fraud/alerts/page.tsx
touch frontend/src/app/audit/logs/page.tsx

touch frontend/src/components/layout/{Sidebar,Topbar}.tsx
touch frontend/src/components/projects/{ProjectTable,MilestoneTimeline}.tsx
touch frontend/src/components/documents/UploadZone.tsx
touch frontend/src/components/biometric/CameraCapture.tsx
touch frontend/src/components/fraud/AlertQueue.tsx
touch frontend/src/components/shared/{StatusBadge,HashDisplay,KpiCard}.tsx

touch frontend/src/lib/{api-client,auth,utils}.ts
touch frontend/src/types/index.ts
touch frontend/__tests__/{ProjectTable,UploadZone}.test.tsx

# ─── CHAINCODE ─────────────────────────────────────────────
mkdir -p chaincode/go-contract/{contracts,models,tests}

touch chaincode/go-contract/go.mod
touch chaincode/go-contract/go.sum
touch chaincode/go-contract/contracts/{project_contract,milestone_contract,audit_contract,document_contract}.go
touch chaincode/go-contract/models/{project,milestone,audit_entry}.go
touch chaincode/go-contract/tests/{project_contract_test,milestone_contract_test}.go

# ─── ANALYTICS ─────────────────────────────────────────────
mkdir -p analytics/{models,notebooks}

touch analytics/requirements.txt analytics/Dockerfile
touch analytics/models/{isolation_forest,feature_engineering,model_trainer}.py
touch analytics/models/fraud_rules.yaml
touch analytics/notebooks/{fraud_analysis,model_evaluation}.ipynb

# ─── INFRASTRUCTURE ────────────────────────────────────────
mkdir -p infrastructure/helm/{backend,frontend}
mkdir -p infrastructure/k8s-manifests
mkdir -p infrastructure/fabric-network/organizations/{Org1MSP,Org2MSP}

touch infrastructure/helm/backend/{Chart,values}.yaml
touch infrastructure/helm/frontend/{Chart,values}.yaml

touch infrastructure/k8s-manifests/{namespace,keycloak,postgres,minio,milvus,monitoring,ingress}.yaml

touch infrastructure/fabric-network/{configtx,crypto-config}.yaml
touch infrastructure/fabric-network/docker-compose.fabric.yml

# ─── CI/CD ─────────────────────────────────────────────────
mkdir -p .github/workflows

touch .github/workflows/{backend-ci,frontend-ci,chaincode-ci,deploy-staging,deploy-prod}.yml

# ─── ROOT FILES ────────────────────────────────────────────
touch README.md .gitignore CONTRIBUTING.md

echo ""
echo "✅ NitiLedger workspace created successfully!"
echo ""
echo "📁 Structure summary:"
find . -type d | sed 's|[^/]*/|  |g' | head -60
echo ""
echo "📄 Total files created: $(find . -type f | wc -l)"
echo "📂 Total directories:   $(find . -type d | wc -l)"
