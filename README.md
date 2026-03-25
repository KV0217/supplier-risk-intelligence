# 📊 Supplier Risk Intelligence System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)

> **An enterprise-grade, end-to-end Machine Learning pipeline that continuously monitors multi-modal data streams (Financial Market Data & News RSS feeds) to generate predictive early-warning risk scores for global hardware and semiconductor supply chains.**

In modern supply chain management, operational delays and vendor distres are lagging indicators. By the time a vendor misses a shipment, the critical window for mitigation has closed. This system shifts the paradigm from **reactive** to **predictive** by mathematically quantifying external market behaviors and news sentiment *before* they appear in internal ERP systems.

---

## 🏗️ System Architecture

The project is built around a robust ETL pipeline, a context-aware NLP engine, and an AutoML ensemble tournament.

```mermaid
flowchart LR
    subgraph ETL Data Ingestion
        RSS[📰 Google News RSS] --> News[Unstructured Text]
        API[📈 Market API Waterfall] --> Fin[Structured OHLCV]
    end

    subgraph Feature Engineering
        News --> NLP[Contextual Sentiment & Negation]
        Fin --> Math[Volatility & Trend Position]
    end

    subgraph Scoring Engine
        NLP --> Rule[Domain Heuristics (30%)]
        Math --> Rule
        NLP --> ML[XGBoost / AutoML Winner (70%)]
        Math --> ML
        Rule --> Blend[Ensemble Risk Score 0-100]
        ML --> Blend
    end

    subgraph Presentation Layer
        Blend --> UI[💻 Streamlit Interactive Dashboard]
        Blend --> REST[🔌 FastAPI REST Service]
    end
```

---

## 🚀 Core Engineering Components

### 1. The ETL Pipeline & Resilience (`data_collector.py`)
Extracting consistent financial data from free endpoints is historically unreliable due to aggressive rate-limiting. This system implements a highly resilient, multi-tiered extraction strategy:
*   **The API Waterfall:** When requesting daily closing prices, the system attempts a primary endpoint (YFinance). If rate-limited, it automatically catches the exception and routes the request gracefully through a fallback chain (Stooq CSV → TwelveData → Alpha Vantage) to guarantee pipeline continuity without crashing.
*   **Targeted NLP Ingestion:** It uses targeted Google News RSS queries to guarantee high-fidelity entity matching for over 40 global hardware suppliers, automatically falling back to simulated data only if a total network partition occurs.

### 2. The NLP & Sentiment Engine (`risk_scoring.py`)
Naïve dictionary-based sentiment scoring fails on nuanced financial text (e.g., falsely flagging "The company will *not* face *bankruptcy*" as a negative signal).
*   **Contextual Negation:** By integrating `TextBlob`, the NLP engine understands grammatical polarity and modifier flipping.
*   **Domain-Specific Anchoring:** The pure NLP score is then blended with a weighted dictionary of supply-chain-specific heuristics (e.g., heavily weighting terms like "recall," "disruption," or "shortage").

### 3. The Machine Learning Tournament
Supply chain failure incidents are sparse, making pure supervised learning difficult. This module uses **Weak Supervision**:
*   **AutoML Selection:** The system extracts 10+ mathematical features (e.g., trailing volatility, 52-week position) and dynamically trains an arena of models (`RandomForest`, `GradientBoosting`, `XGBoost`, `LinearRegression`, `SVR`). It seamlessly evaluates them and selects the predictor with the lowest Mean Squared Error (MSE).
*   **Ensemble Guardrails:** To prevent the ML black box from hallucinating catastrophic risk scores, the final predictive score is a carefully balanced ensemble: **70% ML Output + 30% Expert Rule-Based Anchor**.

### 4. Presentation & Microservices
*   **Lightning-Fast UI (`app.py`):** The Streamlit dashboard utilizes `@st.cache_resource` for memoization, ensuring that complex Pandas DataFrame transformations and model inferences are strictly cached, providing instantaneous, deeply interactive Plotly visualizations.
*   **Enterprise Integration (`api.py`):** The entire scoring engine is cleanly exposed via a fully documented FastAPI REST service (complete with Pydantic schema validation), making it immediately pluggable into external enterprise systems (like SAP or Oracle).

---

## 🛠️ Tech Stack
*   **Core:** Python 3.11, Pandas, NumPy
*   **Machine Learning:** Scikit-Learn, XGBoost
*   **NLP:** TextBlob, Feedparser
*   **Web / API:** Streamlit, FastAPI, Uvicorn
*   **Visualization:** Plotly Express, Plotly Graph Objects

---

## 📖 Quick Start (Local Setup)

The architecture is entirely modular and can be spun up locally in under 5 minutes.

### 1. Clone & Environment
```bash
git clone https://github.com/KV0217/supplier-risk-intelligence.git
cd supplier-risk-intelligence

# Initialize virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launching Interfaces
```bash
# Launch the Interactive Dashboard (Automatically opens at http://localhost:8501)
streamlit run app.py

# OR: Launch the REST API Service (Swagger Docs at http://localhost:8000/docs)
uvicorn api:app --reload
```

---

## 📂 Repository Structure

| File | Technical Purpose |
|------|---------|
| `data_collector.py` | ETL engine containing the resilient multi-source API waterfall and RSS ingestion. |
| `risk_scoring.py` | The analytical brain. Contains feature engineering, NLP negation logic, and the AutoML competition. |
| `app.py` | The Streamlit visualization dashboard utilizing memoized state for performance. |
| `api.py` | Asynchronous FastAPI REST surface for headless, programmatic scoring workflows. |
| `config.py` | Centralized hyperparameter and configuration dictionaries (for modifying keywords or suppliers). |

---

## 👨‍💻 Primary Architect

**Kavin Venkat**
🎓 *Data Analyst / ML Engineer*
🔗 [LinkedIn Profile](https://www.linkedin.com/in/kavin-venkat-1710s0202)
🐙 [GitHub Portfolio](https://github.com/KV0217)

*Designed as an end-to-end demonstration of data engineering resilience, context-aware NLP, and applied machine learning.*