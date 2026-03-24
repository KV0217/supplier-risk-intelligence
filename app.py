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

def load_data():
    """Load and cache data"""
    collector = DataCollector()
    scoring_engine = RiskScoringEngine()
    
    # Expected schemas to prevent runtime KeyErrors when external feeds are empty.
    news_columns = ['title', 'summary', 'link', 'published', 'source', 'companies', 'fetch_date', 'sentiment']
    financial_columns = ['ticker', 'company_name', 'current_price', 'price_52w_high', 'price_52w_low', 'volatility', 'price_trend', 'fetch_date']
    risk_columns = ['company', 'risk_score', 'risk_level', 'news_risk', 'financial_risk', 'recent_articles', 'assessment_date']
    
    try:
        news_df, financial_df = collector.collect_all_data()
    except Exception:
        news_df = pd.DataFrame(columns=news_columns)
        financial_df = pd.DataFrame(columns=financial_columns)
    
    if news_df is None or news_df.empty:
        news_df = pd.DataFrame(columns=news_columns)
    else:
        for col in news_columns:
            if col not in news_df.columns:
                news_df[col] = np.nan
    
    if financial_df is None or financial_df.empty:
        financial_df = pd.DataFrame(columns=financial_columns)
    else:
        for col in financial_columns:
            if col not in financial_df.columns:
                financial_df[col] = np.nan
    
    try:
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df)
    except Exception:
        risk_scores = pd.DataFrame(columns=risk_columns)
    
    if risk_scores is None or risk_scores.empty:
        risk_scores = pd.DataFrame(columns=risk_columns)
    
    return news_df, financial_df, risk_scores, scoring_engine


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
        go.Bar(
            x=risk_counts.index,
            y=risk_counts.values,
            marker=dict(
                color=['#ef4444', '#f59e0b', '#facc15', '#22c55e', '#38bdf8'],
                line=dict(color='#e5e7eb', width=1.5)
            ),
            text=risk_counts.values,
            textposition='outside',
            textfont=dict(color='#e5e7eb', size=12),
            cliponaxis=False
        )
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
    if len(news_df) == 0:
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
    st.markdown("Real-time monitoring of supplier risks through news sentiment analysis and financial metrics")
    
    # Sidebar filters
    st.sidebar.title("⚙️ Settings")
    refresh_button = st.sidebar.button("🔄 Refresh Data", use_container_width=True)
    
    min_risk_filter = st.sidebar.slider("Minimum Risk Score Filter", 0, 100, 0)
    
    show_high_risk_only = st.sidebar.checkbox("Show High Risk Only (≥60)")
    
    # Load data
    with st.spinner("Loading supplier data..."):
        news_df, financial_df, risk_scores, scoring_engine = load_data()
    
    if risk_scores.empty:
        st.warning("No supplier risk data is available right now. Please click 'Refresh Data' or try again shortly.")
        st.stop()
    
    # Filter data
    if show_high_risk_only:
        filtered_scores = risk_scores[risk_scores['risk_score'] >= 60]
    else:
        filtered_scores = risk_scores[risk_scores['risk_score'] >= min_risk_filter]
    
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
            st.plotly_chart(create_risk_gauge(risk_scores['risk_score'].mean(), "Portfolio Risk Score"), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_risk_distribution(risk_scores), use_container_width=True)
        
        # Risk scatter
        st.plotly_chart(create_risk_scatter(risk_scores), use_container_width=True)
        
        # Top risks table
        st.subheader("Top 15 Suppliers by Risk Score")
        top_risks = risk_scores.head(15)[['company', 'risk_score', 'risk_level', 'news_risk', 'financial_risk', 'recent_articles']]
        
        # Color code the table
        def color_code_risk(val):
            if val >= 75:
                return 'background-color: rgba(239, 68, 68, 0.35); color: #f8fafc; font-weight: 600;'
            elif val >= 60:
                return 'background-color: rgba(245, 158, 11, 0.35); color: #f8fafc; font-weight: 600;'
            elif val >= 40:
                return 'background-color: rgba(250, 204, 21, 0.35); color: #f8fafc; font-weight: 600;'
            else:
                return 'background-color: rgba(34, 197, 94, 0.35); color: #f8fafc; font-weight: 600;'
        
        styled_table = top_risks.style.applymap(
            color_code_risk, subset=['risk_score']
        ).format({
            'risk_score': '{:.2f}',
            'news_risk': '{:.2f}',
            'financial_risk': '{:.2f}'
        })
        
        st.dataframe(styled_table, use_container_width=True)
    
    # Tab 2: News Analysis
    with tab2:
        st.subheader("News Sentiment & Coverage Analysis")
        
        # News timeline
        st.plotly_chart(create_news_timeline(news_df), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(news_df) > 0:
                # Sentiment histogram
                fig = px.histogram(news_df, x='sentiment', nbins=20,
                                 title='News Sentiment Distribution',
                                 labels={'sentiment': 'Sentiment Score'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(news_df) > 0:
                # Top mentioned companies
                all_companies = []
                for companies_str in news_df['companies'].dropna():
                    all_companies.extend([c.strip() for c in companies_str.split(',')])
                
                company_counts = pd.Series(all_companies).value_counts().head(10)
                fig = px.bar(
                    x=company_counts.index,
                    y=company_counts.values,
                    title='Top 10 Companies in News',
                    labels={'x': 'Company', 'y': 'Mentions'},
                    color_discrete_sequence=['#60a5fa']
                )
                fig.update_traces(
                    texttemplate='%{y}',
                    textposition='outside',
                    marker_line_color='#e5e7eb',
                    marker_line_width=1.5
                )
                fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent news
        st.subheader("Recent News Articles")
        if len(news_df) > 0:
            recent_news = news_df.sort_values('published', ascending=False).head(10)
            for idx, row in recent_news.iterrows():
                with st.expander(f"📰 {row['title'][:60]}... ({row['published'].strftime('%Y-%m-%d')})"):
                    st.write(f"**Companies:** {row['companies']}")
                    st.write(f"**Sentiment:** {row['sentiment']:.3f}")
                    st.write(f"**Source:** {row['source']}")
                    st.write(f"{row['summary']}")
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
                fig.update_traces(
                    marker=dict(color='#38bdf8', line=dict(color='#e5e7eb', width=1.5)),
                    texttemplate='%{y}',
                    textposition='outside',
                    textfont=dict(color='#e5e7eb', size=11),
                    cliponaxis=False
                )
                fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Price trend analysis
                fig = px.histogram(financial_df, x='price_trend', nbins=15,
                                 title='Price Trend Distribution (1Y)',
                                 labels={'price_trend': 'Price Change (%)'})
                fig.update_traces(
                    marker=dict(color='#a78bfa', line=dict(color='#e5e7eb', width=1.5)),
                    texttemplate='%{y}',
                    textposition='outside',
                    textfont=dict(color='#e5e7eb', size=11),
                    cliponaxis=False
                )
                fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide')
                st.plotly_chart(fig, use_container_width=True)
            
            # Financial data table
            st.subheader("Financial Metrics by Supplier")
            financial_display = financial_df[['company_name', 'current_price', 'volatility', 'price_trend']].head(20)
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
            risk_scores['company'].values,
            index=0
        )
        
        # Get company data
        company_risk = risk_scores[risk_scores['company'] == selected_company].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Risk Score", f"{company_risk['risk_score']:.1f}/100")
        with col2:
            st.metric("Risk Level", company_risk['risk_level'])
        with col3:
            st.metric("News Risk", f"{company_risk['news_risk']:.1f}")
        with col4:
            st.metric("Financial Risk", f"{company_risk['financial_risk']:.1f}")
        
        # Risk breakdown
        st.subheader("Risk Score Breakdown")
        
        fig = go.Figure(data=[
            go.Bar(
                x=['News Risk', 'Financial Risk'],
                y=[company_risk['news_risk'], company_risk['financial_risk']],
                marker=dict(
                    color=['#f59e0b', '#60a5fa'],
                    line=dict(color='#e5e7eb', width=1.5)
                ),
                text=[f"{company_risk['news_risk']:.1f}", f"{company_risk['financial_risk']:.1f}"],
                textposition='outside',
                textfont=dict(color='#e5e7eb')
            )
        ])
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Related news
        st.subheader(f"Related News Articles ({company_risk['recent_articles']} found)")
        company_news = news_df[news_df['companies'].str.contains(selected_company, case=False, na=False)]
        
        if len(company_news) > 0:
            for idx, row in company_news.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{row['title']}**")
                    st.caption(f"{row['published'].strftime('%Y-%m-%d')} | Sentiment: {row['sentiment']:.3f}")
                with col2:
                    sentiment_label = "😊 Positive" if row['sentiment'] > 0.3 else "😟 Negative" if row['sentiment'] < -0.3 else "😐 Neutral"
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
