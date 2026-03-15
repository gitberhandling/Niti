package contracts

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/niti-ledger/go-contract/models"
)

// ProjectContract manages government projects on-chain.
type ProjectContract struct {
	contractapi.Contract
}

// CreateProject creates a new government project on the ledger.
// Requires: caller must be Org1MSP or Org2MSP peer.
func (c *ProjectContract) CreateProject(
	ctx contractapi.TransactionContextInterface,
	projectID, name, department, budget string,
) error {
	// Validate caller MSP
	mspID, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		return fmt.Errorf("failed to get MSP ID: %w", err)
	}
	if mspID != "Org1MSP" && mspID != "Org2MSP" {
		return fmt.Errorf("unauthorized MSP: %s", mspID)
	}

	// Check for duplicate
	existing, err := ctx.GetStub().GetState(projectID)
	if err != nil {
		return fmt.Errorf("failed to read world state: %w", err)
	}
	if existing != nil {
		return fmt.Errorf("project '%s' already exists", projectID)
	}

	var budgetF float64
	fmt.Sscanf(budget, "%f", &budgetF)

	project := models.Project{
		ProjectID:   projectID,
		Name:        name,
		Department:  department,
		Status:      "active",
		TotalBudget: budgetF,
		Disbursed:   0,
		CreatedAt:   time.Now().UTC(),
		UpdatedAt:   time.Now().UTC(),
		Milestones:  []models.Milestone{},
	}

	data, err := json.Marshal(project)
	if err != nil {
		return fmt.Errorf("failed to marshal project: %w", err)
	}

	if err := ctx.GetStub().PutState(projectID, data); err != nil {
		return fmt.Errorf("failed to write to world state: %w", err)
	}

	// Write audit entry
	auditContract := AuditContract{}
	actorID, _ := ctx.GetClientIdentity().GetID()
	return auditContract.AppendAuditEntry(ctx, actorID, "CreateProject", projectID)
}

// GetProject retrieves a project from the ledger.
func (c *ProjectContract) GetProject(
	ctx contractapi.TransactionContextInterface,
	projectID string,
) (*models.Project, error) {
	data, err := ctx.GetStub().GetState(projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to read world state: %w", err)
	}
	if data == nil {
		return nil, fmt.Errorf("project '%s' not found", projectID)
	}
	var project models.Project
	if err := json.Unmarshal(data, &project); err != nil {
		return nil, fmt.Errorf("failed to unmarshal project: %w", err)
	}
	return &project, nil
}

// UpdateProjectStatus changes a project's status (active | closed).
func (c *ProjectContract) UpdateProjectStatus(
	ctx contractapi.TransactionContextInterface,
	projectID, status string,
) error {
	project, err := c.GetProject(ctx, projectID)
	if err != nil {
		return err
	}
	project.Status = status
	project.UpdatedAt = time.Now().UTC()

	data, err := json.Marshal(project)
	if err != nil {
		return fmt.Errorf("failed to marshal updated project: %w", err)
	}
	if err := ctx.GetStub().PutState(projectID, data); err != nil {
		return err
	}

	auditContract := AuditContract{}
	actorID, _ := ctx.GetClientIdentity().GetID()
	return auditContract.AppendAuditEntry(ctx, actorID, "UpdateProjectStatus:"+status, projectID)
}

// ListProjects returns all projects stored in the world state.
func (c *ProjectContract) ListProjects(
	ctx contractapi.TransactionContextInterface,
) ([]*models.Project, error) {
	iterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer iterator.Close()

	var projects []*models.Project
	for iterator.HasNext() {
		result, err := iterator.Next()
		if err != nil {
			return nil, err
		}
		var p models.Project
		if err := json.Unmarshal(result.Value, &p); err != nil {
			continue // skip non-project entries
		}
		if p.ProjectID != "" {
			projects = append(projects, &p)
		}
	}
	return projects, nil
}
