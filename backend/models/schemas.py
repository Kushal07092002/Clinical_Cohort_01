"""
Pydantic models / schemas for the Clinical Cohort AI System.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ─── Upload ────────────────────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    filename: Optional[str] = None
    session_id: str
    rows: int
    columns: List[str]
    missing_summary: Dict[str, int]
    message: str


# ─── Cleaning ─────────────────────────────────────────────────────────────────
class CleaningReport(BaseModel):
    original_rows: int
    cleaned_rows: int
    columns_fixed: List[str]
    strategies_used: Dict[str, str]
    missing_before: Dict[str, int]
    missing_after: Dict[str, int]


# ─── Cohort ───────────────────────────────────────────────────────────────────
class CohortFilter(BaseModel):
    session_id: str
    disease: Optional[str] = None
    age_group: Optional[str] = None      # "child", "adult", "senior"
    medication: Optional[str] = None
    outcome: Optional[str] = None


class CohortResult(BaseModel):
    cohort_name: str
    filters_applied: Dict[str, str]
    total_patients: int
    statistics: Dict[str, Any]
    patients: List[Dict[str, Any]]


# ─── Agent / Chat ─────────────────────────────────────────────────────────────
class QuestionRequest(BaseModel):
    session_id: str
    question: str


class AgentResponse(BaseModel):
    answer: str
    agent_used: str
    context_used: Dict[str, Any]
    sql_like_query: Optional[str] = None


# ─── Insights ─────────────────────────────────────────────────────────────────
class InsightRequest(BaseModel):
    session_id: str
    cohort_name: Optional[str] = None


class InsightResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]
    risk_patients: List[Dict[str, Any]]
    summary: str
    protocol_analysis: Optional[Dict[str, Any]] = None
