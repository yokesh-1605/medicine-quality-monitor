from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import pandas as pd

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Medicine Quality Monitor API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Load ML model and scaler
model = None
scaler = None

def load_ml_model():
    """Load the trained ML model and scaler"""
    global model, scaler
    try:
        model_path = ROOT_DIR / 'models' / 'anomaly_model.joblib'
        scaler_path = ROOT_DIR / 'models' / 'scaler.joblib'
        
        if model_path.exists() and scaler_path.exists():
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            logger.info("ML model and scaler loaded successfully!")
        else:
            logger.warning("ML model files not found. Please run train_model.py first.")
    except Exception as e:
        logger.error(f"Error loading ML model: {e}")

# Pydantic Models
class VerifyRequest(BaseModel):
    code: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class VerifyResponse(BaseModel):
    status: str
    reason: str
    confidence: float
    batch_info: Optional[Dict[str, Any]] = None

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

class LogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    batch_code: str
    status: str
    reason: str
    confidence: float
    location: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None

class Medicine(BaseModel):
    id: str
    batch_id: str
    name: str
    manufacturer: str
    manufacturer_score: float
    expiry_date: str
    status: str
    scan_count: int

# Helper functions
def calculate_days_to_expiry(expiry_date_str: str) -> int:
    """Calculate days until expiry"""
    try:
        expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (expiry_date - now).days
    except:
        return -999  # Invalid date

def predict_anomaly(medicine_data: dict) -> tuple[bool, float]:
    """Use ML model to predict if medicine is anomalous"""
    if model is None or scaler is None:
        return False, 0.5  # Default if model not loaded
    
    try:
        # Prepare features for the model
        features = [
            medicine_data.get('manufacturer_score', 7.0),
            calculate_days_to_expiry(medicine_data.get('expiry_date', '')),
            medicine_data.get('scan_count', 1),
            medicine_data.get('distinct_locations', 1),
            medicine_data.get('batch_age_days', 180),
            medicine_data.get('verification_ratio', 0.8)
        ]
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Predict
        prediction = model.predict(features_scaled)[0]
        anomaly_score = model.decision_function(features_scaled)[0]
        
        # Convert prediction: -1 means anomaly, 1 means normal
        is_anomaly = prediction == -1
        
        # Convert anomaly score to confidence (0 to 1)
        # Anomaly scores are typically between -0.5 and 0.5
        confidence = max(0.1, min(0.9, (1 - anomaly_score) / 2))
        
        return is_anomaly, confidence
    
    except Exception as e:
        logger.error(f"Error in anomaly prediction: {e}")
        return False, 0.5

async def log_verification(batch_code: str, status: str, reason: str, confidence: float, location: dict = None):
    """Log verification attempt to database"""
    try:
        log_entry = LogEntry(
            batch_code=batch_code,
            status=status,
            reason=reason,
            confidence=confidence,
            location=location
        )
        await db.logs.insert_one(log_entry.dict())
    except Exception as e:
        logger.error(f"Error logging verification: {e}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Medicine Quality Monitor API", "version": "1.0.0"}

