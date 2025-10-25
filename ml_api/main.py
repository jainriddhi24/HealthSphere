from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import food_recognition, activity_detection, risk_forecasting, chat
from app.middleware import logging_middleware

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="HealthSphere ML API",
    description="AI-powered health and fitness analysis services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Include routers
app.include_router(food_recognition.router, prefix="/food-recognition", tags=["Food Recognition"])
app.include_router(activity_detection.router, prefix="/activity-detect", tags=["Activity Detection"])
app.include_router(risk_forecasting.router, prefix="/risk-forecast", tags=["Risk Forecasting"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])

@app.get("/")
async def root():
    return {
        "message": "HealthSphere ML API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "food_recognition": "/food-recognition",
            "activity_detection": "/activity-detect", 
            "risk_forecasting": "/risk-forecast",
            "ai_chat": "/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HealthSphere ML API",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
