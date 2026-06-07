"""
Insight Generation Agent
────────────────────────
Uses OpenAI to generate clinical insights and recommendations
from cohort statistics and patient data.
"""
import os
import json
import pandas as pd
from openai import OpenAI
from typing import Dict, Any, List


class InsightAgent:
    """Agent that uses GPT to generate clinical insights from cohort data."""

    name = "InsightAgent"

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))

    def run(self, df: pd.DataFrame, cohort_name: str = "All Patients") -> Dict[str, Any]:
        """
        Generate insights, recommendations, and flag at-risk patients.
        Falls back to rule-based insights if no OpenAI key is configured.
        """
        # Compute summary stats to feed the model
        stats = self._summary_stats(df)
        risk_patients = self._flag_risk_patients(df)

        if self.client:
            return self._ai_insights(stats, cohort_name, risk_patients)
        else:
            return self._rule_based_insights(stats, cohort_name, risk_patients)

    # ── AI-powered insights ───────────────────────────────────────────────────

    def _ai_insights(
        self,
        stats: Dict[str, Any],
        cohort_name: str,
        risk_patients: List[Dict],
    ) -> Dict[str, Any]:
        prompt = f"""
You are a clinical data analyst AI. Analyse the following cohort statistics
for the cohort "{cohort_name}" and provide:
1. 5 key clinical insights (bullet points)
2. 4 actionable recommendations for clinicians (bullet points)
3. A 2-sentence executive summary

Cohort statistics (JSON):
{json.dumps(stats, indent=2)}

Number of at-risk patients flagged: {len(risk_patients)}

Return ONLY valid JSON in this format:
{{
  "insights": ["...", "...", "...", "...", "..."],
  "recommendations": ["...", "...", "...", "..."],
  "summary": "..."
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            data["risk_patients"] = risk_patients
            return data
        except Exception as e:
            return self._rule_based_insights(stats, cohort_name, risk_patients)

    # ── Rule-based fallback ───────────────────────────────────────────────────

    def _rule_based_insights(
        self,
        stats: Dict[str, Any],
        cohort_name: str,
        risk_patients: List[Dict],
    ) -> Dict[str, Any]:
        insights = [
            f"Cohort '{cohort_name}' contains {stats.get('total_patients', 0)} patients.",
            f"Average age: {stats.get('avg_age', 'N/A')} years.",
            f"Most common disease: {stats.get('top_disease', 'N/A')}.",
            f"Most common outcome: {stats.get('top_outcome', 'N/A')}.",
            f"Smoking rate: {stats.get('smoking_pct', 0):.1f}% of cohort.",
        ]
        recommendations = [
            "Review high-risk patients with multiple comorbidities.",
            "Consider medication adherence programs for deteriorating patients.",
            "Increase follow-up frequency for senior patients.",
            "Monitor blood sugar and BMI trends across the cohort.",
        ]
        summary = (
            f"The {cohort_name} cohort shows diverse health profiles. "
            "Targeted interventions are recommended for at-risk subgroups."
        )
        return {
            "insights": insights,
            "recommendations": recommendations,
            "summary": summary,
            "risk_patients": risk_patients,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"total_patients": len(df)}
        if "age" in df.columns:
            stats["avg_age"] = round(float(df["age"].mean()), 1)
        if "disease" in df.columns:
            vc = df["disease"].value_counts()
            stats["top_disease"] = vc.index[0] if not vc.empty else "N/A"
            stats["disease_counts"] = vc.to_dict()
        if "outcome" in df.columns:
            vc = df["outcome"].value_counts()
            stats["top_outcome"] = vc.index[0] if not vc.empty else "N/A"
            stats["outcome_counts"] = vc.to_dict()
        if "smoking" in df.columns:
            stats["smoking_pct"] = float((df["smoking"] == "Yes").mean() * 100)
        if "bmi" in df.columns:
            stats["avg_bmi"] = round(float(df["bmi"].mean()), 2)
        if "blood_sugar" in df.columns:
            stats["avg_blood_sugar"] = round(float(df["blood_sugar"].mean()), 2)
        return stats

    def _flag_risk_patients(self, df: pd.DataFrame) -> List[Dict]:
        """Simple rule-based risk flagging."""
        risk = df.copy()
        conditions = pd.Series([False] * len(risk), index=risk.index)

        if "bmi" in risk.columns:
            conditions |= risk["bmi"] > 30
        if "blood_sugar" in risk.columns:
            conditions |= risk["blood_sugar"] > 150
        if "age" in risk.columns:
            conditions |= risk["age"] > 70
        if "outcome" in risk.columns:
            conditions |= risk["outcome"].str.lower() == "deteriorated"

        risky = risk[conditions]
        cols = [c for c in ["patient_id", "age", "disease", "outcome", "bmi", "blood_sugar"] if c in risky.columns]
        return risky[cols].head(10).to_dict(orient="records")
