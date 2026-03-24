"""
Phase 2 Enhancements - Database Integration & Advanced ML
Extends the basic system with persistent storage and trained models
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import pickle
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupplierRiskDatabase:
    """SQLite database for persistent risk tracking"""
    
    def __init__(self, db_path: str = 'supplier_risk.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Risk scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                news_risk REAL,
                financial_risk REAL,
                recent_articles INTEGER,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Historical trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                risk_score REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # News articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                companies TEXT,
                sentiment REAL,
                published TIMESTAMP,
                source TEXT,
                link TEXT,
                fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Financial metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                ticker TEXT,
                current_price REAL,
                volatility REAL,
                price_trend REAL,
                price_52w_high REAL,
                price_52w_low REAL,
                fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON risk_scores(company_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON risk_scores(assessment_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_date ON risk_history(timestamp)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def insert_risk_scores(self, risk_scores_df: pd.DataFrame):
        """Insert risk assessment into database"""
        conn = sqlite3.connect(self.db_path)
        
        risk_scores_df.to_sql('risk_scores', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(risk_scores_df)} risk scores")
    
    def insert_news_articles(self, news_df: pd.DataFrame):
        """Insert news articles into database"""
        conn = sqlite3.connect(self.db_path)
        
        news_df.to_sql('news_articles', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(news_df)} news articles")
    
    def insert_financial_metrics(self, financial_df: pd.DataFrame):
        """Insert financial metrics into database"""
        conn = sqlite3.connect(self.db_path)
        
        financial_df.to_sql('financial_metrics', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(financial_df)} financial records")
    
    def get_risk_history(self, company: str, days: int = 30) -> pd.DataFrame:
        """Get historical risk data for a company"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT * FROM risk_history
            WHERE company_name = ? 
            AND timestamp >= datetime('now', '-{days} days')
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(company,))
        conn.close()
        
        return df
    
    def get_trending_risks(self, days: int = 7) -> pd.DataFrame:
        """Get companies with increasing risk trends"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                company_name,
                risk_score,
                assessment_date,
                LAG(risk_score) OVER (PARTITION BY company_name ORDER BY assessment_date) as prev_score
            FROM risk_scores
            WHERE assessment_date >= datetime('now', ?)
            ORDER BY assessment_date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
        conn.close()
        
        # Calculate trend
        df['risk_change'] = df['risk_score'] - df['prev_score']
        df['trend_direction'] = df['risk_change'].apply(
            lambda x: '📈 Increasing' if x > 5 else '📉 Decreasing' if x < -5 else '➡️ Stable'
        )
        
        return df[df['risk_change'].notna()].sort_values('risk_change', ascending=False)
    
    def get_risk_summary(self, days: int = 30) -> Dict:
        """Get summary statistics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT 
                risk_level,
                COUNT(*) as count,
                AVG(risk_score) as avg_score
            FROM risk_scores
            WHERE assessment_date >= datetime('now', '-{days} days')
            GROUP BY risk_level
        '''
        
        summary = pd.read_sql_query(query, conn)
        conn.close()
        
        return summary.to_dict()
    
    def cleanup_old_data(self, retention_days: int = 90):
        """Remove data older than retention period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cursor.execute(
            'DELETE FROM risk_history WHERE timestamp < ?',
            (cutoff_date,)
        )
        cursor.execute(
            'DELETE FROM risk_scores WHERE assessment_date < ?',
            (cutoff_date,)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {deleted} old records")


class AdvancedRiskModel:
    """Machine learning model for risk prediction"""
    
    def __init__(self, model_path: str = 'risk_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
    
    def prepare_training_data(self, 
                             news_risk: np.ndarray,
                             financial_risk: np.ndarray,
                             article_count: np.ndarray,
                             volatility: np.ndarray) -> np.ndarray:
        """Prepare features for model training"""
        
        features = np.column_stack([
            news_risk,
            financial_risk,
            article_count,
            volatility,
            # Interaction terms
            news_risk * financial_risk,
            article_count * volatility,
            # Polynomial features
            news_risk ** 2,
            financial_risk ** 2,
        ])
        
        return features
    
    def train_model(self,
                   features: np.ndarray,
                   targets: np.ndarray):
        """Train ML model on historical data"""
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import GradientBoostingRegressor
        
        # Scale features
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model.fit(features_scaled, targets)
        
        # Save model
        self._save_model()
        
        logger.info("Model trained and saved")
    
    def predict_risk(self,
                    news_risk: float,
                    financial_risk: float,
                    article_count: int,
                    volatility: float) -> float:
        """Predict risk using trained model"""
        
        if self.model is None:
            self._load_model()
        
        features = np.array([[
            news_risk,
            financial_risk,
            article_count,
            volatility,
            news_risk * financial_risk,
            article_count * volatility,
            news_risk ** 2,
            financial_risk ** 2,
        ]])
        
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        
        return float(np.clip(prediction, 0, 100))
    
    def _save_model(self):
        """Save model to disk"""
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def _load_model(self):
        """Load model from disk"""
        if Path(self.model_path).exists():
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']


class AlertSystem:
    """Real-time alerting for critical risks"""
    
    def __init__(self, alert_threshold: float = 75):
        self.alert_threshold = alert_threshold
        self.alert_history = []
    
    def check_critical_risks(self, risk_scores: pd.DataFrame) -> List[Dict]:
        """Check for critical risks and generate alerts"""
        alerts = []
        
        critical = risk_scores[risk_scores['risk_score'] >= self.alert_threshold]
        
        for idx, row in critical.iterrows():
            alert = {
                'severity': 'CRITICAL',
                'company': row['company'],
                'risk_score': row['risk_score'],
                'timestamp': datetime.now(),
                'message': f"🚨 {row['company']} risk score: {row['risk_score']:.1f}/100",
                'action': 'Immediate review required'
            }
            alerts.append(alert)
            self.alert_history.append(alert)
        
        return alerts
    
    def send_email_alert(self, alert: Dict, recipient: str):
        """Send email alert (requires email configuration)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Configure these in production
            SENDER_EMAIL = "alerts@yourcompany.com"
            SENDER_PASSWORD = "your_app_password"
            
            message = MIMEMultipart("alternative")
            message["Subject"] = f"⚠️ Supply Chain Risk Alert: {alert['company']}"
            message["From"] = SENDER_EMAIL
            message["To"] = recipient
            
            html = f"""
            <html>
              <body>
                <h2>Supply Chain Risk Alert</h2>
                <p><strong>Company:</strong> {alert['company']}</p>
                <p><strong>Risk Score:</strong> {alert['risk_score']:.1f}/100</p>
                <p><strong>Severity:</strong> {alert['severity']}</p>
                <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
                <p><strong>Recommended Action:</strong> {alert['action']}</p>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            # Send email (commented for safety)
            # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            #     server.login(SENDER_EMAIL, SENDER_PASSWORD)
            #     server.sendmail(SENDER_EMAIL, recipient, message.as_string())
            
            logger.info(f"Alert email prepared for {recipient}")
        
        except Exception as e:
            logger.error(f"Email alert failed: {e}")
    
    def get_alert_summary(self) -> Dict:
        """Get summary of recent alerts"""
        if not self.alert_history:
            return {'total': 0, 'critical': 0, 'recent': []}
        
        recent_alerts = self.alert_history[-10:]
        
        return {
            'total': len(self.alert_history),
            'critical': len([a for a in self.alert_history if a['severity'] == 'CRITICAL']),
            'recent': recent_alerts
        }


class RiskPrediction:
    """Predict future risk based on trends"""
    
    @staticmethod
    def predict_next_week(risk_history: pd.DataFrame) -> Dict:
        """Forecast risk for next 7 days"""
        if len(risk_history) < 3:
            return {'trend': 'Insufficient data', 'forecast': None}
        
        # Simple trend analysis
        scores = risk_history['risk_score'].values
        dates = pd.to_datetime(risk_history['timestamp']).values
        
        # Calculate trend
        x = np.arange(len(scores))
        z = np.polyfit(x, scores, 1)
        trend_slope = z[0]
        
        # Forecast
        next_score = scores[-1] + (trend_slope * 7)
        next_score = np.clip(next_score, 0, 100)
        
        trend = 'Increasing' if trend_slope > 0 else 'Decreasing' if trend_slope < 0 else 'Stable'
        
        return {
            'current_score': float(scores[-1]),
            'predicted_score': float(next_score),
            'trend': trend,
            'trend_slope': float(trend_slope),
            'confidence': 'Low' if len(risk_history) < 10 else 'Medium' if len(risk_history) < 30 else 'High'
        }
    
    @staticmethod
    def detect_anomalies(risk_history: pd.DataFrame, threshold: float = 2.0) -> List[Dict]:
        """Detect unusual risk spikes"""
        if len(risk_history) < 10:
            return []
        
        scores = risk_history['risk_score'].values
        mean = np.mean(scores)
        std = np.std(scores)
        
        anomalies = []
        
        for idx, (ts, score) in enumerate(zip(risk_history['timestamp'], scores)):
            z_score = abs((score - mean) / std)
            
            if z_score > threshold:
                anomalies.append({
                    'timestamp': ts,
                    'score': score,
                    'z_score': z_score,
                    'type': 'Spike' if score > mean else 'Dip'
                })
        
        return anomalies


if __name__ == "__main__":
    # Example usage
    print("Phase 2 Enhancements Demo\n")
    
    # Initialize database
    db = SupplierRiskDatabase()
    print("✅ Database initialized")
    
    # Initialize ML model
    model = AdvancedRiskModel()
    print("✅ ML model initialized")
    
    # Initialize alerts
    alerts = AlertSystem(alert_threshold=70)
    print("✅ Alert system initialized")
    
    print("\nPhase 2 features ready for integration!")
