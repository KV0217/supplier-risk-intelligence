"""
Risk Scoring Engine for Supplier Risk Intelligence System
Combines NLP sentiment analysis with rule-based ML scoring
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Tuple, List
import pickle
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Performs NLP-based sentiment analysis on news articles"""
    
    def __init__(self):
        try:
            from textblob import TextBlob
            self.textblob_available = True
        except ImportError:
            self.textblob_available = False
            logger.warning("TextBlob not available, using rule-based sentiment")
        
        # Risk keywords that indicate negative sentiment
        self.negative_keywords = {
            'bankruptcy': 3.0, 'layoff': 2.5, 'recall': 2.8, 'lawsuit': 2.5,
            'decline': 1.5, 'loss': 1.8, 'fail': 2.0, 'scandal': 2.5,
            'crisis': 2.5, 'emergency': 2.0, 'shortage': 2.0, 'delay': 1.5,
            'supply chain': 1.0, 'disruption': 2.0, 'problem': 1.2,
            'risk': 1.0, 'concern': 1.2, 'warning': 1.5, 'downgrade': 2.0,
            'default': 2.5, 'debt': 1.0, 'weak': 1.5, 'slump': 1.8,
            'suspended': 2.0, 'halted': 2.0, 'violated': 2.5, 'probe': 1.8,
        }
        
        self.positive_keywords = {
            'growth': 0.5, 'success': 0.5, 'profit': 0.7, 'expansion': 0.5,
            'strong': 0.7, 'recovery': 0.8, 'breakthrough': 0.8, 'improvement': 0.7,
            'leading': 0.5, 'innovation': 0.5, 'partnership': 0.4, 'deal': 0.3,
        }
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text
        Returns: sentiment score from -1.0 (very negative) to 1.0 (very positive)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Count negative keywords
        for keyword, weight in self.negative_keywords.items():
            score -= text_lower.count(keyword) * weight
        
        # Count positive keywords
        for keyword, weight in self.positive_keywords.items():
            score += text_lower.count(keyword) * weight
        
        # Normalize to -1 to 1 range
        score = max(-1.0, min(1.0, score / 10.0))
        
        # Try TextBlob if available for more accurate analysis
        if self.textblob_available:
            try:
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity  # -1 to 1
                # Blend rule-based and textblob analysis
                score = (score * 0.3) + (sentiment_score * 0.7)
            except:
                pass
        
        return score


