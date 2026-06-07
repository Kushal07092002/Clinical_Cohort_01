# Sessional 1 Report: Project Ideation and Proposal

## 1. Introduction
The process of patient recruitment and cohort selection for clinical trials is one of the most critical, yet historically time-consuming and error-prone bottlenecks in modern medical research. According to industry statistics, nearly 80% of all clinical trials fail to recruit the required patient cohorts within their allotted timeframe. These delays not only lead to extended research periods but also result in significant financial losses for pharmaceutical companies and research institutions. The root of this challenge lies in the manual screening of vast amounts of electronic health records (EHRs) to painstakingly match patients against strict, complex eligibility criteria.

For the final project of the MTech in Data Science program, our team proposed the conceptualization and development of a **Clinical Cohort AI System**. The overarching objective of this project is to automate the lifecycle of clinical data analysis. By transforming raw, unstructured clinical datasets into meticulously structured, insightful cohorts using modern machine learning and artificial intelligence techniques, we aim to drastically reduce the time and resources required for patient screening.

## 2. Understanding Clinical Cohorts
A fundamental concept driving this project is the "clinical cohort." Before designing the AI system, it is imperative to understand what a clinical cohort is, its primary uses, and the distinct advantages it brings to clinical research.

### 2.1. Definition and Uses
A clinical cohort is a group of subjects (patients) who share a defining characteristic or experience within a specified period. In clinical research, cohorts are established to observe the effects of a specific treatment, understand the progression of a disease, or evaluate the impact of various risk factors over time. 
The primary uses of clinical cohorts include:
- **Observational Studies**: Tracking patients over years to see how lifestyle choices or chronic conditions (like Diabetes or Cardiovascular Disease) impact long-term health.
- **Trial Eligibility (Pre-screening)**: Identifying a precise subgroup of patients who strictly meet the inclusion and exclusion criteria for a new experimental drug or therapy.
- **Risk Stratification**: Grouping patients based on their physiological markers to determine who is at the highest risk of adverse outcomes, thereby prioritizing them for aggressive treatment protocols.

### 2.2. Advantages of Cohort Analysis
Analyzing well-defined clinical cohorts provides several unparalleled advantages in medical research:
- **High Temporal Clarity**: Because cohorts track patients based on specific timelines or exposures, researchers can clearly establish the sequence of events (e.g., proving that a specific medication was taken *before* the onset of a side effect).
- **Multiple Outcomes**: A single cohort can be used to study multiple disease outcomes simultaneously. For instance, a cohort of patients with high BMI can be evaluated for risks of both diabetes and heart disease.
- **Real-World Evidence**: Unlike highly controlled randomized clinical trials, cohort analysis often utilizes real-world electronic health records, providing insights into how treatments perform in standard clinical practice across diverse demographic populations.
- **Statistical Power**: By grouping patients with similar characteristics, researchers reduce confounding variables and increase the statistical power and validity of their findings.

## 3. Literature Review
During the initial phase of our MTech project, we conducted a rigorous literature review to understand the current technological landscape of clinical cohort selection. We primarily focused on three key areas of contemporary research:

1. **LLM-Assisted Clinical Trial Recruitment**: We studied recent surveys highlighting a paradigm shift toward utilizing Large Language Models (LLMs) for matching patients to clinical trials. Traditional methods rely on rigid, rule-based heuristics, which often fail to capture the nuanced reasoning required to interpret complex, natural language eligibility criteria. LLMs, with their vast parameter space, offer highly promising capabilities in knowledge aggregation and contextual reasoning. However, the literature also warns of challenges such as stringent data privacy laws (e.g., HIPAA) and the risk of AI hallucination in critical medical settings.
2. **Multiple Instance Learning (MIL) for Cohort Selection**: We explored academic studies that formulate cohort selection mathematically as a Multiple Instance Learning problem. A single patient often has multiple, unstructured longitudinal records spanning several years. MIL algorithms (such as Multi-Instance Support Vector Machines) can classify a patient as eligible if at least one record (or a combination thereof) within their "bag" of records satisfies the required clinical criteria. This research highlighted the inherent complexity of dealing with unstructured clinical narratives.
3. **Clinical Trial Design Optimization**: We reviewed optimization algorithms used in early-stage (Phase I) cancer clinical trials. These papers detailed how mathematical and statistical models are used to determine the maximum tolerated dose (MTD) and how they improve upon traditional 3+3 trial designs by dynamically adjusting patient cohorts based on real-time toxicity responses.

## 4. Proposed Idea and System Architecture
Drawing profound insights from the literature, we concluded that while traditional NLP and statistical MIL methods are effective baselines, the recent advent of Generative AI and "Agentic" workflows provides a unique opportunity to build a more flexible, intelligent, and interactive system. 

We proposed building a state-of-the-art decoupled client-server architecture:
- **The Frontend (Client Interface)**: A highly interactive, aesthetically pleasing web dashboard built with React and TailwindCSS. It will serve as the primary portal for clinicians to upload datasets, select filtering criteria, and visually explore the generated cohorts.
- **The Backend (The AI "Brain")**: A FastAPI-based server hosting multiple autonomous AI agents. Rather than writing a monolithic, procedural codebase, we planned to divide the system's logic into specialized, decoupled agents (e.g., a Data Cleaning Agent, a Cohort Analysis Agent, an Insight Agent). Each agent will have a singular responsibility, mimicking a team of specialized medical researchers working in tandem.

## 5. Objectives for the Next Phase
Moving into Sessional 2, our primary objectives are:
1. To set up the foundational frontend and backend infrastructure, ensuring seamless API communication.
2. To develop the data ingestion module and the autonomous statistical data cleaning pipelines.
3. To implement the core deterministic logic for patient filtering and clinical risk stratification before introducing the more complex Generative LLMs.
