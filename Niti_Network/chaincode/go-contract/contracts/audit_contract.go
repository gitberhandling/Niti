package contracts

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
	"github.com/niti-ledger/go-contract/models"
)

// AuditContract manages the immutable audit trail on-chain.
// Rule: No update or delete functions are allowed.
type AuditContract struct {
	contractapi.Contract
}

// AppendAuditEntry writes a new audit record for any action. Immutable — cannot be overwritten.
func (c *AuditContract) AppendAuditEntry(
	ctx contractapi.TransactionContextInterface,
	actorID, action, entityID string,
) error {
	txID := ctx.GetStub().GetTxID()
	entry := models.AuditEntry{
		EntryID:    txID,
		ActorID:    actorID,
		Action:     action,
		EntityID:   entityID,
		EntityType: "Project",
		Timestamp:  time.Now().UTC(),
	}
	data, err := json.Marshal(entry)
	if err != nil {
		return fmt.Errorf("failed to marshal audit entry: %w", err)
	}
	auditKey := fmt.Sprintf("AUDIT_%s_%s", entityID, txID)
	return ctx.GetStub().PutState(auditKey, data)
}

// GetAuditTrail returns all audit entries for a given entity ID.
func (c *AuditContract) GetAuditTrail(
	ctx contractapi.TransactionContextInterface,
	entityID string,
) ([]*models.AuditEntry, error) {
	prefix := fmt.Sprintf("AUDIT_%s_", entityID)
	iterator, err := ctx.GetStub().GetStateByRange(prefix, prefix+"~")
	if err != nil {
		return nil, fmt.Errorf("failed to query audit trail: %w", err)
	}
	defer iterator.Close()

	var entries []*models.AuditEntry
	for iterator.HasNext() {
		result, err := iterator.Next()
		if err != nil {
			return nil, err
		}
		var entry models.AuditEntry
		if err := json.Unmarshal(result.Value, &entry); err != nil {
			continue
		}
		entries = append(entries, &entry)
	}
	return entries, nil
}
