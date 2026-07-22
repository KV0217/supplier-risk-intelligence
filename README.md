# Supplier Risk Intelligence System

## Overview
Automated real-time risk monitoring system for 41 global semiconductor suppliers. This project leverages an ETL pipeline pulling from Google News RSS and Yahoo Finance API fallbacks.

## Architecture
1. **Data Ingestion (ETL):** Automated pipeline extracting news and financial data.
2. **Modeling:** 70/30 ML-rule ensemble classifier to accurately predict distress events.
   - **Performance:** Achieved zero false-safe classifications on validated distress events.
3. **Deployment:** FastAPI backend serving a Streamlit frontend with Plotly visualizations.

## Tech Stack
- **Languages:** Python
- **Data Processing:** Pandas
- **Machine Learning:** Gradient Boosting
- **NLP:** TextBlob
- **Deployment & Dashboard:** FastAPI, Streamlit, Plotly

## Business Value
Provides actionable intelligence on supplier health, allowing proactive supply chain risk management.
