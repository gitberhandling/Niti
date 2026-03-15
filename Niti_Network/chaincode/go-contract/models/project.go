package models

import "time"

// Project represents a government project stored on-chain.
type Project struct {
	ProjectID   string      `json:"projectID"`
	Name        string      `json:"name"`
	Department  string      `json:"department"`
	Status      string      `json:"status"`      // active | closed
	TotalBudget float64     `json:"totalBudget"`
	Disbursed   float64     `json:"disbursed"`
	CreatedAt   time.Time   `json:"createdAt"`
	UpdatedAt   time.Time   `json:"updatedAt"`
	Milestones  []Milestone `json:"milestones"`
}

// Milestone represents a verifiable project deliverable stored on-chain.
type Milestone struct {
	MilestoneID          string    `json:"milestoneID"`
	ProjectID            string    `json:"projectID"`
	Title                string    `json:"title"`
	Status               string    `json:"status"`               // pending | verified | rejected
	CompletionPercentage int       `json:"completionPercentage"`
	EvidenceHash         string    `json:"evidenceHash"`         // SHA-256 of uploaded document
	VerifiedBy           string    `json:"verifiedBy"`
	VerifiedAt           time.Time `json:"verifiedAt"`
}
