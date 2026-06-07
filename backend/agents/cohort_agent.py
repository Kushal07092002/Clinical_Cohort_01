"""
Cohort Analysis Agent
─────────────────────
Responsible for:
  • Filtering patients into cohorts by disease / age group / medication / outcome
  • Computing cohort-level statistics
  • Returning structured cohort data
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


AGE_GROUPS = {
    "child":  (0,  17),
    "adult":  (18, 59),
    "senior": (60, 120),
}


class CohortAnalysisAgent:
    """Agent that creates and analyses clinical cohorts."""

    name = "CohortAnalysisAgent"

    def run(
        self,
        df: pd.DataFrame,
        disease: Optional[str] = None,
        age_group: Optional[str] = None,
        medication: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Filter the DataFrame based on criteria and compute statistics.
        Returns a dict matching CohortResult schema.
        """
        filtered = df.copy()
        filters_applied: Dict[str, str] = {}

        # ── Apply filters ──────────────────────────────────────────────────────
        if disease and "disease" in filtered.columns:
            filtered = filtered[filtered["disease"].str.lower() == disease.lower()]
            filters_applied["disease"] = disease

        if age_group and age_group.lower() in AGE_GROUPS and "age" in filtered.columns:
            lo, hi = AGE_GROUPS[age_group.lower()]
            filtered = filtered[(filtered["age"] >= lo) & (filtered["age"] <= hi)]
            filters_applied["age_group"] = age_group

        if medication and "medication" in filtered.columns:
            filtered = filtered[
                filtered["medication"].str.lower() == medication.lower()
            ]
            filters_applied["medication"] = medication

        if outcome and "outcome" in filtered.columns:
            filtered = filtered[
                filtered["outcome"].str.lower() == outcome.lower()
            ]
            filters_applied["outcome"] = outcome

        # ── Cohort name ────────────────────────────────────────────────────────
        if filters_applied:
            cohort_name = " | ".join(
                f"{k}: {v}" for k, v in filters_applied.items()
            )
        else:
            cohort_name = "All Patients"

        # ── Statistics ─────────────────────────────────────────────────────────
        stats = self._compute_stats(filtered)

        # ── Add Risk Scoring to each patient ────────────────────────────────────
        patients_with_risk = []
        for p in filtered.to_dict(orient="records"):
            risk_info = self._calculate_risk_level(p)
            p.update(risk_info)
            patients_with_risk.append(p)

        return {
            "cohort_name": cohort_name,
            "filters_applied": filters_applied,
            "total_patients": len(filtered),
            "statistics": stats,
            "patients": patients_with_risk,
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _calculate_risk_level(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates a clinical risk score based on vitals and history."""
        score = 0
        factors = []
        
        # BMI Risk (> 30 is obese)
        bmi = patient.get("bmi")
        if bmi and bmi > 30:
            score += 2
            factors.append("Obesity")
        elif bmi and bmi > 25:
            score += 1
            factors.append("Overweight")
            
        # Blood Sugar Risk (> 140 is high)
        sugar = patient.get("blood_sugar")
        if sugar and sugar > 180:
            score += 3
            factors.append("Critically High Glucose")
        elif sugar and sugar > 140:
            score += 1
            factors.append("Elevated Glucose")
            
        # Age Risk (> 65)
        age = patient.get("age")
        if age and age > 75:
            score += 2
            factors.append("Advanced Age")
        elif age and age > 60:
            score += 1
            factors.append("Geriatric")

        # Outcome Risk
        outcome = str(patient.get("outcome", "")).lower()
        if outcome == "deteriorated":
            score += 3
            factors.append("Clinical Deterioration")
        
        # Smoking Risk
        if patient.get("smoking") == "Yes":
            score += 1
            factors.append("Smoker")

        # Level assignment
        if score >= 6:
            level = "Critical"
        elif score >= 4:
            level = "High"
        elif score >= 2:
            level = "Moderate"
        else:
            level = "Low"
            
        return {
            "risk_score": score,
            "risk_level": level,
            "risk_factors": factors
        }

    def _compute_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}

        stats: Dict[str, Any] = {}

        # Outcome distribution
        if "outcome" in df.columns:
            stats["outcome_distribution"] = (
                df["outcome"].value_counts().to_dict()
            )

        # Age stats
        if "age" in df.columns:
            stats["age"] = {
                "mean": round(float(df["age"].mean()), 1),
                "min":  int(df["age"].min()),
                "max":  int(df["age"].max()),
            }

        # Disease breakdown
        if "disease" in df.columns:
            stats["disease_distribution"] = (
                df["disease"].value_counts().to_dict()
            )

        # Medication breakdown
        if "medication" in df.columns:
            stats["medication_distribution"] = (
                df["medication"].value_counts().to_dict()
            )

        # BMI mean
        if "bmi" in df.columns:
            stats["avg_bmi"] = round(float(df["bmi"].mean()), 2)

        # Blood sugar mean
        if "blood_sugar" in df.columns:
            stats["avg_blood_sugar"] = round(float(df["blood_sugar"].mean()), 2)

        # Smoking %
        if "smoking" in df.columns:
            stats["smoking_rate_pct"] = round(
                float((df["smoking"] == "Yes").mean() * 100), 1
            )

        return stats

    # ── Convenience: age group breakdown ──────────────────────────────────────
    def group_by_age(self, df: pd.DataFrame) -> Dict[str, int]:
        counts = {group: 0 for group in AGE_GROUPS}
        if "age" not in df.columns:
            return counts
            
        for group, (lo, hi) in AGE_GROUPS.items():
            counts[group] = int(((df["age"] >= lo) & (df["age"] <= hi)).sum())
        return counts
