"""
Upload API Router
─────────────────
POST /api/upload/  — Accept CSV, run cleaning agent, store in session.
GET  /api/upload/sessions — List active sessions.
GET  /api/upload/sample   — Load the bundled sample dataset.
"""
import io
import os
import uuid
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from agents.cleaning_agent import DataCleaningAgent
from utils.session_store import save_df, load_df, list_sessions
from models.schemas import UploadResponse

router = APIRouter()
cleaner = DataCleaningAgent()

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_patients.csv")


@router.post("/", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload a patient CSV, auto-clean it, and return a session_id."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    # Run cleaning agent
    df_clean, report = cleaner.run(df)

    session_id = str(uuid.uuid4())
    save_df(session_id, df_clean)

    return UploadResponse(
        filename=file.filename,
        session_id=session_id,
        rows=len(df_clean),
        columns=list(df_clean.columns),
        missing_summary=report["missing_before"],
        message=f"File uploaded and cleaned. {report['original_rows']} rows processed.",
    )


@router.get("/sample", response_model=UploadResponse)
async def load_sample():
    """Load the built-in sample dataset."""
    try:
        df = pd.read_csv(SAMPLE_PATH)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample dataset not found.")

    df_clean, report = cleaner.run(df)
    session_id = str(uuid.uuid4())
    save_df(session_id, df_clean)

    return UploadResponse(
        filename="sample_patients.csv",
        session_id=session_id,
        rows=len(df_clean),
        columns=list(df_clean.columns),
        missing_summary=report["missing_before"],
        message="Sample dataset loaded and cleaned successfully.",
    )


@router.get("/sessions")
async def get_sessions():
    """Return all active session IDs."""
    return {"sessions": list_sessions()}
