# 🔍 Supplier Risk Intelligence

An end-to-end pipeline that ingests public market and news data, scores suppliers using rule-based and ML methods, and delivers insights through a REST API and executive dashboard — built to demonstrate how a lean analytics team can turn unstructured headlines and structured price data into a repeatable supplier risk signal, without proprietary datasets or mocked financials.

**Repository:** [github.com/KV0217/supplier-risk-intelligence](https://github.com/KV0217/supplier-risk-intelligence)

| 🔗 Resource | URL |
|-------------|-----|
| 📊 Dashboard | [supplier-risk-intelligence-kv.streamlit.app](https://supplier-risk-intelligence-kv.streamlit.app) |
| ⚡ API Base | [supplier-risk-intelligence-1.onrender.com](https://supplier-risk-intelligence-1.onrender.com) |
| 📄 API Docs | [supplier-risk-intelligence-1.onrender.com/docs](https://supplier-risk-intelligence-1.onrender.com/docs) |

> Hosted instances may change with redeploys.

---

## 💡 Overview

Procurement and supply-chain teams need early signals — supplier distress typically surfaces in news and price behaviour before it appears in internal systems. This project demonstrates how to:

- Ingest noisy, delayed, and heterogeneous public data
- Engineer interpretable features aligned to risk (sentiment, volatility, trend, range position)
- Produce a scalar risk score (0–100) with tiered labels suitable for triage
- Expose the same scoring logic through both a UI and a REST interface

---

## 🏗️ System Architecture

```mermaid
flowchart LR
  RSS[RSS Feeds] --> NewsDF[News DataFrame]
  MKT[Yahoo / Stooq / Optional APIs] --> FinDF[Market DataFrame]
  NewsDF --> FE[Feature Engineering]
  FinDF --> FE
  FE --> Rules[Rule-based Scores]
  FE --> ML[XGBoost Regressor]
  Rules --> ML
  ML --> API[FastAPI]
  ML --> UI[Streamlit]
```

| Layer | Description |
|-------|-------------|
| 📰 **News** | RSS ingestion from Bloomberg, Reuters, CNBC, MarketWatch, TechCrunch (configurable in `config.py`). Articles are filtered when monitored supplier names appear in title or summary. |
| 📈 **Market Data** | Real daily price history — no mocked financials. Per ticker, providers are tried in order: Yahoo Finance → Stooq → optional Twelve Data / Alpha Vantage / Finnhub. Each row records `data_source` for auditability. |
| 🧠 **Scoring** | Keyword + TextBlob sentiment → news risk; volatility / trend / 52-week position → financial risk; weighted composite feeds an XGBoost regressor with weak supervision. |
| 🚀 **Delivery** | Streamlit dashboard (`app.py`) and FastAPI service (`api.py`) share the same scoring engine. |

---

## 🔬 Methodology

### 📰 News Signal
- Features derived from article title and summary: lexicon-weighted risk terms blended with TextBlob polarity
- Aggregates per supplier: average sentiment, article count, and distributional stats for downstream ML features

### 📈 Financial Signal
- Derived from ~1 year of daily closes: realized volatility (std of daily returns), trailing trend, and position relative to rolling 52-week high/low band

### 🧠 Composite & ML Scoring
- **Rule-based baseline:** Dynamic news vs. financial weighting with configurable caps — transparent and explainable for stakeholders
- **XGBoost regressor:** Trained on engineered features using weak labels bootstrapped from the baseline composite, a practical bridge until curated incident labels are available
- **Model persistence:** Trained model saved and reloaded as `xgboost_risk_model.pkl` for consistent inference across runs

> ⚠️ Severity thresholds (e.g. `CRITICAL ≥ 75`) are configurable and intended for operational triage, not regulatory decisions.

---

## 📁 Repository Layout

| File | Role |
|------|------|
| `data_collector.py` | RSS and multi-provider financial ingestion; records `data_source` per financial row |
| `risk_scoring.py` | Sentiment, financial rules, composite logic, XGBoost train/infer, model I/O |
| `app.py` | Streamlit monitoring dashboard |
| `api.py` | FastAPI REST service |
| `config.py` | RSS feeds, ticker list, scoring thresholds |
| `requirements.txt` | Pinned dependencies (`fastapi`, `uvicorn`, `xgboost`, etc.) |

---

## ⚡ Quick Start

```bash
git clone https://github.com/KV0217/supplier-risk-intelligence.git
cd supplier-risk-intelligence
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**▶️ Run the dashboard:**
```bash
streamlit run app.py
```

**▶️ Run the API:**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

**🔑 Optional API keys** (set as environment variables for additional price data resilience):

```
TWELVE_DATA_API_KEY
ALPHA_VANTAGE_API_KEY
FINNHUB_API_KEY
```

---

## ⚠️ Data Provenance & Limitations

Public data is real but not equivalent to a paid terminal or internal master data.

- **📰 News:** RSS reflects each outlet's feed exposure; latency and completeness vary. Cloud IP blocks can occasionally reduce article volume.
- **📈 Prices:** Free routes are commonly delayed (~15 min for many US listings) or end-of-day. Yahoo Finance and Stooq may disagree slightly; the pipeline prefers the first successful source per ticker and logs which was used.
- **🔭 Coverage:** The monitored universe is the ticker list in `config.py` (`STOCK_TICKERS`) — extend this mapping to broaden coverage.

If all providers fail for a ticker, that supplier is omitted rather than filled with fabricated values. Explicit gaps are preferable to synthetic data.

---

## 🚀 Extending the System

| Area | Recommendation |
|------|---------------|
| 🏷️ **Ground Truth** | Replace weak labels with incident logs (late delivery, quality holds, bankruptcy, force majeure); retrain with proper train/validate split and calibration |
| 🤖 **NLP** | Replace lexicon + TextBlob with domain-finetuned transformers once a few hundred labelled headlines are available |
| 🛡️ **Governance** | Add model cards, data freshness SLAs, and drift checks on feature distributions (`data_source` mix, article volume, volatility regime) |
| 🏢 **Infrastructure** | Land raw articles and quotes in Snowflake or BigQuery, version features, and schedule scoring with Airflow or cloud-native jobs |

---

## 🌐 Deployment

The typical pattern is **Streamlit Community Cloud** for the dashboard and **Render** for the API, with Python version pinned via `runtime.txt` or `.python-version`. Redeploy after dependency updates to pick up changes to packages such as `uvicorn` and `xgboost`.

---

## 📜 License & Data Use

Code is released for portfolio and learning purposes. Respect each publisher's RSS terms and each market data provider's terms of use. Scores are decision-support prototypes — not investment advice.

---

## 👤 Author

**KAVIN VENKAT**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kavin-venkat-1710s0202)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/KV0217)

*Maintained as a portfolio-quality analytics and engineering reference.*
