"""
Cohort API Router
─────────────────
POST /api/cohort/create   — Build a cohort with optional filters.
GET  /api/cohort/diseases — List unique diseases in the dataset.
GET  /api/cohort/age-groups/{session_id} — Count patients per age group.
"""
from fastapi import APIRouter, HTTPException

from agents.cohort_agent import CohortAnalysisAgent
from utils.session_store import load_df
from models.schemas import CohortFilter, CohortResult

router = APIRouter()
cohort_agent = CohortAnalysisAgent()


@router.post("/create", response_model=CohortResult)
async def create_cohort(filters: CohortFilter):
    """Create a patient cohort based on the supplied filters."""
    df = load_df(filters.session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found. Please upload data first.")

    result = cohort_agent.run(
        df=df,
        disease=filters.disease,
        age_group=filters.age_group,
        medication=filters.medication,
        outcome=filters.outcome,
    )

    if result["total_patients"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No patients match the specified filters."
        )

    return result


@router.get("/diseases/{session_id}")
async def get_diseases(session_id: str):
    """List all unique disease values in the uploaded dataset."""
    df = load_df(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if "disease" not in df.columns:
        return {"diseases": []}

    diseases = sorted(df["disease"].dropna().unique().tolist())
    return {"diseases": diseases}


@router.get("/medications/{session_id}")
async def get_medications(session_id: str):
    """List all unique medications in the uploaded dataset."""
    df = load_df(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if "medication" not in df.columns:
        return {"medications": []}

    meds = sorted(df["medication"].dropna().unique().tolist())
    return {"medications": meds}


@router.get("/outcomes/{session_id}")
async def get_outcomes(session_id: str):
    """List all unique outcomes in the uploaded dataset."""
    df = load_df(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if "outcome" not in df.columns:
        return {"outcomes": []}

    outcomes = sorted(df["outcome"].dropna().unique().tolist())
    return {"outcomes": outcomes}


@router.get("/age-groups/{session_id}")
async def get_age_groups(session_id: str):
    """Return patient counts by age group."""
    df = load_df(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    groups = cohort_agent.group_by_age(df)
    return {"age_groups": groups}


@router.get("/summary/{session_id}")
async def get_summary(session_id: str):
    """Full dataset overview — all cohorts combined."""
    df = load_df(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    result = cohort_agent.run(df)
    return result
