package contracts

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// DocumentRecord represents an on-chain anchored document hash.
type DocumentRecord struct {
	DocumentID  string    `json:"documentID"`
	ProjectID   string    `json:"projectID"`
	SHA256Hash  string    `json:"sha256Hash"`
	AnchoredAt  time.Time `json:"anchoredAt"`
	AnchoredBy  string    `json:"anchoredBy"`
}

// DocumentContract manages document hash anchoring on-chain.
// Documents go to MinIO first; ONLY the SHA-256 hash goes on-chain.
type DocumentContract struct {
	contractapi.Contract
}

// AnchorDocumentHash writes a document's SHA-256 hash to the ledger.
func (c *DocumentContract) AnchorDocumentHash(
	ctx contractapi.TransactionContextInterface,
	documentID, projectID, sha256Hash string,
) error {
	actorID, _ := ctx.GetClientIdentity().GetID()

	record := DocumentRecord{
		DocumentID: documentID,
		ProjectID:  projectID,
		SHA256Hash: sha256Hash,
		AnchoredAt: time.Now().UTC(),
		AnchoredBy: actorID,
	}
	data, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal document record: %w", err)
	}
	key := fmt.Sprintf("DOC_%s", documentID)
	if err := ctx.GetStub().PutState(key, data); err != nil {
		return fmt.Errorf("failed to anchor hash: %w", err)
	}

	auditContract := AuditContract{}
	return auditContract.AppendAuditEntry(ctx, actorID, "AnchorDocumentHash", documentID)
}

// VerifyDocumentHash checks whether the provided hash matches the on-chain record.
func (c *DocumentContract) VerifyDocumentHash(
	ctx contractapi.TransactionContextInterface,
	documentID, sha256Hash string,
) (bool, error) {
	key := fmt.Sprintf("DOC_%s", documentID)
	data, err := ctx.GetStub().GetState(key)
	if err != nil {
		return false, fmt.Errorf("failed to read world state: %w", err)
	}
	if data == nil {
		return false, fmt.Errorf("document '%s' not found on-chain", documentID)
	}
	var record DocumentRecord
	if err := json.Unmarshal(data, &record); err != nil {
		return false, fmt.Errorf("failed to unmarshal document record: %w", err)
	}
	return record.SHA256Hash == sha256Hash, nil
}
