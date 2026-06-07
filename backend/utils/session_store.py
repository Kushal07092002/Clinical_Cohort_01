"""
Session store — keeps DataFrames in memory keyed by session_id.
In production, replace with Redis or a database.
"""
import pandas as pd
from typing import Dict, Optional

# Global in-memory session store
_store: Dict[str, pd.DataFrame] = {}


def save_df(session_id: str, df: pd.DataFrame) -> None:
    """Persist a DataFrame for a session."""
    _store[session_id] = df.copy()


def load_df(session_id: str) -> Optional[pd.DataFrame]:
    """Retrieve a DataFrame by session ID."""
    return _store.get(session_id)


def delete_df(session_id: str) -> None:
    """Remove a session's DataFrame."""
    _store.pop(session_id, None)


def list_sessions() -> list:
    """Return all active session IDs."""
    return list(_store.keys())