@api_router.post("/verify", response_model=VerifyResponse)
async def verify_medicine(request: VerifyRequest):
    """Verify a medicine batch code"""
    try:
        batch_code = request.code.strip().upper()
        
        # Look up medicine in database
        medicine = await db.medicines.find_one({"batch_id": batch_code})
        
        if not medicine:
            # Medicine not found in database
            response = VerifyResponse(
                status="Fake ❌",
                reason="Batch code not found in official database",
                confidence=0.95
            )
            await log_verification(batch_code, "fake", response.reason, response.confidence,
                                 {"lat": request.lat, "lng": request.lng} if request.lat and request.lng else None)
            return response
        
        # Check if expired
        days_to_expiry = calculate_days_to_expiry(medicine['expiry_date'])
        if days_to_expiry < 0:
            response = VerifyResponse(
                status="Expired ⚠️",
                reason=f"Medicine expired {abs(days_to_expiry)} days ago",
                confidence=0.99,
                batch_info={
                    "name": medicine['name'],
                    "manufacturer": medicine['manufacturer'],
                    "expiry_date": medicine['expiry_date']
                }
            )
            await log_verification(batch_code, "expired", response.reason, response.confidence,
                                 {"lat": request.lat, "lng": request.lng} if request.lat and request.lng else None)
            return response
        
        # Check if known fake
        if medicine.get('status') == 'fake':
            response = VerifyResponse(
                status="Fake ❌",
                reason="Batch identified as counterfeit in our database",
                confidence=0.98
            )
            await log_verification(batch_code, "fake", response.reason, response.confidence,
                                 {"lat": request.lat, "lng": request.lng} if request.lat and request.lng else None)
            return response
        
        # Update scan count
        await db.medicines.update_one(
            {"batch_id": batch_code},
            {"$inc": {"scan_count": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Run anomaly detection
        medicine_data = {
            'manufacturer_score': medicine.get('manufacturer_score', 7.0),
            'expiry_date': medicine.get('expiry_date'),
            'scan_count': medicine.get('scan_count', 0) + 1,  # Include this scan
            'distinct_locations': medicine.get('distinct_locations', 1),
            'batch_age_days': 180,  # Default value
            'verification_ratio': 0.8  # Default value
        }
        
        is_anomaly, confidence = predict_anomaly(medicine_data)
        
        if is_anomaly and confidence > 0.7:
            response = VerifyResponse(
                status="Suspected Counterfeit 🤔",
                reason=f"AI anomaly detection flagged this batch (confidence: {confidence:.1%})",
                confidence=confidence,
                batch_info={
                    "name": medicine['name'],
                    "manufacturer": medicine['manufacturer'],
                    "expiry_date": medicine['expiry_date'],
                    "scan_count": medicine.get('scan_count', 0) + 1
                }
            )
            await log_verification(batch_code, "suspected", response.reason, response.confidence,
                                 {"lat": request.lat, "lng": request.lng} if request.lat and request.lng else None)
            return response
        
        # Medicine is valid
        response = VerifyResponse(
            status="Valid ✅",
            reason=f"Medicine is authentic and valid (expires in {days_to_expiry} days)",
            confidence=1.0 - confidence if is_anomaly else 0.95,
            batch_info={
                "name": medicine['name'],
                "manufacturer": medicine['manufacturer'],
                "expiry_date": medicine['expiry_date'],
                "scan_count": medicine.get('scan_count', 0) + 1
            }
        )
        
        await log_verification(batch_code, "valid", response.reason, response.confidence,
                             {"lat": request.lat, "lng": request.lng} if request.lat and request.lng else None)
        return response
        
    except Exception as e:
        logger.error(f"Error in verify_medicine: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        # Simple authentication (in production, use proper password hashing)
        admin_user = await db.admin_users.find_one({"username": request.username})
        
        if not admin_user or admin_user.get('password') != request.password:
            return AdminLoginResponse(
                success=False,
                message="Invalid username or password"
            )
        
        # In a real app, generate a proper JWT token
        token = f"admin_token_{uuid.uuid4()}"
        
        return AdminLoginResponse(
            success=True,
            message="Login successful",
            token=token
        )
        
    except Exception as e:
        logger.error(f"Error in admin_login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100):
    """Get verification logs for admin dashboard"""
    try:
        logs = await db.logs.find().sort("timestamp", -1).limit(limit).to_list(length=None)
        return [LogEntry(**log) for log in logs]
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/stats")
async def get_stats():
    """Get statistics for admin dashboard"""
    try:
        # Get log statistics
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_stats = await db.logs.aggregate(pipeline).to_list(length=None)
        
        # Get daily verification counts for the last 7 days
        seven_days_ago = datetime.now(timezone.utc) - pd.Timedelta(days=7)
        
        daily_pipeline = [
            {"$match": {"timestamp": {"$gte": seven_days_ago}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_stats = await db.logs.aggregate(daily_pipeline).to_list(length=None)
        
        # Get total medicines count
        total_medicines = await db.medicines.count_documents({})
        
        return {
            "status_distribution": {item["_id"]: item["count"] for item in status_stats},
            "daily_verifications": daily_stats,
            "total_medicines": total_medicines,
            "total_verifications": sum(item["count"] for item in status_stats)
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load ML model on startup
@app.on_event("startup")
async def startup_event():
    load_ml_model()
    logger.info("Medicine Quality Monitor API started successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()