"""
REST API for Supplier Risk Intelligence System
Enable integration with external systems (SAP, Oracle, Salesforce)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
sys.path.insert(0, '.')

from data_collector import DataCollector
from risk_scoring import RiskScoringEngine

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Supplier Risk Intelligence API",
    description="Real-time supplier risk assessment API",
    version="1.0.0"
)

# Initialize services
collector = DataCollector()
scoring_engine = RiskScoringEngine()


# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class CompanyRequest(BaseModel):
    """Request model for supplier risk assessment"""
    company_name: str
    include_news: bool = True
    include_financial: bool = True


class RiskScoreResponse(BaseModel):
    """Response model for risk scores"""
    company: str
    risk_score: float
    risk_level: str
    news_risk: float
    financial_risk: float
    recent_articles: int
    assessment_date: datetime


class BatchCompaniesRequest(BaseModel):
    """Request for batch assessment"""
    companies: List[str]
    include_trends: bool = False


class SupplierAlert(BaseModel):
    """Alert notification model"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    company: str
    risk_score: float
    timestamp: datetime
    message: str
    action: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Status of the service
    """
    return {
        "status": "healthy",
        "service": "Supplier Risk Intelligence API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/risk/assess")
async def assess_supplier_risk(request: CompanyRequest) -> RiskScoreResponse:
    """
    Assess risk for a single supplier
    
    Args:
        request: CompanyRequest with company name and options
        
    Returns:
        RiskScoreResponse: Complete risk assessment
        
    Example:
        POST /api/v1/risk/assess
        {
            "company_name": "Apple",
            "include_news": true,
            "include_financial": true
        }
    """
    try:
        # Collect data
        news_df, financial_df = collector.collect_all_data()
        
        # Calculate risk
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df, [request.company_name])
        
        if risk_scores.empty:
            raise HTTPException(status_code=404, detail=f"Company '{request.company_name}' not found")
        
        row = risk_scores.iloc[0]
        
        return RiskScoreResponse(
            company=row['company'],
            risk_score=row['risk_score'],
            risk_level=row['risk_level'],
            news_risk=row['news_risk'],
            financial_risk=row['financial_risk'],
            recent_articles=row['recent_articles'],
            assessment_date=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/risk/batch")
async def assess_batch_suppliers(request: BatchCompaniesRequest) -> List[RiskScoreResponse]:
    """
    Assess risk for multiple suppliers
    
    Args:
        request: BatchCompaniesRequest with list of companies
        
    Returns:
        List[RiskScoreResponse]: Risk assessments for all companies
        
    Example:
        POST /api/v1/risk/batch
        {
            "companies": ["Apple", "Samsung", "Intel"],
            "include_trends": true
        }
    """
    try:
        # Collect data
        news_df, financial_df = collector.collect_all_data()
        
        # Calculate risk for all companies
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df, request.companies)
        
        results = []
        for idx, row in risk_scores.iterrows():
            results.append(RiskScoreResponse(
                company=row['company'],
                risk_score=row['risk_score'],
                risk_level=row['risk_level'],
                news_risk=row['news_risk'],
                financial_risk=row['financial_risk'],
                recent_articles=row['recent_articles'],
                assessment_date=datetime.now()
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk/{company_name}")
async def get_supplier_risk(company_name: str) -> RiskScoreResponse:
    """
    Get risk for a specific supplier
    
    Args:
        company_name: Name of the supplier
        
    Returns:
        RiskScoreResponse: Risk assessment
        
    Example:
        GET /api/v1/risk/Apple
    """
    try:
        news_df, financial_df = collector.collect_all_data()
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df, [company_name])
        
        if risk_scores.empty:
            raise HTTPException(status_code=404, detail=f"Company '{company_name}' not found")
        
        row = risk_scores.iloc[0]
        
        return RiskScoreResponse(
            company=row['company'],
            risk_score=row['risk_score'],
            risk_level=row['risk_level'],
            news_risk=row['news_risk'],
            financial_risk=row['financial_risk'],
            recent_articles=row['recent_articles'],
            assessment_date=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risks/all")
async def get_all_risks() -> List[RiskScoreResponse]:
    """
    Get risk scores for all monitored suppliers
    
    Returns:
        List[RiskScoreResponse]: All risk assessments
        
    Example:
        GET /api/v1/risks/all
    """
    try:
        news_df, financial_df = collector.collect_all_data()
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df)
        
        results = []
        for idx, row in risk_scores.iterrows():
            results.append(RiskScoreResponse(
                company=row['company'],
                risk_score=row['risk_score'],
                risk_level=row['risk_level'],
                news_risk=row['news_risk'],
                financial_risk=row['financial_risk'],
                recent_articles=row['recent_articles'],
                assessment_date=datetime.now()
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risks/critical")
async def get_critical_risks() -> List[RiskScoreResponse]:
    """
    Get only critical risk suppliers (score >= 75)
    
    Returns:
        List[RiskScoreResponse]: Critical risk assessments
        
    Example:
        GET /api/v1/risks/critical
    """
    try:
        news_df, financial_df = collector.collect_all_data()
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df)
        
        critical = risk_scores[risk_scores['risk_score'] >= 75]
        
        results = []
        for idx, row in critical.iterrows():
            results.append(RiskScoreResponse(
                company=row['company'],
                risk_score=row['risk_score'],
                risk_level=row['risk_level'],
                news_risk=row['news_risk'],
                financial_risk=row['financial_risk'],
                recent_articles=row['recent_articles'],
                assessment_date=datetime.now()
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_statistics() -> dict:
    """
    Get portfolio statistics
    
    Returns:
        dict: Portfolio statistics and summary
        
    Example:
        GET /api/v1/stats
    """
    try:
        news_df, financial_df = collector.collect_all_data()
        risk_scores = scoring_engine.score_suppliers(news_df, financial_df)
        
        return {
            "total_suppliers": len(risk_scores),
            "average_risk_score": float(risk_scores['risk_score'].mean()),
            "median_risk_score": float(risk_scores['risk_score'].median()),
            "critical_count": len(risk_scores[risk_scores['risk_score'] >= 75]),
            "high_count": len(risk_scores[(risk_scores['risk_score'] >= 60) & (risk_scores['risk_score'] < 75)]),
            "medium_count": len(risk_scores[(risk_scores['risk_score'] >= 40) & (risk_scores['risk_score'] < 60)]),
            "low_count": len(risk_scores[risk_scores['risk_score'] < 40]),
            "risk_level_distribution": risk_scores['risk_level'].value_counts().to_dict(),
            "assessment_timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Generic exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# API DOCUMENTATION & USAGE EXAMPLES
# ============================================================================

"""
HOW TO USE THE API

