package models

import "time"

// AuditEntry is an immutable on-chain audit record. Never update or delete.
type AuditEntry struct {
	EntryID    string    `json:"entryID"`
	ActorID    string    `json:"actorID"`
	Action     string    `json:"action"`
	EntityID   string    `json:"entityID"`
	EntityType string    `json:"entityType"`
	Timestamp  time.Time `json:"timestamp"`
}
