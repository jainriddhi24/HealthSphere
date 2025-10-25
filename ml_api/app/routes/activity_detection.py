from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from services.activity_detection_service import ActivityDetectionService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize activity detection service
activity_service = ActivityDetectionService()

class ActivityData(BaseModel):
    accelerometer_x: List[float]
    accelerometer_y: List[float]
    accelerometer_z: List[float]
    gyroscope_x: List[float] = []
    gyroscope_y: List[float] = []
    gyroscope_z: List[float] = []
    timestamp: List[float]
    user_id: str = None

class ActivityRequest(BaseModel):
    data: ActivityData
    duration_seconds: int
    user_id: str = None

@router.post("/")
async def detect_activity(request: ActivityRequest):
    """
    Detect physical activity from sensor data.
    
    Args:
        request: ActivityRequest containing sensor data
        
    Returns:
        JSON response with detected activity and confidence
    """
    try:
        # Validate input data
        if len(request.data.accelerometer_x) < 10:
            raise HTTPException(status_code=400, detail="Insufficient sensor data")
        
        # Perform activity detection
        result = await activity_service.detect_activity(
            accelerometer_data={
                'x': request.data.accelerometer_x,
                'y': request.data.accelerometer_y,
                'z': request.data.accelerometer_z
            },
            gyroscope_data={
                'x': request.data.gyroscope_x,
                'y': request.data.gyroscope_y,
                'z': request.data.gyroscope_z
            },
            duration=request.duration_seconds,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Activity detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Activity detection failed: {str(e)}")

@router.post("/batch")
async def detect_activity_batch(requests: List[ActivityRequest]):
    """
    Detect activities from multiple sensor data samples.
    
    Args:
        requests: List of ActivityRequest objects
        
    Returns:
        JSON response with batch detection results
    """
    try:
        results = []
        
        for i, request in enumerate(requests):
            try:
                result = await activity_service.detect_activity(
                    accelerometer_data={
                        'x': request.data.accelerometer_x,
                        'y': request.data.accelerometer_y,
                        'z': request.data.accelerometer_z
                    },
                    gyroscope_data={
                        'x': request.data.gyroscope_x,
                        'y': request.data.gyroscope_y,
                        'z': request.data.gyroscope_z
                    },
                    duration=request.duration_seconds,
                    user_id=request.user_id
                )
                
                results.append({
                    "sample_id": i,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "sample_id": i,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": {
                "results": results,
                "total_samples": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"Batch activity detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")

@router.get("/activities")
async def get_supported_activities():
    """
    Get list of supported activity types.
    
    Returns:
        JSON response with supported activities
    """
    try:
        activities = await activity_service.get_supported_activities()
        
        return {
            "success": True,
            "data": activities
        }
        
    except Exception as e:
        logger.error(f"Get activities error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get activities: {str(e)}")
