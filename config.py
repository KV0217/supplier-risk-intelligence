"""
Configuration for Supplier Risk Intelligence System
"""

# Data Collection Settings
DATA_COLLECTION = {
    'NEWS_LOOKBACK_DAYS': 7,
    'NEWS_ARTICLES_PER_FEED': 20,
    'FINANCIAL_DATA_PERIOD': '1y',
    'RSS_FEEDS': [
        "http://feeds.bloomberg.com/markets/news.rss",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.cnbc.com/cnbc/id/100003114/",
        "https://feeds.bloomberg.com/markets/supplychain.rss",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://techcrunch.com/feed/",
        "https://arstechnica.com/business/feed/",
    ],
}

# Risk Scoring Settings
RISK_SCORING = {
    'MIN_ARTICLES_FOR_NEWS_WEIGHTING': 1,
    'MAX_RISK_SCORE': 100,
    'MIN_RISK_SCORE': 0,
}

# Risk Thresholds
RISK_THRESHOLDS = {
    'CRITICAL': 75,
    'HIGH': 60,
    'MEDIUM': 40,
    'LOW': 25,
    'MINIMAL': 0,
}

# Risk Level Labels
RISK_LEVELS = {
    'CRITICAL': '🔴 CRITICAL',
    'HIGH': '🟠 HIGH',
    'MEDIUM': '🟡 MEDIUM',
    'LOW': '🟢 LOW',
    'MINIMAL': '✅ MINIMAL',
}

# Supplier Companies to Monitor
SUPPLIERS = [
    'Apple', 'Tesla', 'Samsung', 'Intel', 'TSMC', 'Microsoft',
    'Amazon', 'Google', 'Meta', 'Nvidia', 'AMD', 'Taiwan Semiconductor',
    'Qualcomm', 'Broadcom', 'Analog Devices', 'STMicroelectronics',
    'Sony', 'LG Electronics', 'Foxconn', 'SMIC', 'SK Hynix',
    'Micron Technology', 'Western Digital', 'Seagate', 'Corsair',
    'ASUS', 'Gigabyte', 'MSI', 'HP', 'Dell', 'Lenovo',
    'Cisco', 'Juniper', 'Arista', 'Marvell', 'Skyworks',
    'Realtek', 'MediaTek', 'UMC', 'GlobalFoundries', 'Infineon'
]

# Stock Tickers for Financial Data
STOCK_TICKERS = {
    'AAPL': 'Apple',
    'TSLA': 'Tesla',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'META': 'Meta',
    'NVDA': 'Nvidia',
    'AMD': 'AMD',
    'INTC': 'Intel',
    'QCOM': 'Qualcomm',
    'AVGO': 'Broadcom',
    'CSCO': 'Cisco',
    'HPQ': 'HP',
    'DELL': 'Dell',
    'LOGI': 'Logitech',
    'SWKS': 'Skyworks',
    'MRVL': 'Marvell',
    'SSNLF': 'Samsung',
    'LPL': 'LG',
    'QVCO': 'Corsair',
}

# Sentiment Keywords
SENTIMENT = {
    'NEGATIVE_KEYWORDS': {
        'bankruptcy': 3.0, 'layoff': 2.5, 'recall': 2.8, 'lawsuit': 2.5,
        'decline': 1.5, 'loss': 1.8, 'fail': 2.0, 'scandal': 2.5,
        'crisis': 2.5, 'emergency': 2.0, 'shortage': 2.0, 'delay': 1.5,
        'supply chain': 1.0, 'disruption': 2.0, 'problem': 1.2,
        'risk': 1.0, 'concern': 1.2, 'warning': 1.5, 'downgrade': 2.0,
        'default': 2.5, 'debt': 1.0, 'weak': 1.5, 'slump': 1.8,
        'suspended': 2.0, 'halted': 2.0, 'violated': 2.5, 'probe': 1.8,
    },
    'POSITIVE_KEYWORDS': {
        'growth': 0.5, 'success': 0.5, 'profit': 0.7, 'expansion': 0.5,
        'strong': 0.7, 'recovery': 0.8, 'breakthrough': 0.8, 'improvement': 0.7,
        'leading': 0.5, 'innovation': 0.5, 'partnership': 0.4, 'deal': 0.3,
    }
}

# Display Settings
DISPLAY = {
    'THEME': 'plotly_white',
    'COLOR_SCHEME': {
        'CRITICAL': '#d62728',
        'HIGH': '#ff7f0e',
        'MEDIUM': '#ffd700',
        'LOW': '#2ca02c',
        'MINIMAL': '#1f77b4'
    },
    'DEFAULT_FIGURE_HEIGHT': 500,
    'DEFAULT_FIGURE_WIDTH': 1200,
}

# Database Settings (for future enhancement)
DATABASE = {
    'TYPE': 'sqlite',
    'PATH': 'supplier_risk.db',
    'HISTORY_RETENTION_DAYS': 90,
}

# Logging Settings
LOGGING = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