class RiskScoringEngine:
    """Calculates comprehensive supplier risk scores"""
    
    def __init__(self, model_path: str = "xgboost_risk_model.pkl"):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.model_path = model_path
        self.ml_model = None
        self.ml_available = self._load_model()

    def _load_model(self) -> bool:
        """Load a persisted XGBoost model if available."""
        if not os.path.exists(self.model_path):
            return False

        try:
            with open(self.model_path, "rb") as f:
                self.ml_model = pickle.load(f)
            return True
        except Exception as exc:
            logger.warning(f"Could not load ML model from {self.model_path}: {exc}")
            self.ml_model = None
            return False

    def _save_model(self):
        """Persist trained XGBoost model to disk."""
        if self.ml_model is None:
            return
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.ml_model, f)
        except Exception as exc:
            logger.warning(f"Could not save ML model to {self.model_path}: {exc}")
    
    def calculate_news_risk_score(self, articles_df: pd.DataFrame, company: str) -> Tuple[float, int]:
        """
        Calculate risk score based on recent news sentiment
        Returns: (risk_score, article_count)
        """
        if articles_df is None or len(articles_df) == 0:
            return 0.0, 0
        
        # Filter articles for this company
        company_articles = articles_df[
            articles_df['companies'].str.contains(company, case=False, na=False)
        ]
        
        if len(company_articles) == 0:
            return 0.0, 0
        
        # Calculate average sentiment
        sentiments = []
        for idx, row in company_articles.iterrows():
            combined_text = str(row.get('title', '')) + ' ' + str(row.get('summary', ''))
            sentiment = self.sentiment_analyzer.analyze_sentiment(combined_text)
            sentiments.append(sentiment)
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        
        # Convert sentiment to risk score (negative sentiment = higher risk)
        # Sentiment -1 to 1 → Risk score 100 to 0
        news_risk = max(0, min(100, 50 - (avg_sentiment * 50)))
        
        return news_risk, len(company_articles)
    
    def calculate_financial_risk_score(self, financial_data: pd.DataFrame, company: str) -> float:
        """
        Calculate risk based on financial metrics
        """
        # Find company in financial data
        company_financial = financial_data[
            financial_data['company_name'].str.contains(company, case=False, na=False)
        ]
        
        if company_financial.empty:
            return 0.0
        
        row = company_financial.iloc[0]
        risk = 0.0
        
        # Volatility risk (high volatility = higher risk)
        volatility = row.get('volatility', 20)
        if volatility > 40:
            risk += 25
        elif volatility > 30:
            risk += 15
        elif volatility > 20:
            risk += 8
        else:
            risk += 2
        
        # Trend risk (negative trend = higher risk)
        trend = row.get('price_trend', 0)
        if trend < -15:
            risk += 25
        elif trend < -5:
            risk += 15
        elif trend < 0:
            risk += 8
        else:
            risk += max(0, -trend * 0.5)  # Small bonus for positive trend
        
        # Price position risk (near 52-week low = higher risk)
        current = row.get('current_price', 100)
        price_52w_low = row.get('price_52w_low', 100)
        price_52w_high = row.get('price_52w_high', 100)
        
        if price_52w_high > price_52w_low:
            price_position = (current - price_52w_low) / (price_52w_high - price_52w_low)
            if price_position < 0.2:
                risk += 20
            elif price_position < 0.4:
                risk += 12
            elif price_position > 0.9:
                risk += 8
        
        return min(100, risk)
    
    def calculate_composite_risk_score_rule_based(
        self, 
        news_risk: float, 
        financial_risk: float,
        article_count: int
    ) -> Tuple[float, str]:
        """
        Calculate final composite risk score
        Returns: (risk_score, risk_level)
        """
        # Weight the components
        # News is more important if we have recent articles
        news_weight = min(0.6, 0.3 + (article_count * 0.05))
        financial_weight = 1.0 - news_weight
        
        composite_score = (news_risk * news_weight) + (financial_risk * financial_weight)
        composite_score = min(100, max(0, composite_score))
        
        # Determine risk level
        if composite_score >= 75:
            risk_level = "🔴 CRITICAL"
        elif composite_score >= 60:
            risk_level = "🟠 HIGH"
        elif composite_score >= 40:
            risk_level = "🟡 MEDIUM"
        elif composite_score >= 25:
            risk_level = "🟢 LOW"
        else:
            risk_level = "✅ MINIMAL"
        
        return composite_score, risk_level

    def _risk_level_from_score(self, score: float) -> str:
        """Map numeric score to categorical risk level."""
        if score >= 75:
            return "🔴 CRITICAL"
        if score >= 60:
            return "🟠 HIGH"
        if score >= 40:
            return "🟡 MEDIUM"
        if score >= 25:
            return "🟢 LOW"
        return "✅ MINIMAL"

    def _extract_company_features(
        self,
        company: str,
        news_df: pd.DataFrame,
        financial_df: pd.DataFrame,
    ) -> Dict:
        """
        Build model features for one supplier.
        Uses both text-derived and market-derived signals.
        """
        company_articles = news_df[
            news_df["companies"].str.contains(company, case=False, na=False)
        ] if news_df is not None and len(news_df) > 0 else pd.DataFrame()

        article_count = len(company_articles)
        sentiments: List[float] = []

        for _, row in company_articles.iterrows():
            combined_text = str(row.get("title", "")) + " " + str(row.get("summary", ""))
            sentiments.append(self.sentiment_analyzer.analyze_sentiment(combined_text))

        if sentiments:
            sentiment_mean = float(np.mean(sentiments))
            sentiment_std = float(np.std(sentiments))
            sentiment_min = float(np.min(sentiments))
            sentiment_max = float(np.max(sentiments))
            negative_ratio = float(np.mean(np.array(sentiments) < -0.2))
        else:
            sentiment_mean = 0.0
            sentiment_std = 0.0
            sentiment_min = 0.0
            sentiment_max = 0.0
            negative_ratio = 0.0

        news_risk, _ = self.calculate_news_risk_score(news_df, company)

        company_financial = financial_df[
            financial_df["company_name"].str.contains(company, case=False, na=False)
        ]
        financial_risk = self.calculate_financial_risk_score(financial_df, company)

        if company_financial.empty:
            volatility = 20.0
            price_trend = 0.0
            current_price = 100.0
            price_52w_low = 100.0
            price_52w_high = 100.0
            price_position = 0.5
        else:
            row = company_financial.iloc[0]
            volatility = float(row.get("volatility", 20.0))
            price_trend = float(row.get("price_trend", 0.0))
            current_price = float(row.get("current_price", 100.0))
            price_52w_low = float(row.get("price_52w_low", current_price))
            price_52w_high = float(row.get("price_52w_high", current_price))
            denom = max(1e-6, price_52w_high - price_52w_low)
            price_position = float((current_price - price_52w_low) / denom)

        return {
            "company": company,
            "news_risk": float(news_risk),
            "financial_risk": float(financial_risk),
            "article_count": float(article_count),
            "sentiment_mean": sentiment_mean,
            "sentiment_std": sentiment_std,
            "sentiment_min": sentiment_min,
            "sentiment_max": sentiment_max,
            "negative_ratio": negative_ratio,
            "volatility": volatility,
            "price_trend": price_trend,
            "price_position": float(np.clip(price_position, 0.0, 1.0)),
        }

    def _train_xgboost_weak_supervision(self, features_df: pd.DataFrame) -> bool:
        """
        Train XGBoost on weak labels generated by the current rule-based scorer.
        This is the bridge from expert rules to a true learned model.
        """
        if len(features_df) < 8:
            return False

        try:
            from xgboost import XGBRegressor
        except ImportError:
            logger.warning("xgboost is not installed. Falling back to rule-based scoring.")
            return False

        feature_cols = [
            "news_risk",
            "financial_risk",
            "article_count",
            "sentiment_mean",
            "sentiment_std",
            "sentiment_min",
            "sentiment_max",
            "negative_ratio",
            "volatility",
            "price_trend",
            "price_position",
        ]

        # Weak labels from domain heuristic (current production formula).
        y = []
        for _, row in features_df.iterrows():
            weak_score, _ = self.calculate_composite_risk_score_rule_based(
                row["news_risk"], row["financial_risk"], int(row["article_count"])
            )
            y.append(weak_score)

        X = features_df[feature_cols]
        y = np.array(y, dtype=float)

        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            objective="reg:squarederror",
        )
        model.fit(X, y)

        self.ml_model = model
        self._save_model()
        return True

    def _predict_with_ml(self, feature_row: Dict) -> float:
        """Predict risk score using trained XGBoost model."""
        if self.ml_model is None:
            raise RuntimeError("ML model is not trained/loaded.")

        feature_cols = [
            "news_risk",
            "financial_risk",
            "article_count",
            "sentiment_mean",
            "sentiment_std",
            "sentiment_min",
            "sentiment_max",
            "negative_ratio",
            "volatility",
            "price_trend",
            "price_position",
        ]
        X = pd.DataFrame([{k: feature_row[k] for k in feature_cols}])
        pred = float(self.ml_model.predict(X)[0])
        return float(np.clip(pred, 0, 100))
    
    def score_suppliers(
        self, 
        news_df: pd.DataFrame, 
        financial_df: pd.DataFrame,
        companies: list = None
    ) -> pd.DataFrame:
        """
        Calculate risk scores for all suppliers
        """
        if companies is None:
            companies = financial_df['company_name'].unique().tolist()
        
        results = []
        feature_rows = []

        for company in companies:
            # Get financial company name variant
            financial_match = financial_df[
                financial_df['company_name'].str.contains(company, case=False, na=False)
            ]
            
            if financial_match.empty:
                continue

            feature_rows.append(self._extract_company_features(company, news_df, financial_df))

        if not feature_rows:
            return pd.DataFrame()

        features_df = pd.DataFrame(feature_rows)
        model_used = "Rule-Based"

        # Train once when a persisted model is unavailable.
        if not self.ml_available:
            self.ml_available = self._train_xgboost_weak_supervision(features_df)

        for _, row in features_df.iterrows():
            news_risk = float(row["news_risk"])
            financial_risk = float(row["financial_risk"])
            article_count = int(row["article_count"])

            if self.ml_available and self.ml_model is not None:
                composite_score = self._predict_with_ml(row.to_dict())
                risk_level = self._risk_level_from_score(composite_score)
                model_used = "XGBoost (Weak Supervision)"
            else:
                composite_score, risk_level = self.calculate_composite_risk_score_rule_based(
                    news_risk, financial_risk, article_count
                )

            results.append({
                "company": row["company"],
                "risk_score": round(composite_score, 2),
                "risk_level": risk_level,
                "news_risk": round(news_risk, 2),
                "financial_risk": round(financial_risk, 2),
                "recent_articles": article_count,
                "model_used": model_used,
                "assessment_date": datetime.now(),
            })
        
        return pd.DataFrame(results).sort_values('risk_score', ascending=False)


