"""
Data Collection Module for Supplier Risk Intelligence System
Scrapes news from RSS feeds and financial data from free APIs
"""

import feedparser
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsCollector:
    """Collects news from multiple RSS feeds for supplier monitoring"""
    
    def __init__(self):
        # Free RSS news feeds for business/supply chain news
        self.rss_feeds = [
            "http://feeds.bloomberg.com/markets/news.rss",
            "http://feeds.reuters.com/reuters/businessNews",
            "http://feeds.cnbc.com/cnbc/id/100003114/",
            "https://feeds.bloomberg.com/markets/supplychain.rss",
        ]
        
        self.supplier_companies = [
            "Apple", "Tesla", "Samsung", "Intel", "TSMC", "Microsoft",
            "Amazon", "Google", "Meta", "Nvidia", "AMD", "Taiwan Semiconductor",
            "Qualcomm", "Broadcom", "Analog Devices", "STMicroelectronics",
            "Sony", "LG Electronics", "Foxconn", "SMIC", "SK Hynix",
            "Micron Technology", "Western Digital", "Seagate", "Corsair",
            "ASUS", "Gigabyte", "MSI", "HP", "Dell", "Lenovo",
            "Cisco", "Juniper", "Arista", "Marvell", "Skyworks",
            "Realtek", "MediaTek", "UMC", "GlobalFoundries", "Infineon"
        ]
    
    def fetch_news(self, days_back: int = 7) -> List[Dict]:
        """Fetch news articles from RSS feeds"""
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Limit to 20 per feed
                    try:
                        pub_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                        
                        if pub_date > cutoff_date:
                            title = entry.get('title', '')
                            summary = entry.get('summary', '')[:500]
                            
                            # Check if article mentions any supplier company
                            matched_companies = [company for company in self.supplier_companies 
                                               if company.lower() in (title + " " + summary).lower()]
                            
                            if matched_companies:
                                articles.append({
                                    'title': title,
                                    'summary': summary,
                                    'link': entry.get('link', ''),
                                    'published': pub_date,
                                    'source': feed_url.split('/')[2],
                                    'companies': ', '.join(matched_companies),
                                    'fetch_date': datetime.now()
                                })
                    except Exception as e:
                        logger.warning(f"Error processing entry: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching {feed_url}: {e}")
                continue
        
        return articles


class FinancialDataCollector:
    """Collects basic financial data from free APIs"""
    
    def __init__(self):
        self.suppliers = {
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
            'SKX': 'Skyworks',
            'MRVL': 'Marvell',
            'SSNLF': 'Samsung',
            'LPL': 'LG',
            'QVCO': 'Corsair',
        }
    
    def fetch_stock_data(self) -> pd.DataFrame:
        """Fetch stock data from yfinance-like free sources"""
        data = []
        
        try:
            import yfinance as yf
            
            for ticker, name in self.suppliers.items():
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1y")
                    
                    if len(hist) > 0:
                        current_price = hist['Close'].iloc[-1]
                        price_52w_high = hist['Close'].max()
                        price_52w_low = hist['Close'].min()
                        volatility = hist['Close'].pct_change().std() * 100
                        
                        # Calculate price trend (positive = uptrend)
                        price_trend = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                        
                        data.append({
                            'ticker': ticker,
                            'company_name': name,
                            'current_price': current_price,
                            'price_52w_high': price_52w_high,
                            'price_52w_low': price_52w_low,
                            'volatility': volatility,
                            'price_trend': price_trend,
                            'fetch_date': datetime.now()
                        })
                        time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching data for {ticker}: {e}")
                    continue
        
        except ImportError:
            logger.warning("yfinance not available, using mock data for demo")
            data = self._generate_mock_financial_data()
        
        return pd.DataFrame(data)
    
    def _generate_mock_financial_data(self) -> list:
        """Generate realistic mock financial data for demo purposes"""
        import random
        data = []
        
        for ticker, name in list(self.suppliers.items())[:15]:
            base_price = random.uniform(50, 200)
            data.append({
                'ticker': ticker,
                'company_name': name,
                'current_price': base_price,
                'price_52w_high': base_price * random.uniform(1.1, 1.5),
                'price_52w_low': base_price * random.uniform(0.7, 0.95),
                'volatility': random.uniform(15, 45),
                'price_trend': random.uniform(-20, 30),
                'fetch_date': datetime.now()
            })
        
        return data


class DataCollector:
    """Main coordinator for data collection"""
    
    def __init__(self):
        self.news_collector = NewsCollector()
        self.financial_collector = FinancialDataCollector()
    
    def collect_all_data(self) -> tuple:
        """Collect all data from news and financial sources"""
        logger.info("Starting comprehensive data collection...")
        
        # Collect news
        news_articles = self.news_collector.fetch_news(days_back=7)
        news_df = pd.DataFrame(news_articles)
        logger.info(f"Collected {len(news_df)} news articles")
        
        # Collect financial data
        financial_df = self.financial_collector.fetch_stock_data()
        logger.info(f"Collected financial data for {len(financial_df)} companies")
        
        return news_df, financial_df


if __name__ == "__main__":
    collector = DataCollector()
    news_data, financial_data = collector.collect_all_data()
    
    print("\n=== NEWS DATA ===")
    print(news_data.head())
    print(f"\nTotal articles: {len(news_data)}")
    
    print("\n=== FINANCIAL DATA ===")
    print(financial_data.head())
    print(f"\nTotal companies: {len(financial_data)}")
    
    # Save for later use
    news_data.to_csv('/tmp/news_data.csv', index=False)
    financial_data.to_csv('/tmp/financial_data.csv', index=False)
    print("\nData saved to /tmp/")
