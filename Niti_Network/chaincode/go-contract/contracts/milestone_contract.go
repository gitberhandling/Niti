package contracts

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/niti-ledger/go-contract/models"
)

// MilestoneContract manages project milestones on-chain.
type MilestoneContract struct {
	contractapi.Contract
}

// AddMilestone adds a new milestone to an existing project.
func (c *MilestoneContract) AddMilestone(
	ctx contractapi.TransactionContextInterface,
	projectID, milestoneID, title string,
) error {
	projectContract := ProjectContract{}
	project, err := projectContract.GetProject(ctx, projectID)
	if err != nil {
		return err
	}

	// Check for duplicate milestone
	for _, m := range project.Milestones {
		if m.MilestoneID == milestoneID {
			return fmt.Errorf("milestone '%s' already exists in project '%s'", milestoneID, projectID)
		}
	}

	milestone := models.Milestone{
		MilestoneID:          milestoneID,
		ProjectID:            projectID,
		Title:                title,
		Status:               "pending",
		CompletionPercentage: 0,
		EvidenceHash:         "",
		VerifiedBy:           "",
		VerifiedAt:           time.Time{},
	}
	project.Milestones = append(project.Milestones, milestone)
	project.UpdatedAt = time.Now().UTC()

	data, err := json.Marshal(project)
	if err != nil {
		return fmt.Errorf("failed to marshal project with milestone: %w", err)
	}
	if err := ctx.GetStub().PutState(projectID, data); err != nil {
		return err
	}

	auditContract := AuditContract{}
	actorID, _ := ctx.GetClientIdentity().GetID()
	return auditContract.AppendAuditEntry(ctx, actorID, "AddMilestone:"+milestoneID, projectID)
}

// UpdateMilestoneStatus changes a milestone's status and records the verifier.
func (c *MilestoneContract) UpdateMilestoneStatus(
	ctx contractapi.TransactionContextInterface,
	milestoneID, status, verifiedBy string,
) error {
	// NOTE: In production a composite key would map milestoneID → projectID.
	// For Sprint 1, milestone is embedded in the project — requires scanning.
	// This is a known Sprint 2 optimisation.
	return fmt.Errorf("UpdateMilestoneStatus requires Sprint 2 composite key index — stub only")
}