class RiskMonitor:
    """Monitors risk trends over time"""
    
    def __init__(self, history_file: str = 'risk_history.pkl'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load historical risk data"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save_history(self):
        """Save historical risk data"""
        try:
            with open(self.history_file, 'wb') as f:
                pickle.dump(self.history, f)
        except:
            pass
    
    def record_risk_scores(self, risk_df: pd.DataFrame):
        """Record risk scores for trend analysis"""
        timestamp = datetime.now().isoformat()
        
        for idx, row in risk_df.iterrows():
            company = row['company']
            if company not in self.history:
                self.history[company] = []
            
            self.history[company].append({
                'timestamp': timestamp,
                'risk_score': row['risk_score'],
                'risk_level': row['risk_level']
            })
        
        self._save_history()
    
    def get_risk_trend(self, company: str, days: int = 30) -> list:
        """Get historical risk trend for a company"""
        if company not in self.history:
            return []
        
        return self.history[company][-days:]


if __name__ == "__main__":
    from data_collector import DataCollector
    
    # Collect data
    print("Collecting data...")
    collector = DataCollector()
    news_df, financial_df = collector.collect_all_data()
    
    # Score suppliers
    print("\nScoring suppliers...")
    scoring_engine = RiskScoringEngine()
    risk_scores = scoring_engine.score_suppliers(news_df, financial_df)
    
    print("\n=== SUPPLIER RISK ASSESSMENT ===")
    print(risk_scores.to_string(index=False))
    
    # Save results
    risk_scores.to_csv('/tmp/risk_assessment.csv', index=False)
    print("\nRisk assessment saved to /tmp/risk_assessment.csv")
