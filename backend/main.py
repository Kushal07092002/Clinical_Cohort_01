"""
Clinical Cohort AI System - Main FastAPI Application
Entry point for the backend server
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from api.upload import router as upload_router
from api.cohort import router as cohort_router
from api.agent import router as agent_router
from api.insights import router as insights_router

app = FastAPI(
    title="Clinical Cohort AI System",
    description="Agentic AI platform for clinical cohort analysis",
    version="1.0.0"
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://clinical-cohort-01-nd45.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─── Ensure upload directory exists ───────────────────────────────────────────
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(cohort_router, prefix="/api/cohort", tags=["Cohort"])
app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
app.include_router(insights_router, prefix="/api/insights", tags=["Insights"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Clinical Cohort AI System is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
