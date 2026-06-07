"""
Agent (QA) API Router
─────────────────────
POST /api/agent/ask  — Answer a natural language question about the data.
"""
from fastapi import APIRouter, HTTPException

from agents.qa_agent import QAAgent
from utils.session_store import load_df
from models.schemas import QuestionRequest, AgentResponse

router = APIRouter()
qa_agent = QAAgent()


@router.post("/ask", response_model=AgentResponse)
async def ask_question(request: QuestionRequest):
    """Ask a natural language question about the uploaded patient data."""
    df = load_df(request.session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found. Please upload data first.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = qa_agent.run(df, request.question)
    return AgentResponse(**result)
