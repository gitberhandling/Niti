"""
Isolation Forest anomaly detection for government project spending patterns.
Acts as a second-pass fraud classifier after rule-based detection (R001-R006).
"""
import numpy as np
import pandas as pd
import yaml
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional


class NitiIsolationForest:
    """
    Detects statistical outliers in project spending patterns.
    Trained on historical project features; outputs anomaly score.
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def _extract_features(self, projects: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Extract numerical features for Isolation Forest from project records.
        Features:
        - budget_utilisation: disbursed / totalBudget
        - milestone_count: number of milestones
        - completion_rate: % of milestones with status 'verified'
        - days_since_creation: age of project in days
        """
        rows = []
        for p in projects:
            milestones = p.get("milestones", [])
            total = len(milestones)
            verified = sum(1 for m in milestones if m.get("status") == "verified")
            budget = p.get("totalBudget", 1)
            disbursed = p.get("disbursed", 0)
            rows.append({
                "budget_utilisation": disbursed / max(budget, 1),
                "milestone_count": total,
                "completion_rate": verified / max(total, 1),
                "disbursed": disbursed,
                "total_budget": budget,
            })
        return pd.DataFrame(rows)

    def train(self, projects: List[Dict[str, Any]]) -> None:
        """Train the model on a list of project dicts."""
        X = self._extract_features(projects)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

    def predict(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return anomaly classification for a single project.
        Returns: {
            "is_anomaly": bool,
            "anomaly_score": float,  # negative = more anomalous
            "severity": "green" | "amber" | "red"
        }
        """
        if not self.is_trained:
            return {"is_anomaly": False, "anomaly_score": 0.0, "severity": "green"}

        X = self._extract_features([project])
        X_scaled = self.scaler.transform(X)
        score = float(self.model.score_samples(X_scaled)[0])
        prediction = self.model.predict(X_scaled)[0]  # -1 = anomaly, 1 = normal

        is_anomaly = prediction == -1
        severity = "green"
        if is_anomaly:
            severity = "red" if score < -0.6 else "amber"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "severity": severity,
        }
