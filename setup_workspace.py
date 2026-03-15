import os
import sys

def create_workspace():
    print("🚀 Creating NitiLedger workspace in Niti_Network...")
    
    # Root
    os.makedirs("Niti_Network", exist_ok=True)
    os.chdir("Niti_Network")
    
    # Backend
    backend_dirs = [
        "backend/app/api", "backend/app/services", "backend/app/models",
        "backend/app/middleware", "backend/app/db/migrations/versions",
        "backend/app/core", "backend/tests"
    ]
    for d in backend_dirs:
        os.makedirs(d, exist_ok=True)
        
    backend_files = [
        "backend/docker-compose.yml", "backend/.env", "backend/.env.example",
        "backend/Dockerfile", "backend/requirements.txt",
        "backend/app/main.py", "backend/app/api/__init__.py",
        "backend/app/api/auth.py", "backend/app/api/projects.py", "backend/app/api/milestones.py", "backend/app/api/documents.py", "backend/app/api/biometric.py", "backend/app/api/fraud.py", "backend/app/api/audit.py", "backend/app/api/reports.py",
        "backend/app/services/fabric_client.py", "backend/app/services/minio_service.py", "backend/app/services/keycloak_service.py", "backend/app/services/fraud_engine.py", "backend/app/services/biometric_service.py", "backend/app/services/hash_service.py", "backend/app/services/webhook_service.py",
        "backend/app/models/user.py", "backend/app/models/project.py", "backend/app/models/milestone.py", "backend/app/models/document.py", "backend/app/models/fraud_alert.py", "backend/app/models/audit_log.py",
        "backend/app/middleware/auth_middleware.py", "backend/app/middleware/rbac_middleware.py", "backend/app/middleware/rate_limit.py", "backend/app/middleware/logging_middleware.py",
        "backend/app/db/database.py", "backend/app/db/migrations/env.py",
        "backend/app/core/config.py", "backend/app/core/security.py", "backend/app/core/exceptions.py",
        "backend/tests/conftest.py", "backend/tests/test_auth.py", "backend/tests/test_projects.py", "backend/tests/test_documents.py", "backend/tests/test_fraud.py", "backend/tests/test_biometric.py"
    ]
    for f in backend_files:
        open(f, 'a').close()
        
    # Frontend
    frontend_dirs = [
        "frontend/src/app/login", "frontend/src/app/dashboard", "frontend/src/app/projects/[id]",
        "frontend/src/app/documents/upload", "frontend/src/app/biometric/verify", "frontend/src/app/fraud/alerts", "frontend/src/app/audit/logs",
        "frontend/src/components/layout", "frontend/src/components/projects", "frontend/src/components/documents", "frontend/src/components/biometric", "frontend/src/components/fraud", "frontend/src/components/shared",
        "frontend/src/lib", "frontend/src/types", "frontend/__tests__"
    ]
    for d in frontend_dirs:
        os.makedirs(d, exist_ok=True)
        
    frontend_files = [
        "frontend/Dockerfile", "frontend/package.json", "frontend/next.config.js",
        "frontend/tailwind.config.js", "frontend/tsconfig.json",
        "frontend/src/app/login/page.tsx", "frontend/src/app/dashboard/page.tsx", "frontend/src/app/projects/page.tsx", "frontend/src/app/projects/[id]/page.tsx",
        "frontend/src/app/documents/upload/page.tsx", "frontend/src/app/biometric/verify/page.tsx", "frontend/src/app/fraud/alerts/page.tsx", "frontend/src/app/audit/logs/page.tsx",
        "frontend/src/components/layout/Sidebar.tsx", "frontend/src/components/layout/Topbar.tsx",
        "frontend/src/components/projects/ProjectTable.tsx", "frontend/src/components/projects/MilestoneTimeline.tsx",
        "frontend/src/components/documents/UploadZone.tsx",
        "frontend/src/components/biometric/CameraCapture.tsx",
        "frontend/src/components/fraud/AlertQueue.tsx",
        "frontend/src/components/shared/StatusBadge.tsx", "frontend/src/components/shared/HashDisplay.tsx", "frontend/src/components/shared/KpiCard.tsx",
        "frontend/src/lib/api-client.ts", "frontend/src/lib/auth.ts", "frontend/src/lib/utils.ts",
        "frontend/src/types/index.ts",
        "frontend/__tests__/ProjectTable.test.tsx", "frontend/__tests__/UploadZone.test.tsx"
    ]
    for f in frontend_files:
        open(f, 'a').close()
        
    # Chaincode
    chaincode_dirs = [
        "chaincode/go-contract/contracts", "chaincode/go-contract/models", "chaincode/go-contract/tests"
    ]
    for d in chaincode_dirs:
        os.makedirs(d, exist_ok=True)
        
    chaincode_files = [
        "chaincode/go-contract/go.mod", "chaincode/go-contract/go.sum",
        "chaincode/go-contract/contracts/project_contract.go", "chaincode/go-contract/contracts/milestone_contract.go", "chaincode/go-contract/contracts/audit_contract.go", "chaincode/go-contract/contracts/document_contract.go",
        "chaincode/go-contract/models/project.go", "chaincode/go-contract/models/milestone.go", "chaincode/go-contract/models/audit_entry.go",
        "chaincode/go-contract/tests/project_contract_test.go", "chaincode/go-contract/tests/milestone_contract_test.go"
    ]
    for f in chaincode_files:
        open(f, 'a').close()
        
    # Analytics
    analytics_dirs = [
        "analytics/models", "analytics/notebooks"
    ]
    for d in analytics_dirs:
        os.makedirs(d, exist_ok=True)
        
    analytics_files = [
        "analytics/requirements.txt", "analytics/Dockerfile",
        "analytics/models/isolation_forest.py", "analytics/models/feature_engineering.py", "analytics/models/model_trainer.py",
        "analytics/models/fraud_rules.yaml",
        "analytics/notebooks/fraud_analysis.ipynb", "analytics/notebooks/model_evaluation.ipynb"
    ]
    for f in analytics_files:
        open(f, 'a').close()
        
    # Infrastructure
    infra_dirs = [
        "infrastructure/helm/backend", "infrastructure/helm/frontend",
        "infrastructure/k8s-manifests",
        "infrastructure/fabric-network/organizations/Org1MSP", "infrastructure/fabric-network/organizations/Org2MSP"
    ]
    for d in infra_dirs:
        os.makedirs(d, exist_ok=True)
        
    infra_files = [
        "infrastructure/helm/backend/Chart.yaml", "infrastructure/helm/backend/values.yaml",
        "infrastructure/helm/frontend/Chart.yaml", "infrastructure/helm/frontend/values.yaml",
        "infrastructure/k8s-manifests/namespace.yaml", "infrastructure/k8s-manifests/keycloak.yaml", "infrastructure/k8s-manifests/postgres.yaml", "infrastructure/k8s-manifests/minio.yaml", "infrastructure/k8s-manifests/milvus.yaml", "infrastructure/k8s-manifests/monitoring.yaml", "infrastructure/k8s-manifests/ingress.yaml",
        "infrastructure/fabric-network/configtx.yaml", "infrastructure/fabric-network/crypto-config.yaml", "infrastructure/fabric-network/docker-compose.fabric.yml"
    ]
    for f in infra_files:
        open(f, 'a').close()
        
    # CI/CD
    cicd_dirs = [".github/workflows"]
    for d in cicd_dirs:
        os.makedirs(d, exist_ok=True)
        
    cicd_files = [
        ".github/workflows/backend-ci.yml", ".github/workflows/frontend-ci.yml", ".github/workflows/chaincode-ci.yml", ".github/workflows/deploy-staging.yml", ".github/workflows/deploy-prod.yml"
    ]
    for f in cicd_files:
        open(f, 'a').close()
        
    # Root Files
    root_files = ["README.md", ".gitignore", "CONTRIBUTING.md"]
    for f in root_files:
        open(f, 'a').close()
        
    print("")
    print("✅ NitiLedger workspace created successfully in Niti_Network!")
    print("")

if __name__ == '__main__':
    create_workspace()
