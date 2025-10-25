from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import base64
import io
from PIL import Image
import numpy as np
from typing import Dict, Any
import logging

from services.food_recognition_service import FoodRecognitionService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize food recognition service
food_service = FoodRecognitionService()

@router.post("/")
async def recognize_food(
    image: UploadFile = File(...),
    user_id: str = Form(None)
):
    """
    Recognize food items in an uploaded image and return nutrition information.
    
    Args:
        image: Image file containing food
        user_id: Optional user ID for personalization
        
    Returns:
        JSON response with food recognition results and nutrition data
    """
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await image.read()
        image_pil = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image_pil.mode != 'RGB':
            image_pil = image_pil.convert('RGB')
        
        # Resize image for processing
        image_pil = image_pil.resize((224, 224))
        
        # Convert to numpy array
        image_array = np.array(image_pil)
        
        # Perform food recognition
        result = await food_service.recognize_food(image_array, user_id)
        
        return JSONResponse(content={
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Food recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Food recognition failed: {str(e)}")

@router.post("/batch")
async def recognize_food_batch(
    images: list[UploadFile] = File(...),
    user_id: str = Form(None)
):
    """
    Recognize food items in multiple images.
    
    Args:
        images: List of image files
        user_id: Optional user ID for personalization
        
    Returns:
        JSON response with batch recognition results
    """
    try:
        results = []
        
        for image in images:
            if not image.content_type.startswith('image/'):
                continue
                
            # Process each image
            image_data = await image.read()
            image_pil = Image.open(io.BytesIO(image_data))
            
            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')
                
            image_pil = image_pil.resize((224, 224))
            image_array = np.array(image_pil)
            
            result = await food_service.recognize_food(image_array, user_id)
            results.append({
                "filename": image.filename,
                "result": result
            })
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "results": results,
                "total_images": len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"Batch food recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch recognition failed: {str(e)}")

@router.get("/nutrition/{food_name}")
async def get_nutrition_info(food_name: str):
    """
    Get detailed nutrition information for a specific food item.
    
    Args:
        food_name: Name of the food item
        
    Returns:
        JSON response with nutrition data
    """
    try:
        nutrition_data = await food_service.get_nutrition_info(food_name)
        
        return JSONResponse(content={
            "success": True,
            "data": nutrition_data
        })
        
    except Exception as e:
        logger.error(f"Nutrition lookup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Nutrition lookup failed: {str(e)}")
