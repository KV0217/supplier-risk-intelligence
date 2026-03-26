"""
Streamlit Dashboard for Supplier Risk Intelligence System
Interactive visualization and monitoring of supplier risks
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '.')

from data_collector import DataCollector
from risk_scoring import RiskScoringEngine

# Configure page
st.set_page_config(
    page_title="Supplier Risk Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .critical { color: #d62728; font-weight: bold; }
    .high { color: #ff7f0e; font-weight: bold; }
    .medium { color: #ffd700; font-weight: bold; }
    .low { color: #2ca02c; font-weight: bold; }
    .minimal { color: #1f77b4; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


def style_histogram_bins(fig: go.Figure, bargap: float = 0.2) -> go.Figure:
    """Separate adjacent histogram bins with gaps and outlines (readable in dark theme)."""
    fig.update_layout(bargap=bargap)
    fig.update_traces(
        marker=dict(
            line=dict(width=1.2, color="rgba(255, 255, 255, 0.55)"),
        ),
        opacity=0.88,
    )
    return fig


@st.cache_resource
def load_data():
    """Load and cache data"""
    collector = DataCollector()
    news_df, financial_df = collector.collect_all_data()

    if news_df is None:
        news_df = pd.DataFrame()
    if financial_df is None:
        financial_df = pd.DataFrame()
    if "company_name" not in financial_df.columns:
        financial_df = pd.DataFrame(
            columns=[
                "company_name",
                "current_price",
                "volatility",
                "price_trend",
                "price_52w_high",
                "price_52w_low",
            ]
        )
    
    # Calculate risk scores
    scoring_engine = RiskScoringEngine()
    risk_scores = scoring_engine.score_suppliers(news_df, financial_df)

    if risk_scores is None or len(risk_scores) == 0:
        risk_scores = pd.DataFrame(
            columns=[
                "company",
                "risk_score",
                "risk_level",
                "news_risk",
                "financial_risk",
                "recent_articles",
                "model_used",
                "assessment_date",
            ]
        )
    
    return news_df, financial_df, risk_scores, scoring_engine


def safe_refresh():
    """Best-effort cache clear across Streamlit versions."""
    try:
        st.cache_resource.clear()
    except Exception:
        pass
    try:
        st.cache_data.clear()
    except Exception:
        pass


def create_risk_gauge(value: float, title: str) -> go.Figure:
    """Create a gauge chart for risk visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "#2ca02c"},  # Green - Minimal
                {'range': [25, 40], 'color': "#ffd700"},  # Yellow - Low
                {'range': [40, 60], 'color': "#ff7f0e"},  # Orange - Medium
                {'range': [60, 75], 'color': "#ff6347"},  # Red-orange - High
                {'range': [75, 100], 'color': "#d62728"}  # Red - Critical
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def create_risk_scatter(risk_scores: pd.DataFrame) -> go.Figure:
    """Create scatter plot of news vs financial risk"""
    fig = px.scatter(
        risk_scores,
        x='financial_risk',
        y='news_risk',
        size='risk_score',
        color='risk_score',
        hover_name='company',
        hover_data=['risk_score', 'recent_articles'],
        color_continuous_scale='Reds',
        title='Financial vs News Risk Analysis',
        labels={
            'financial_risk': 'Financial Risk Score',
            'news_risk': 'News Sentiment Risk Score'
        }
    )
    fig.update_layout(height=500, hovermode='closest')
    return fig


def create_risk_distribution(risk_scores: pd.DataFrame) -> go.Figure:
    """Create distribution chart of risk levels"""
    risk_level_map = {
        '🔴 CRITICAL': 'Critical (75+)',
        '🟠 HIGH': 'High (60-75)',
        '🟡 MEDIUM': 'Medium (40-60)',
        '🟢 LOW': 'Low (25-40)',
        '✅ MINIMAL': 'Minimal (<25)'
    }
    
    risk_counts = risk_scores['risk_level'].value_counts().rename(index=risk_level_map)
    
    fig = go.Figure(data=[
        go.Bar(x=risk_counts.index, y=risk_counts.values, marker_color=['#d62728', '#ff7f0e', '#ffd700', '#2ca02c', '#1f77b4'])
    ])
    fig.update_layout(
        title='Supplier Distribution by Risk Level',
        xaxis_title='Risk Level',
        yaxis_title='Number of Suppliers',
        height=400,
        showlegend=False
    )
    return fig


def create_news_timeline(news_df: pd.DataFrame) -> go.Figure:
    """Create timeline of news articles"""
    if len(news_df) == 0 or "published" not in news_df.columns:
        return go.Figure().add_annotation(text="No news data available")
    
    news_timeline = news_df.groupby(pd.Grouper(key='published', freq='D')).size()
    
    fig = go.Figure(data=[
        go.Scatter(x=news_timeline.index, y=news_timeline.values, mode='lines+markers',
                  fill='tozeroy', name='Articles per Day')
    ])
    fig.update_layout(
        title='News Coverage Timeline (Last 7 Days)',
        xaxis_title='Date',
        yaxis_title='Number of Articles',
        height=400,
        hovermode='x unified'
    )
    return fig