1. START THE SERVER
   $ pip install fastapi uvicorn
   $ uvicorn api:app --reload --host 0.0.0.0 --port 8000

2. API DOCUMENTATION
   Interactive docs: http://localhost:8000/docs
   Alternative docs: http://localhost:8000/redoc

3. EXAMPLE REQUESTS

A) Health Check
   GET http://localhost:8000/health
   
   Response:
   {
     "status": "healthy",
     "service": "Supplier Risk Intelligence API",
     "version": "1.0.0",
     "timestamp": "2024-03-23T18:00:00"
   }

B) Get Risk for Single Supplier
   POST http://localhost:8000/api/v1/risk/assess
   
   Body:
   {
     "company_name": "Apple",
     "include_news": true,
     "include_financial": true
   }
   
   Response:
   {
     "company": "Apple",
     "risk_score": 42.5,
     "risk_level": "🟡 MEDIUM",
     "news_risk": 35.0,
     "financial_risk": 50.0,
     "recent_articles": 12,
     "assessment_date": "2024-03-23T18:00:00"
   }

C) Get Risk for Multiple Suppliers
   POST http://localhost:8000/api/v1/risk/batch
   
   Body:
   {
     "companies": ["Apple", "Samsung", "Intel"],
     "include_trends": true
   }
   
   Response:
   [
     { "company": "Apple", "risk_score": 42.5, ... },
     { "company": "Samsung", "risk_score": 65.2, ... },
     { "company": "Intel", "risk_score": 55.1, ... }
   ]

D) Get All Suppliers
   GET http://localhost:8000/api/v1/risks/all
   
   Response: [All supplier risk scores]

E) Get Critical Risks Only
   GET http://localhost:8000/api/v1/risks/critical
   
   Response: [Only suppliers with score >= 75]

F) Get Portfolio Statistics
   GET http://localhost:8000/api/v1/stats
   
   Response:
   {
     "total_suppliers": 20,
     "average_risk_score": 45.3,
     "critical_count": 2,
     "high_count": 3,
     ...
   }

4. INTEGRATION EXAMPLES

Python Integration:
   import requests
   
   response = requests.post(
       'http://localhost:8000/api/v1/risk/assess',
       json={'company_name': 'Apple'}
   )
   risk = response.json()

JavaScript Integration:
   fetch('http://localhost:8000/api/v1/risk/Apple')
     .then(r => r.json())
     .then(data => console.log(data))

cURL:
   curl -X GET http://localhost:8000/api/v1/risk/Apple

5. DEPLOYMENT

Development:
   $ uvicorn api:app --reload

Production:
   $ gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

With Nginx:
   server {
       listen 80;
       server_name api.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
       }
   }

6. RATE LIMITING (Production)

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/risk/{company}")
@limiter.limit("100/minute")
async def get_supplier_risk(company_name: str):
    ...

7. AUTHENTICATION (For Private APIs)

from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/v1/risk/{company}")
async def get_supplier_risk(
    company_name: str,
    credentials: HTTPAuthCredentials = Depends(security)
):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401)
    ...
"""

if __name__ == "__main__":
    import uvicorn
    
    print("""
    🚀 STARTING SUPPLIER RISK API
    
    Interactive docs: http://localhost:8000/docs
    Alternative docs: http://localhost:8000/redoc
    
    Endpoints:
    - GET /health
    - POST /api/v1/risk/assess
    - POST /api/v1/risk/batch
    - GET /api/v1/risk/{company}
    - GET /api/v1/risks/all
    - GET /api/v1/risks/critical
    - GET /api/v1/stats
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
