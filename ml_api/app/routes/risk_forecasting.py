from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.risk_forecasting_service import RiskForecastingService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize risk forecasting service
risk_service = RiskForecastingService()

class HealthMetrics(BaseModel):
    weight: float
    height: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    cholesterol_total: Optional[float] = None
    cholesterol_hdl: Optional[float] = None
    cholesterol_ldl: Optional[float] = None
    blood_glucose: Optional[float] = None
    hba1c: Optional[float] = None

class LifestyleData(BaseModel):
    age: int
    gender: str
    smoking_status: str  # never, former, current
    alcohol_consumption: str  # none, light, moderate, heavy
    physical_activity_level: str  # sedentary, light, moderate, active, very_active
    diet_quality: str  # poor, fair, good, excellent
    stress_level: str  # low, moderate, high
    sleep_hours: float
    family_history: Dict[str, bool]  # diabetes, heart_disease, hypertension, etc.

class RiskForecastRequest(BaseModel):
    health_metrics: HealthMetrics
    lifestyle_data: LifestyleData
    time_horizon_years: int = 5
    user_id: str = None

@router.post("/")
async def forecast_health_risk(request: RiskForecastRequest):
    """
    Forecast long-term health risks based on current metrics and lifestyle.
    
    Args:
        request: RiskForecastRequest containing health and lifestyle data
        
    Returns:
        JSON response with risk forecasts and recommendations
    """
    try:
        # Perform risk forecasting
        result = await risk_service.forecast_risk(
            health_metrics=request.health_metrics.dict(),
            lifestyle_data=request.lifestyle_data.dict(),
            time_horizon=request.time_horizon_years,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Risk forecasting error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk forecasting failed: {str(e)}")

@router.post("/comparison")
async def compare_scenarios(requests: List[RiskForecastRequest]):
    """
    Compare health risk scenarios under different lifestyle conditions.
    
    Args:
        requests: List of RiskForecastRequest objects for different scenarios
        
    Returns:
        JSON response with scenario comparison
    """
    try:
        results = []
        
        for i, request in enumerate(requests):
            try:
                result = await risk_service.forecast_risk(
                    health_metrics=request.health_metrics.dict(),
                    lifestyle_data=request.lifestyle_data.dict(),
                    time_horizon=request.time_horizon_years,
                    user_id=request.user_id
                )
                
                results.append({
                    "scenario_id": i,
                    "scenario_name": f"Scenario {i+1}",
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "scenario_id": i,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": {
                "scenarios": results,
                "total_scenarios": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"Scenario comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario comparison failed: {str(e)}")

@router.get("/risk-factors")
async def get_risk_factors():
    """
    Get information about different health risk factors.
    
    Returns:
        JSON response with risk factor information
    """
    try:
        risk_factors = await risk_service.get_risk_factors()
        
        return {
            "success": True,
            "data": risk_factors
        }
        
    except Exception as e:
        logger.error(f"Get risk factors error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk factors: {str(e)}")

@router.post("/interventions")
async def suggest_interventions(request: RiskForecastRequest):
    """
    Suggest lifestyle interventions to reduce health risks.
    
    Args:
        request: RiskForecastRequest containing current health and lifestyle data
        
    Returns:
        JSON response with intervention suggestions
    """
    try:
        interventions = await risk_service.suggest_interventions(
            health_metrics=request.health_metrics.dict(),
            lifestyle_data=request.lifestyle_data.dict(),
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "data": interventions
        }
        
    except Exception as e:
        logger.error(f"Intervention suggestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intervention suggestion failed: {str(e)}")
