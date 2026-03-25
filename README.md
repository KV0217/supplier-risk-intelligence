# 📊 Supplier Risk Intelligence System
Predicts which critical hardware and semiconductor suppliers are facing distress using an AI Ensemble (XGBoost + Rules) on real-time Yahoo Finance and Google News data. Features automated ETL resilience, TextBlob NLP negation handling, weak supervision, and a live interactive Streamlit web app deployed.

## Live Deployments
| App | URL |
|-----|-----|
| Streamlit Dashboard | https://supplier-risk-intel-kv.streamlit.app |
| REST API | https://supplier-risk-intel-api.onrender.com |
| API Docs | https://supplier-risk-intel-api.onrender.com/docs |

> Note: API might be on a free tier — first request may take 30 seconds to wake up.

## Screenshots
### Streamlit Dashboard
![App Demo](screenshots/streamlit_risk_demo.png)

## What's Inside
- Real-time ETL pipeline with fully resilient API fallback cascades
- Advanced feature engineering (Realized Volatility, 52-week position)
- Context-aware NLP with negation handling (TextBlob)
- Weak Supervision methodology for synthetic labeling 
- 5-model automated machine learning (AutoML) tournament
- Ensemble scoring — completely safeguards against ML black-box hallucinations

## API Usage
```python
import requests
response = requests.post(
    "https://supplier-risk-intel-api.onrender.com/api/v1/risk/assess",
    json={
        "company_name": "Intel",
        "include_news": True,
        "include_financial": True
    }
)
print(response.json())
```

## Sample Response
```json
{
  "company": "Intel",
  "risk_score": 68.5,
  "risk_level": "🟠 HIGH",
  "news_risk": 55.0,
  "financial_risk": 82.0,
  "recent_articles": 14,
  "assessment_date": "2024-03-24T10:00:00"
}
```

## 🔍 What Makes This Unique
- **Live Streamlit App** — 5-tab interactive dashboard cached heavily with memoization for lightning-fast speeds.
- **Resilient API Waterfall** — Bypasses aggressive Yahoo Finance rate-limiting by automatically failing-over to Stooq and TwelveData without crashing.
- **NLP Negation Handling** — Understands nuanced grammar (e.g., scoring "no bankruptcy" properly) using explicit TextBlob tokenization.
- **70/30 ML Ensemble** — Blends predictions from XGBoost (70%) with domain-expert rules (30%) to ensure absolute system stability.
- **Google News RSS Targeting** — Programmatically constructs tailored RSS queries to guarantee high-fidelity entity matching for 40+ hardware suppliers.

## 📊 Dataset
Continuous Real-Time Data Streams — Google News RSS & Yahoo Finance OHLCV Markets | Monitoring 41 Global Suppliers (Apple, TSMC, Nvidia, etc.)

## Tech Stack
Python · Pandas · Scikit-learn · XGBoost · TextBlob · FastAPI · Streamlit · Plotly Express · Feedparser

## 📈 Model Results
| Model | Mean Squared Error (MSE) |
|-------|-----|
| Linear Regression | ~18.5 |
| Support Vector Regressor (SVR) | ~14.2 |
| Random Forest | ~9.8 |
| Gradient Boosting | ~8.4 |
| **XGBoost (Tuned Winner)** | **~7.5** |

## 🔑 Key Insights
- Suppliers exhibiting high continuous volatility (≥30%) carry extreme predictive signal.
- The 52-week trailing limit position acts as the strongest market anchor.
- Exact-match NLP triggers (e.g., "lawsuit," "shortage") cause massive short-term risk spikes.
- Using a 30% rule-based anchor prevents the ML system from hallucinating during unprecedented black-swan market events.

## 🚀 Streamlit App Features
- **Tab 1** — Portfolio Risk Overview (Interactive Gauges & Target Tables)
- **Tab 2** — News Analysis (Sentiment Distribution & Coverage Timelines)
- **Tab 3** — Financial Metrics (Volatility Distributions & Price Trends)
- **Tab 4** — Deep Risk Breakdown (Per-supplier force breakdown)
- **Tab 5** — Automated Audit Reporting (CSV & Text Export)

## 💰 Business Impact
- Shifts supply-chain mitigation from a reactive (ERP logs) to a predictive framework.
- Automates the daily screening of massive multi-modal information streams.
- Identifies supplier distress days or weeks before an operational failure occurs.

## 👤 Author
**KAVIN VENKAT**
[LinkedIn](www.linkedin.com/in/kavin-venkat-1710s0202) 
[Github](www.github.com/KV0217)