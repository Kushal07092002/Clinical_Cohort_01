"""
Data Cleaning Agent
───────────────────
Responsible for:
  • Detecting missing values
  • Applying smart fill strategies (median for numeric, mode for categorical)
  • Generating a human-readable cleaning report
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


class DataCleaningAgent:
    """Agent that automatically cleans a clinical patient DataFrame."""

    name = "DataCleaningAgent"

    # Columns we know are numeric
    NUMERIC_COLS = [
        "age", "dosage_mg", "treatment_duration_days",
        "blood_sugar", "cholesterol", "bmi",
    ]

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Clean the DataFrame and return (cleaned_df, report).
        """
        original_rows = len(df)
        missing_before = df.isnull().sum().to_dict()
        strategies: Dict[str, str] = {}
        columns_fixed: list = []

        df = df.copy()

        for col in df.columns:
            n_missing = df[col].isnull().sum()
            if n_missing == 0:
                continue

            columns_fixed.append(col)

            if col in self.NUMERIC_COLS or df[col].dtype in [np.float64, np.int64]:
                # Use median for numeric columns – robust to outliers
                fill_val = df[col].median()
                df[col] = df[col].fillna(fill_val)
                strategies[col] = f"filled with median ({fill_val:.2f})"

            else:
                # Use mode (most frequent value) for categorical columns
                mode_vals = df[col].mode()
                fill_val = mode_vals[0] if not mode_vals.empty else "Unknown"
                df[col] = df[col].fillna(fill_val)
                strategies[col] = f"filled with mode ('{fill_val}')"

        # Drop any remaining rows that couldn't be filled (edge case)
        df.dropna(inplace=True)
        missing_after = df.isnull().sum().to_dict()

        report = {
            "original_rows": original_rows,
            "cleaned_rows": len(df),
            "columns_fixed": columns_fixed,
            "strategies_used": strategies,
            "missing_before": {k: int(v) for k, v in missing_before.items()},
            "missing_after": {k: int(v) for k, v in missing_after.items()},
        }

        return df, report
