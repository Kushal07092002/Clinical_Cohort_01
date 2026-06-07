"""
Insights API Router
───────────────────
POST /api/insights/generate  — Generate AI insights for a cohort.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from agents.insight_agent import InsightAgent
from agents.cohort_agent import CohortAnalysisAgent
from agents.protocol_agent import ProtocolAgent
from utils.session_store import load_df
from models.schemas import InsightRequest, InsightResponse

router = APIRouter()
insight_agent = InsightAgent()
cohort_agent = CohortAnalysisAgent()
protocol_agent = ProtocolAgent()


@router.post("/generate", response_model=InsightResponse)
async def generate_insights(request: InsightRequest):
    """Generate AI-powered clinical insights and protocol analysis for the dataset / cohort."""
    df = load_df(request.session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found. Please upload data first.")

    cohort_name = request.cohort_name or "All Patients"
    
    # Run insights and protocol agents in parallel (or sequential for simplicity)
    insights_result = insight_agent.run(df, cohort_name)
    protocol_result = protocol_agent.run(df, cohort_name)

    return InsightResponse(
        insights=insights_result.get("insights", []),
        recommendations=insights_result.get("recommendations", []),
        risk_patients=insights_result.get("risk_patients", []),
        summary=insights_result.get("summary", ""),
        protocol_analysis=protocol_result
    )
