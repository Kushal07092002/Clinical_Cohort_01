"""
Natural Language Q&A Agent
──────────────────────────
Allows users to ask plain-English questions about their dataset.
Uses OpenAI with dataset context. Falls back to keyword matching.
"""
import os
import json
import pandas as pd
from openai import OpenAI
from typing import Dict, Any


class QAAgent:
    """Agent that answers natural language questions about clinical data."""

    name = "QAAgent"

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def run(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Answer a natural language question about the dataset."""
        context = self._build_context(df)

        if self.client:
            return self._ai_answer(df, question, context)
        else:
            return self._keyword_answer(df, question, context)

    # ── AI-powered answer ─────────────────────────────────────────────────────

    def _ai_answer(
        self, df: pd.DataFrame, question: str, context: str
    ) -> Dict[str, Any]:
        # Provide a sample of the data to give the AI a "feel" for the records
        sample_data = df.head(15).to_json(orient="records")
        summary_stats = df.describe(include='all').to_json()

        prompt = f"""
You are a Clinical Data Analyst AI. Answer the user's question based on the provided dataset context, summary statistics, and sample records.

### Dataset Context:
{context}

### Summary Statistics:
{summary_stats}

### Sample Records (Top 15):
{sample_data}

### User Question:
"{question}"

### Requirements:
1. Provide a natural, detailed, and clinical answer.
2. If the user asks for feedback, insights, or opinions, provide them based on the patterns seen in the data.
3. If the user asks for specific values (like age of a person with diabetes), use the provided context and statistics to give the most accurate answer possible.
4. Be professional and factual.

Return JSON:
{{
  "answer": "...",
  "sql_like_query": "...",
  "confidence": "high|medium|low"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical data assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            return {
                "answer": data.get("answer", "I could not analyze the data for an answer."),
                "agent_used": self.name,
                "context_used": {"dataset_rows": len(df)},
                "sql_like_query": data.get("sql_like_query"),
            }
        except Exception as e:
            return self._keyword_answer(df, question, context)

    # ── Keyword fallback ──────────────────────────────────────────────────────

    def _keyword_answer(
        self, df: pd.DataFrame, question: str, context: str
    ) -> Dict[str, Any]:
        q = question.lower()
        answer = "I'm not sure. Please ask about disease counts, outcomes, age, medication, or BMI."

        if "how many" in q and "patient" in q:
            answer = f"The dataset contains {len(df)} patients."
        elif ("average age" in q or "mean age" in q) and "age" in df.columns:
            answer = f"The average patient age is {df['age'].mean():.1f} years."
        elif "age" in q and "diabet" in q and "disease" in df.columns and "age" in df.columns:
            subset = df[df["disease"].str.lower().str.contains("diabet")]
            if not subset.empty:
                avg_age = subset["age"].mean()
                answer = f"The average age of patients with Diabetes is {avg_age:.1f} years. There are {len(subset)} such patients."
            else:
                answer = "I couldn't find any patients with Diabetes in the dataset."
        elif "disease" in q and ("most" in q or "common" in q) and "disease" in df.columns:
            top = df["disease"].value_counts().idxmax()
            answer = f"The most common disease is {top}."
        elif "outcome" in q and ("most" in q or "common" in q) and "outcome" in df.columns:
            top = df["outcome"].value_counts().idxmax()
            answer = f"The most common outcome is {top}."
        elif "deteriorat" in q and "outcome" in df.columns:
            n = (df["outcome"].str.lower() == "deteriorated").sum()
            answer = f"{n} patients showed a deteriorated outcome."
        elif "improved" in q and "outcome" in df.columns:
            n = (df["outcome"].str.lower() == "improved").sum()
            answer = f"{n} patients showed improvement."
        elif "smok" in q and "smoking" in df.columns:
            pct = (df["smoking"] == "Yes").mean() * 100
            answer = f"{pct:.1f}% of patients are smokers."
        elif "bmi" in q and "bmi" in df.columns:
            answer = f"The average BMI is {df['bmi'].mean():.2f}."
        elif ("medication" in q or "drug" in q) and "medication" in df.columns:
            top = df["medication"].value_counts().idxmax()
            answer = f"The most prescribed medication is {top}."
        elif ("senior" in q or "elderly" in q or "old" in q) and "age" in df.columns:
            n = (df["age"] >= 60).sum()
            answer = f"There are {n} senior patients (age ≥ 60)."
        elif "diabet" in q and "disease" in df.columns:
            n = (df["disease"].str.lower().str.contains("diabet")).sum()
            answer = f"There are {n} patients with Diabetes."
        elif "hypertension" in q and "disease" in df.columns:
            n = (df["disease"].str.lower() == "hypertension").sum()
            answer = f"There are {n} patients with Hypertension."

        return {
            "answer": answer,
            "agent_used": self.name + " (rule-based)",
            "context_used": {"dataset_rows": len(df)},
            "sql_like_query": None,
        }

    # ── Context builder ───────────────────────────────────────────────────────

    def _build_context(self, df: pd.DataFrame) -> str:
        lines = [
            f"Total patients: {len(df)}",
            f"Columns: {list(df.columns)}",
        ]
        for col in ["disease", "outcome", "medication", "gender"]:
            if col in df.columns:
                vc = df[col].value_counts().head(5).to_dict()
                lines.append(f"{col} distribution: {vc}")
        for col in ["age", "bmi", "blood_sugar", "cholesterol"]:
            if col in df.columns:
                lines.append(
                    f"{col}: mean={df[col].mean():.1f}, "
                    f"min={df[col].min()}, max={df[col].max()}"
                )
        return "\n".join(lines)
