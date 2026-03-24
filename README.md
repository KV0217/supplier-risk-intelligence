<h1 align="center">Supplier Risk Intelligence Platform</h1>
<p align="center">
  End-to-end ML project for supplier disruption monitoring using live news and market signals, deployed as a dashboard and REST API.
</p>
<p align="center">
  <em>Real-time monitoring | NLP sentiment analysis | Financial risk scoring | Production deployment</em>
</p>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Render](https://img.shields.io/badge/Render-API%20Hosting-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com/)
[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-7C3AED?style=for-the-badge)](https://supplier-risk-intelligence-kv.streamlit.app)
[![API Docs](https://img.shields.io/badge/API-Docs-0EA5E9?style=for-the-badge)](https://supplier-risk-intelligence-1.onrender.com/docs)

## 🔗 Live Links

- Dashboard: `https://supplier-risk-intelligence-kv.streamlit.app`
- API Base URL: `https://supplier-risk-intelligence-1.onrender.com`
- API Docs: `https://supplier-risk-intelligence-1.onrender.com/docs`

## 📌 Overview

Procurement teams need early warning for supplier risk, but manual tracking across news and financial data is slow and inconsistent.

This system automates that process:
- Collects live business news and stock data
- Scores sentiment and financial stress
- Produces a unified supplier risk score (`0-100`)
- Exposes results through an interactive Streamlit UI and FastAPI endpoints

## ✨ Key Features

- Live RSS ingestion (Bloomberg, Reuters, CNBC)
- Supplier mention detection from article text
- NLP sentiment analysis (rule-based + TextBlob blend)
- Financial risk scoring (volatility, trend, 52-week range)
- Composite risk score and severity labels
- Dashboard with filtering, drill-down, and exports
- API for single, batch, and portfolio-level risk queries
- Cloud-safe fallbacks when upstream data is empty/unavailable

## 🧠 Risk Scoring Logic

1. **News Risk**
   - Sentiment from article title + summary
   - More negative sentiment -> higher risk

2. **Financial Risk**
   - Higher volatility -> higher risk
   - Negative annual trend -> higher risk
   - Price near 52-week low -> higher risk

3. **Composite Risk**

```text
Final Risk = (News Risk * News Weight) + (Financial Risk * Financial Weight)
```

Risk levels:
- `>= 75`: CRITICAL
- `60-74.99`: HIGH
- `40-59.99`: MEDIUM
- `25-39.99`: LOW
- `< 25`: MINIMAL

## 🚀 API Endpoints

- `GET /health`
- `POST /api/v1/risk/assess`
- `POST /api/v1/risk/batch`
- `GET /api/v1/risk/{company_name}`
- `GET /api/v1/risks/all`
- `GET /api/v1/risks/critical`
- `GET /api/v1/stats`

Example:

```bash
curl -X POST "https://supplier-risk-intelligence-1.onrender.com/api/v1/risk/assess" \
  -H "Content-Type: application/json" \
  -d "{\"company_name\":\"Tesla\",\"include_news\":true,\"include_financial\":true}"
```

## 📊 Dashboard Modules

- Risk overview KPIs and portfolio gauge
- Risk distribution and comparison charts
- News trend and sentiment views
- Financial health analysis
- Supplier-level drill-down
- CSV and audit report export

## 🖼️ Screenshots

Add your screenshots in a repo folder like `assets/screenshots/`, then update filenames below.

<table>
  <tr>
    <td align="center"><strong>Dashboard Overview</strong></td>
    <td align="center"><strong>Risk Distribution</strong></td>
  </tr>
  <tr>
    <td><img src="assets/screenshots/dashboard-overview.png" alt="Dashboard Overview" width="100%"></td>
    <td><img src="assets/screenshots/risk-distribution.png" alt="Risk Distribution" width="100%"></td>
  </tr>
  <tr>
    <td align="center"><strong>Financial Metrics</strong></td>
    <td align="center"><strong>Supplier Risk Table</strong></td>
  </tr>
  <tr>
    <td><img src="assets/screenshots/financial-metrics.png" alt="Financial Metrics" width="100%"></td>
    <td><img src="assets/screenshots/supplier-risk-table.png" alt="Supplier Risk Table" width="100%"></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>API Swagger Docs</strong></td>
  </tr>
  <tr>
    <td colspan="2"><img src="assets/screenshots/api-docs.png" alt="API Docs" width="100%"></td>
  </tr>
</table>

## 🛠️ Tech Stack

- **Backend/API:** FastAPI, Uvicorn
- **Dashboard:** Streamlit, Plotly
- **Data/ML:** Pandas, NumPy, TextBlob, scikit-learn
- **Data Sources:** RSS feeds, Yahoo Finance (`yfinance`)
- **Deployment:** Render (API), Streamlit Community Cloud (UI)

## 📁 Project Structure

```text
.
|- app.py
|- api.py
|- data_collector.py
|- risk_scoring.py
|- requirements.txt
|- runtime.txt
|- .python-version
```

## ⚙️ Local Setup

```bash
git clone https://github.com/KV0217/supplier-risk-intelligence.git
cd supplier-risk-intelligence

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Run API:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Run Dashboard:

```bash
streamlit run app.py
```

## ☁️ Deployment Notes

- API deployed on Render with Python version pinning (`runtime.txt`, `.python-version`)
- Streamlit deployed on Streamlit Cloud
- Added runtime protections for missing/empty upstream data
- Improved dark-theme chart/table readability

## 💼 Resume-Ready Highlights

- Built and deployed an end-to-end supplier risk intelligence platform with live data ingestion, NLP sentiment scoring, and financial risk analytics.
- Exposed production-style FastAPI endpoints and an executive dashboard for risk monitoring and reporting.
- Implemented resilient cloud behavior for third-party API/feed failures.

## 🔮 Future Enhancements

- Historical storage in PostgreSQL
- Scheduled scoring + automated alerts (email/Slack)
- Model monitoring and drift checks
- Advanced NLP (transformers) for improved signal quality

## 👨‍💻 Author

**Kavin Venkat**  
📫 LinkedIn: [Kavin Venkat](https://www.linkedin.com/in/kavin-venkat-1710s0202)