def main():
    # Header
    st.title("📊 Supplier Risk Intelligence Platform")
    st.markdown("Real-time monitoring of supplier risks through news sentiment analysis, financial metrics, and XGBoost ML scoring")
    
    # Sidebar filters
    st.sidebar.title("⚙️ Settings")
    refresh_button = st.sidebar.button("🔄 Refresh Data", use_container_width=True)
    if refresh_button:
        safe_refresh()
        st.rerun()
    
    min_risk_filter = st.sidebar.slider("Minimum Risk Score Filter", 0, 100, 0)
    
    show_high_risk_only = st.sidebar.checkbox("Show High Risk Only (≥60)")
    
    # Load data first so we can check ML metrics
    with st.spinner("Loading supplier data..."):
        news_df, financial_df, risk_scores, scoring_engine = load_data()
        
    # Display ML Tournament Results in Sidebar
    if hasattr(scoring_engine, 'model_metrics') and scoring_engine.model_metrics:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏆 ML Model Tournament")
        st.sidebar.caption("Dynamically selected based on lowest Mean Squared Error (MSE)")
        
        # Sort by MSE if it's a dict, fallback to float sorting for older cached models
        sorted_metrics = sorted(
            scoring_engine.model_metrics.items(), 
            key=lambda x: x[1].get('MSE', float('inf')) if isinstance(x[1], dict) else x[1]
        )
        
        for name, metrics in sorted_metrics:
            is_winner = (name == getattr(scoring_engine, 'best_model_name', None))
            icon = "🥇" if is_winner else "▫️"
            
            if isinstance(metrics, dict):
                st.sidebar.markdown(f"**{icon} {name}**<br/><span style='font-size: 0.85em; color: gray;'>MSE: {metrics['MSE']:.2f} | MAE: {metrics['MAE']:.2f} | R²: {metrics['R2']:.2f}</span>", unsafe_allow_html=True)
            else:
                # Fallback for old cached data before the update
                st.sidebar.markdown(f"**{icon} {name}**<br/><span style='font-size: 0.85em; color: gray;'>MSE: {metrics:.2f}</span>", unsafe_allow_html=True)
    
    if risk_scores.empty:
        st.warning("No supplier risk data available right now. This usually means upstream financial/news sources returned empty data. Click Refresh Data and try again in a few minutes.")
        st.stop()
    
    # Check if we are using mock data and display a prominent warning
    is_mock_data = False
    if not financial_df.empty and 'data_source' in financial_df.columns:
        if (financial_df['data_source'] == 'mock_fallback').any():
            is_mock_data = True
            
    if is_mock_data:
        st.error("⚠️ **DEMO MODE ACTIVE:** Live data sources (Yahoo Finance / RSS feeds) are currently rate-limited or unavailable. The dashboard is using **simulated mock data** to demonstrate system functionality.")
    else:
        st.success("🟢 **LIVE DATA ACTIVE:** Successfully pulled real-time data from financial APIs and RSS feeds.")

    # Filter data
    if show_high_risk_only:
        filtered_scores = risk_scores[risk_scores['risk_score'] >= 60]
    else:
        filtered_scores = risk_scores[risk_scores['risk_score'] >= min_risk_filter]
        
    if filtered_scores.empty:
        st.warning("No suppliers match the current filter criteria. Please lower your Minimum Risk Score slider in the sidebar.")
        st.stop()
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Suppliers",
            len(risk_scores),
            f"+{len(filtered_scores)} monitored"
        )
    
    with col2:
        avg_risk = risk_scores['risk_score'].mean()
        st.metric(
            "Average Risk",
            f"{avg_risk:.1f}",
            f"{'+' if avg_risk > 50 else '-'} from baseline"
        )
    
    with col3:
        critical_count = len(risk_scores[risk_scores['risk_score'] >= 75])
        st.metric(
            "🔴 Critical",
            critical_count,
            "Needs immediate action" if critical_count > 0 else "None"
        )
    
    with col4:
        high_count = len(risk_scores[(risk_scores['risk_score'] >= 60) & (risk_scores['risk_score'] < 75)])
        st.metric(
            "🟠 High",
            high_count,
            "Monitor closely" if high_count > 0 else "None"
        )
    
    with col5:
        stable_count = len(risk_scores[risk_scores['risk_score'] < 40])
        st.metric(
            "✅ Stable",
            stable_count,
            "Low risk profile"
        )

    if "model_used" in risk_scores.columns and len(risk_scores) > 0:
        st.caption(f"Scoring model in use: **{risk_scores['model_used'].iloc[0]}**")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Risk Overview",
        "📰 News Analysis",
        "💰 Financial Metrics",
        "⚠️ Risk Details",
        "📊 Export"
    ])
    
    # Tab 1: Risk Overview
    with tab1:
        st.subheader("Risk Assessment Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_risk_gauge(filtered_scores['risk_score'].mean(), "Portfolio Risk Score"), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_risk_distribution(filtered_scores), use_container_width=True)
        
        # Risk scatter
        st.plotly_chart(create_risk_scatter(filtered_scores), use_container_width=True)
        
        # Top risks table
        st.subheader("Top 15 Suppliers by Risk Score")
        top_columns = ['company', 'risk_score', 'risk_level', 'news_risk', 'financial_risk', 'recent_articles']
        top_risks = filtered_scores.sort_values('risk_score', ascending=False).head(15)[top_columns]
        st.dataframe(
            top_risks,
            use_container_width=True,
            hide_index=True,
            column_config={
                "company": st.column_config.TextColumn("Company"),
                "risk_score": st.column_config.NumberColumn("Risk score", format="%.2f"),
                "risk_level": st.column_config.TextColumn("Risk level"),
                "news_risk": st.column_config.NumberColumn("News risk", format="%.2f"),
                "financial_risk": st.column_config.NumberColumn("Financial risk", format="%.2f"),
                "recent_articles": st.column_config.NumberColumn("Recent articles", format="%d"),
            },
        )
    
    # Tab 2: News Analysis
    with tab2:
        st.subheader("News Sentiment & Coverage Analysis")
        
        # News timeline
        st.plotly_chart(create_news_timeline(news_df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(news_df) > 0 and "sentiment" in news_df.columns:
                # Sentiment histogram
                fig = px.histogram(news_df, x='sentiment', nbins=20,
                                 title='News Sentiment Distribution',
                                 labels={'sentiment': 'Sentiment Score'})
                style_histogram_bins(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sentiment distribution unavailable for current data")
        
        with col2:
            if len(news_df) > 0 and "companies" in news_df.columns:
                # Top mentioned companies
                all_companies = []
                for companies_str in news_df['companies'].dropna():
                    all_companies.extend([c.strip() for c in companies_str.split(',')])
                
                company_counts = pd.Series(all_companies).value_counts().head(10)
                fig = px.bar(x=company_counts.index, y=company_counts.values,
                           title='Top 10 Companies in News',
                           labels={'x': 'Company', 'y': 'Mentions'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Company mention analysis unavailable for current data")
        
        # Recent news
        st.subheader("Recent News Articles")
        if len(news_df) > 0 and "published" in news_df.columns:
            recent_news = news_df.sort_values('published', ascending=False).head(10)
            for idx, row in recent_news.iterrows():
                with st.expander(f"📰 {row['title'][:60]}... ({row['published'].strftime('%Y-%m-%d')})"):
                    st.write(f"**Companies:** {row.get('companies', 'N/A')}")
                    sentiment_val = row.get('sentiment', None)
                    if sentiment_val is not None and not pd.isna(sentiment_val):
                        st.write(f"**Sentiment:** {sentiment_val:.3f}")
                    st.write(f"**Source:** {row.get('source', 'N/A')}")
                    st.write(f"{row.get('summary', '')}")
                    if row.get("link"):
                        st.write(f"[Read Full Article]({row['link']})")
        else:
            st.info("No recent news data available")
    
    # Tab 3: Financial Metrics
    with tab3:
        st.subheader("Financial Health Analysis")
        
        if len(financial_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Volatility analysis
                fig = px.histogram(financial_df, x='volatility', nbins=15,
                                 title='Stock Volatility Distribution',
                                 labels={'volatility': 'Volatility (%)'})
                style_histogram_bins(fig)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Price trend analysis
                fig = px.histogram(financial_df, x='price_trend', nbins=15,
                                 title='Price Trend Distribution (1Y)',
                                 labels={'price_trend': 'Price Change (%)'})
                style_histogram_bins(fig)
                st.plotly_chart(fig, use_container_width=True)
            
            # Financial data table
            st.subheader("Financial Metrics by Supplier")
            fin_cols = ['company_name', 'current_price', 'volatility', 'price_trend']
            if 'data_source' in financial_df.columns:
                fin_cols.append('data_source')
            financial_display = financial_df[fin_cols].head(20)
            st.dataframe(financial_display.style.format({
                'current_price': '${:.2f}',
                'volatility': '{:.2f}%',
                'price_trend': '{:.2f}%'
            }), use_container_width=True)
        else:
            st.info("No financial data available")
    
    # Tab 4: Risk Details
    with tab4:
        st.subheader("Detailed Risk Analysis")
        
        # Select company
        selected_company = st.selectbox(
            "Select a Supplier for Detailed Analysis",
            filtered_scores['company'].values,
            index=0
        )
        
        # Get company data
        company_risk = filtered_scores[filtered_scores['company'] == selected_company].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Risk Score", f"{company_risk['risk_score']:.1f}/100")
        with col2:
            st.metric("Risk Level", company_risk['risk_level'])
        with col3:
            st.metric("News Risk", f"{company_risk['news_risk']:.1f}")
        with col4:
            st.metric("Financial Risk", f"{company_risk['financial_risk']:.1f}")
        if "model_used" in company_risk.index:
            st.caption(f"Model used for this score: **{company_risk['model_used']}**")
        
        # Risk breakdown
        st.subheader("Risk Score Breakdown")
        
        fig = go.Figure(data=[
            go.Bar(x=['News Risk', 'Financial Risk'], 
                  y=[company_risk['news_risk'], company_risk['financial_risk']],
                  marker_color=['#ff7f0e', '#1f77b4'])
        ])
        fig.update_layout(height=400, showlegend=False, bargap=0.45)
        fig.update_traces(
            marker_line_width=1.5,
            marker_line_color="rgba(255, 255, 255, 0.5)",
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Related news
        st.subheader(f"Related News Articles ({company_risk['recent_articles']} found)")
        if "companies" in news_df.columns:
            company_news = news_df[news_df['companies'].str.contains(selected_company, case=False, na=False)]
        else:
            company_news = pd.DataFrame()
        
        if len(company_news) > 0:
            for idx, row in company_news.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{row['title']}**")
                    published = row.get("published", None)
                    published_text = published.strftime('%Y-%m-%d') if pd.notna(published) else "N/A"
                    sentiment_val = row.get("sentiment", None)
                    if sentiment_val is not None and not pd.isna(sentiment_val):
                        st.caption(f"{published_text} | Sentiment: {sentiment_val:.3f}")
                    else:
                        st.caption(f"{published_text} | Sentiment: N/A")
                with col2:
                    sentiment_val = row.get("sentiment", 0.0)
                    sentiment_label = "😊 Positive" if sentiment_val > 0.3 else "😟 Negative" if sentiment_val < -0.3 else "😐 Neutral"
                    st.write(sentiment_label)
        else:
            st.info(f"No recent news found for {selected_company}")
    
    # Tab 5: Export
    with tab5:
        st.subheader("Export Data & Reports")
        
        # Export options
        export_format = st.radio("Select Export Format", ["CSV", "Excel"])
        
        if export_format == "CSV":
            csv_data = risk_scores.to_csv(index=False)
            st.download_button(
                label="📥 Download Risk Assessment (CSV)",
                data=csv_data,
                file_name=f"supplier_risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            # For Excel, we'll create a simple CSV that can be imported
            st.info("Excel export can be created by importing the CSV into Excel or using pandas.ExcelWriter")
            excel_info = risk_scores.to_csv(index=False)
            st.download_button(
                label="📥 Download Risk Assessment",
                data=excel_info,
                file_name=f"supplier_risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Generate audit report
        if st.button("📋 Generate Audit Report"):
            report = f"""
SUPPLIER RISK INTELLIGENCE - AUDIT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
=================
Total Suppliers Analyzed: {len(risk_scores)}
Average Risk Score: {risk_scores['risk_score'].mean():.2f}/100
Critical Risks: {len(risk_scores[risk_scores['risk_score'] >= 75])}
High Risks: {len(risk_scores[(risk_scores['risk_score'] >= 60) & (risk_scores['risk_score'] < 75)])}
Stable Suppliers: {len(risk_scores[risk_scores['risk_score'] < 40])}

CRITICAL ISSUES
================
{chr(10).join([f"• {row['company']}: {row['risk_score']:.1f} - {row['risk_level']}" for _, row in risk_scores[risk_scores['risk_score'] >= 75].iterrows()]) if len(risk_scores[risk_scores['risk_score'] >= 75]) > 0 else "None identified"}

RISK DISTRIBUTION
====================
{risk_scores['risk_level'].value_counts().to_string()}

RECOMMENDATIONS
================
1. Immediate Review: Suppliers with score ≥ 75
2. Increased Monitoring: Suppliers with score 60-75
3. Diversification Strategy: High-risk sectors
4. Quarterly Reviews: All suppliers ≥ 40

Data Collection: Last 7 days
News Sources: Bloomberg, Reuters, CNBC
Financial Data: Yahoo Finance
            """
            
            st.download_button(
                label="📋 Download Audit Report",
                data=report,
                file_name=f"supplier_risk_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            st.success("Report generated successfully!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p><strong>Supplier Risk Intelligence Platform</strong></p>
        <p>Real-time monitoring | NLP-based sentiment analysis | ML risk scoring</p>
        <p style='font-size: 12px; color: gray;'>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
