# 📊 Supplier Risk Intelligence System

[!Python 3.11+](https://www.python.org/downloads/)
[!Streamlit](https://streamlit.io)
[!Machine Learning](#)
[!NLP](#)

> **An end-to-end pipeline combining real-time public market data, NLP-based news sentiment analysis, and an ML ensemble model to provide early warning signals for supply chain disruptions.**

Procurement and supply-chain teams care about **early signals**: supplier distress often appears in news and price behavior days or weeks before it shows up in internal systems. This system automates the monitoring of major suppliers, scoring them from 0 to 100 to help teams triage risk proactively.

---

## 🔗 Live Links

| Resource | URL |
|----------|-----|
| **Interactive Dashboard** | View Live on Streamlit Cloud |
| **API Base (Optional)** | supplier-risk-intelligence-1.onrender.com |
| **API Docs** | Swagger UI |

---

## 🏗️ System Architecture

```mermaid
flowchart LR
  RSS[RSS Feeds (Bloomberg, CNBC)] --> NewsDF[News NLP Processing]
  MKT[Yahoo / Stooq / APIs] --> FinDF[Market Data Processing]
  NewsDF --> FE[Feature Engineering]
  FinDF --> FE
  FE --> Rules[Rule-Based Anchor]
  FE --> ML[ML Tournament Winner]
  Rules --> Ensemble[70/30 Ensemble Score]
  ML --> Ensemble
  Ensemble --> UI[Streamlit Dashboard]
```

### The 3-Layer Scoring Engine

1.  **News Signal (NLP):** Scrapes real-time articles via highly reliable Google News RSS queries and dedicated financial feeds to ensure exact entity matching. Uses `TextBlob` polarity for contextual grammar and negation handling, blended with domain-specific keyword weighting (e.g., "bankruptcy", "shortage") to generate a sentiment score from -1.0 to +1.0.
2.  **Financial Signal:** Pulls ~1 year of daily closes utilizing a highly resilient API extraction waterfall (YFinance → Stooq → TwelveData) to completely bypass rate-limiting failures. It calculates realized volatility, trailing trend, and 52-week range position.
3.  **ML Ensemble Composite:** 
    *   **The Tournament:** Automatically trains and evaluates multiple models (`RandomForest`, `GradientBoosting`, `XGBoost`, `LinearRegression`, `SVR`) and dynamically selects the one with the lowest Mean Squared Error (MSE).
    *   **The Blend:** Blends the ML prediction (70%) with a hard-coded expert rule-based score (30%) to act as a guardrail against model hallucinations, ensuring total system stability.

---

## 🚀 Quick Start (Local Setup)

Want to run this locally? It takes less than 5 minutes.

### 1. Clone & Install
```bash
git clone https://github.com/KV0217/supplier-risk-intelligence.git
cd supplier-risk-intelligence
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Launch the System
```bash
# Option A: Run the interactive setup menu
python quickstart.py

# Option B: Run data collection and launch dashboard instantly
python quickstart.py --full

# Option C: Just launch the dashboard (if data is already collected)
streamlit run app.py
```
**The dashboard will automatically open at `http://localhost:8501`**

---

## 📁 Repository Structure

The core logic is modular and production-ready, featuring graceful fallbacks (mock data generation) if upstream APIs are rate-limited.

| File | Purpose |
|------|---------|
| `app.py` | The main Streamlit dashboard. Utilizes `@st.cache_resource` for instant UI interactions and lightning-fast rendering without constantly re-triggering the data pipeline. |
| `data_collector.py` | The ETL pipeline. Extracts data via Google News RSS and a multi-tiered Market API waterfall. Implements robust fallback mechanisms to ensure pipeline continuity during network failures or rate limits. |
| `risk_scoring.py` | The Brain. Contains the NLP logic (with negation handling), financial heuristics, and the AutoML model tournament. |
| `supplier_risk_analysis.ipynb` | An exploratory Jupyter notebook demonstrating the data science process step-by-step. |
| `config.py` | Centralized settings. Easily add new suppliers, adjust risk thresholds, or tweak sentiment keywords here. |
| `api.py` | A FastAPI REST surface for programmatic scoring (useful for integrations). |

---

## 📊 Dashboard Features

The Streamlit UI provides 5 interactive analytical views:

1.  **Risk Overview:** Portfolio-level gauges, risk distribution pie charts, and a sortable table of your riskiest suppliers.
2.  **News Analysis:** A 7-day timeline of coverage, sentiment distribution histograms, and direct links to flagged articles.
3.  **Financial Metrics:** Deep dives into volatility and price trends across the monitored universe.
4.  **Risk Details:** Select a specific supplier to see exactly *why* they were flagged, including the ML vs. Rule-based breakdown.
5.  **Export:** Download CSVs or generate text-based audit reports for compliance and procurement teams.

---

## ☁️ Deployment

This project is configured for seamless deployment on **Streamlit Community Cloud**.

1. Fork or Clone this repository to your GitHub.
2. Go to share.streamlit.io.
3. Click **New app**, select your repository, and set `app.py` as the main file.
4. Click **Deploy**. Your app will be live in ~2 minutes.

---

## 🔮 Extending the System (Phase 2)

If you wish to build upon this system, consider:
*   **Ground Truth Labels:** Replace the "weak supervision" labels with actual incident logs (e.g., late deliveries, quality holds) and retrain the models for true supervised learning.
*   **Advanced NLP:** Upgrade from TextBlob to a domain-finetuned HuggingFace Transformer (e.g., FinBERT) for more nuanced headline understanding.
*   **Persistence:** Implement the provided `phase2_enhancements.py` to store historical tracking data in an SQLite or PostgreSQL database.

---

## 👨‍💻 Author

**Kavin Venkat**
[!LinkedIn](https://www.linkedin.com/in/kavin-venkat-1710s0202)
[!GitHub](https://github.com/KV0217)

*Maintained as a portfolio-quality analytics and software engineering reference.*