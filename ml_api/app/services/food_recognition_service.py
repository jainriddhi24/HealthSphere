import numpy as np
import logging
from typing import Dict, Any, Optional
import random
import json

logger = logging.getLogger(__name__)

class FoodRecognitionService:
    """
    Service for food recognition using computer vision.
    In production, this would use a trained deep learning model.
    """
    
    def __init__(self):
        self.food_database = self._load_food_database()
        logger.info("Food recognition service initialized")
    
    def _load_food_database(self) -> Dict[str, Dict[str, Any]]:
        """Load food database with nutrition information."""
        return {
            "apple": {
                "calories": 52,
                "protein": 0.3,
                "carbs": 13.8,
                "fat": 0.2,
                "fiber": 2.4,
                "vitamins": ["C", "K"],
                "confidence_threshold": 0.8
            },
            "banana": {
                "calories": 89,
                "protein": 1.1,
                "carbs": 22.8,
                "fat": 0.3,
                "fiber": 2.6,
                "vitamins": ["B6", "C"],
                "confidence_threshold": 0.8
            },
            "chicken_breast": {
                "calories": 165,
                "protein": 31,
                "carbs": 0,
                "fat": 3.6,
                "fiber": 0,
                "vitamins": ["B6", "B12"],
                "confidence_threshold": 0.7
            },
            "salmon": {
                "calories": 208,
                "protein": 25,
                "carbs": 0,
                "fat": 12,
                "fiber": 0,
                "vitamins": ["B12", "D"],
                "confidence_threshold": 0.7
            },
            "rice": {
                "calories": 130,
                "protein": 2.7,
                "carbs": 28,
                "fat": 0.3,
                "fiber": 0.4,
                "vitamins": ["B1", "B3"],
                "confidence_threshold": 0.8
            },
            "broccoli": {
                "calories": 34,
                "protein": 2.8,
                "carbs": 6.6,
                "fat": 0.4,
                "fiber": 2.6,
                "vitamins": ["C", "K"],
                "confidence_threshold": 0.8
            },
            "pizza": {
                "calories": 266,
                "protein": 11,
                "carbs": 33,
                "fat": 10,
                "fiber": 2.3,
                "vitamins": ["B12", "D"],
                "confidence_threshold": 0.9
            },
            "salad": {
                "calories": 20,
                "protein": 2,
                "carbs": 4,
                "fat": 0.2,
                "fiber": 1.5,
                "vitamins": ["A", "C"],
                "confidence_threshold": 0.6
            }
        }
    
    async def recognize_food(self, image_array: np.ndarray, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Recognize food in image and return nutrition information.
        
        Args:
            image_array: Preprocessed image array
            user_id: Optional user ID for personalization
            
        Returns:
            Dictionary with food recognition results
        """
        try:
            # In production, this would use a trained CNN model
            # For now, we'll simulate recognition with mock data
            
            # Simulate image analysis
            food_name, confidence = self._simulate_recognition(image_array)
            
            # Get nutrition information
            nutrition_info = self.food_database.get(food_name, {
                "calories": 200,
                "protein": 10,
                "carbs": 25,
                "fat": 8,
                "fiber": 3,
                "vitamins": ["C"],
                "confidence_threshold": 0.5
            })
            
            # Generate ingredients list
            ingredients = self._generate_ingredients(food_name)
            
            result = {
                "food_name": food_name,
                "confidence": confidence,
                "nutrition": {
                    "calories": nutrition_info["calories"],
                    "protein": nutrition_info["protein"],
                    "carbs": nutrition_info["carbs"],
                    "fat": nutrition_info["fat"],
                    "fiber": nutrition_info["fiber"]
                },
                "vitamins": nutrition_info["vitamins"],
                "ingredients": ingredients,
                "serving_size": "1 serving",
                "health_score": self._calculate_health_score(nutrition_info),
                "allergens": self._detect_allergens(food_name),
                "processing_time_ms": random.randint(200, 800)
            }
            
            logger.info(f"Food recognized: {food_name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Food recognition error: {str(e)}")
            raise Exception(f"Food recognition failed: {str(e)}")
    
    def _simulate_recognition(self, image_array: np.ndarray) -> tuple[str, float]:
        """Simulate food recognition with mock data."""
        # In production, this would use a trained model
        foods = list(self.food_database.keys())
        food_name = random.choice(foods)
        confidence = random.uniform(0.7, 0.95)
        return food_name, confidence
    
    def _generate_ingredients(self, food_name: str) -> list[str]:
        """Generate ingredient list based on food name."""
        ingredient_map = {
            "apple": ["Apple"],
            "banana": ["Banana"],
            "chicken_breast": ["Chicken breast", "Salt", "Pepper"],
            "salmon": ["Salmon fillet", "Lemon", "Dill", "Salt"],
            "rice": ["White rice", "Water", "Salt"],
            "broccoli": ["Broccoli", "Olive oil", "Salt"],
            "pizza": ["Pizza dough", "Tomato sauce", "Mozzarella", "Pepperoni"],
            "salad": ["Mixed greens", "Tomatoes", "Cucumbers", "Olive oil", "Vinegar"]
        }
        return ingredient_map.get(food_name, ["Unknown ingredients"])
    
    def _calculate_health_score(self, nutrition_info: Dict[str, Any]) -> int:
        """Calculate health score based on nutrition information."""
        score = 100
        
        # Penalize high calories
        if nutrition_info["calories"] > 300:
            score -= 20
        elif nutrition_info["calories"] > 200:
            score -= 10
        
        # Reward high protein
        if nutrition_info["protein"] > 20:
            score += 10
        elif nutrition_info["protein"] > 10:
            score += 5
        
        # Penalize high fat
        if nutrition_info["fat"] > 15:
            score -= 15
        elif nutrition_info["fat"] > 10:
            score -= 10
        
        # Reward fiber
        if nutrition_info["fiber"] > 5:
            score += 10
        elif nutrition_info["fiber"] > 2:
            score += 5
        
        return max(0, min(100, score))
    
    def _detect_allergens(self, food_name: str) -> list[str]:
        """Detect potential allergens in food."""
        allergen_map = {
            "pizza": ["gluten", "dairy"],
            "salmon": ["fish"],
            "chicken_breast": []
        }
        return allergen_map.get(food_name, [])
    
    async def get_nutrition_info(self, food_name: str) -> Dict[str, Any]:
        """Get detailed nutrition information for a food item."""
        food_info = self.food_database.get(food_name.lower())
        if not food_info:
            raise ValueError(f"Food '{food_name}' not found in database")
        
        return {
            "food_name": food_name,
            "nutrition": food_info,
            "health_benefits": self._get_health_benefits(food_name),
            "preparation_tips": self._get_preparation_tips(food_name)
        }
    
    def _get_health_benefits(self, food_name: str) -> list[str]:
        """Get health benefits for a food item."""
        benefits_map = {
            "apple": ["Rich in fiber", "Contains antioxidants", "Supports heart health"],
            "banana": ["High in potassium", "Good source of vitamin B6", "Supports digestion"],
            "chicken_breast": ["High-quality protein", "Low in fat", "Rich in B vitamins"],
            "salmon": ["High in omega-3 fatty acids", "Excellent protein source", "Rich in vitamin D"],
            "broccoli": ["High in vitamin C", "Contains antioxidants", "Supports immune system"]
        }
        return benefits_map.get(food_name, ["Nutritious food"])
    
    def _get_preparation_tips(self, food_name: str) -> list[str]:
        """Get preparation tips for a food item."""
        tips_map = {
            "chicken_breast": ["Cook to internal temperature of 165°F", "Let rest before slicing"],
            "salmon": ["Cook until flaky", "Don't overcook"],
            "broccoli": ["Steam for 3-5 minutes", "Keep bright green color"],
            "rice": ["Use 2:1 water to rice ratio", "Let steam after cooking"]
        }
        return tips_map.get(food_name, ["Enjoy fresh"])
