# Clinical Cohort AI System: Technical Report

## 1. Project Overview
The Clinical Cohort AI System is an **Agentic AI platform** designed to automate the lifecycle of clinical data analysis. It takes raw, messy clinical datasets (CSV) and transforms them into cleaned, structured, and insightful cohorts using a multi-agent architecture.

## 2. System Architecture
The system follows a **Decoupled Client-Server Architecture**:
*   **Backend:** Built with **FastAPI (Python)**. It acts as the "brain," hosting the AI agents and managing session-based data storage.
*   **Frontend:** Built with **React (TypeScript)** and **Tailwind CSS**. It provides a professional, high-fidelity interface for clinicians to interact with the data.

## 3. The Data Pipeline
The system processes data in four distinct phases:
1.  **Ingestion:** User uploads a CSV file.
2.  **Autonomous Cleaning:** The `DataCleaningAgent` identifies missing values and applies statistical imputation.
3.  **Session Persistence:** Cleaned data is stored in a temporary session store (memory-based).
4.  **Risk Stratification:** The `CohortAnalysisAgent` computes clinical risk scores for each patient.
5.  **Cohort Generation & Protocol Validation:** The system filters data and validates it against medical standards via the `ProtocolAgent`.

---

## 4. Core Components & Agentic Principles

### A. Data Cleaning Agent (`DataCleaningAgent`)
*   **Principle:** Statistical Imputation.
*   **Working:** It scans every column. If it finds a missing value:
    *   **Numeric Columns:** It fills the gap with the **Median**. Median is used because it is robust to outliers (extremely high/low values) which are common in clinical data.
    *   **Categorical Columns:** It fills the gap with the **Mode** (the most frequent value).
*   **Output:** A cleaned DataFrame and a "Cleaning Report" showing exactly what changed.

### B. Cohort Analysis Agent (`CohortAnalysisAgent`)
*   **Principle:** Structured Filtering & Clinical Risk Stratification.
*   **Working:** This agent takes user-defined filters and performs an optimized slice of the dataset while calculating individual patient risk.
*   **Logic:** 
    *   It applies a multi-step filter using Pandas.
    *   **Risk Scoring:** It evaluates factors like Age (>75), BMI (>30), and Blood Sugar (>140) to assign a "Risk Level" (Critical to Low).
    *   It calculates the **Population Distribution** and **Mean Biological Markers**.

### C. Protocol Validation Agent (`ProtocolAgent`) - **NEW**
*   **Principle:** Autonomous Guideline Alignment.
*   **Working:** Evaluates if the cohort's treatment/outcomes align with standard clinical protocols.
*   **Logic:** 
    *   Identifies clinical deviations and outliers.
    *   Generates an **Alignment Score** (0-100%).
    *   Suggests a specific research hypothesis for the cohort.

### D. Natural Language Agent (`QAAgent`)
*   **Principle:** Large Language Model (LLM) + Context Injection.
*   **Working:** When a user asks a question like "What is the average age of diabetic patients?", the system:
    1.  Summarizes the dataset into a "Context String."
    2.  Sends the context + the question to **GPT-4o-mini**.
    3.  The AI acts as a "Data Scientist" and returns a natural language answer.
*   **Fallback:** If no API key is present, it uses a **Rule-based Keyword Matcher** to answer basic questions.

---

## 5. Input / Output Specifications

### Inputs:
*   **Clinical Dataset (CSV):** Must contain columns like `age`, `disease`, `medication`, and `outcome`.
*   **Filter Parameters:** User-selected strings (e.g., "Diabetes", "Metformin").

### Outputs:
*   **Cleaned Data Summary:** Count of rows processed and columns fixed.
*   **Cohort Statistics:** Total population, average age, mean BMI, and disease distributions.
*   **Clinical Preview:** A refined table showing individual patient records matching the cohort.

---

# Annotated Source Code

### Backend: Cleaning Agent (`backend/agents/cleaning_agent.py`)
```python
\"\"\"
This agent is the 'First Responder' for raw data.
It ensures that the dataset is clinically valid by filling in gaps.
\"\"\"
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class DataCleaningAgent:
    # We define specific columns that we expect to be numbers
    NUMERIC_COLS = ["age", "dosage_mg", "blood_sugar", "bmi"]

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        # 1. Create a copy to avoid modifying the original data
        df = df.copy()
        
        # 2. Iterate through every column in the dataset
        for col in df.columns:
            n_missing = df[col].isnull().sum()
            if n_missing == 0: continue # Skip if no missing data

            # 3. Apply Imputation Strategy
            if col in self.NUMERIC_COLS:
                # Use Median: Robust to outliers in medical readings
                fill_val = df[col].median()
                df[col] = df[col].fillna(fill_val)
            else:
                # Use Mode: Most frequent category (e.g., most common disease)
                mode_vals = df[col].mode()
                fill_val = mode_vals[0] if not mode_vals.empty else "Unknown"
                df[col] = df[col].fillna(fill_val)

        return df, {"status": "cleaned"}
```

### Frontend: Cohort Logic (`frontend/src/components/CohortAnalysis.tsx`)
```typescript
/**
 * This component is the main Dashboard.
 * It manages the 'State' of the filters and the 'Results' of the analysis.
 */
const CohortAnalysis: React.FC<{ sessionId: string }> = ({ sessionId }) => {
  // State Hooks: React uses these to remember what the user has selected
  const [selectedDisease, setSelectedDisease] = useState('');
  const [cohortResult, setCohortResult] = useState<any>(null);

  // Effect Hook: Runs automatically when the component loads
  useEffect(() => {
    // Fetches the unique diseases/medications from the backend
    // so the dropdown menus are always accurate to the uploaded file.
    fetchFilters(); 
  }, [sessionId]);

  // Handler: Triggered when user clicks 'Filter'
  const handleCreateCohort = async () => {
    // 1. Send the filter criteria to the Backend API
    const response = await fetch('/api/cohort/create', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, disease: selectedDisease })
    });
    
    // 2. Receive the computed statistics and update the UI
    const data = await response.json();
    setCohortResult(data);
  };

  return (
    // The UI is built using 'Tailwind CSS' for a clean, minimalist look.
    // It conditionally renders the results only after 'cohortResult' is populated.
    <div>{/* Filter UI */}</div>
  );
};
```

### Backend: Main API Entry (`backend/main.py`)
```python
\"\"\"
The FastAPI server. It acts as the gateway between 
the Frontend (React) and the Python Logic (Pandas/AI Agents).
\"\"\"
app = FastAPI()

# Middleware: Allows the Frontend (port 5173) to talk to the Backend (port 8000)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Router: Directs '/api/upload' requests to the Upload Logic
app.include_router(upload_router, prefix="/api/upload")
```
