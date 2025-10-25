import numpy as np
import logging
from typing import Dict, Any, List, Optional
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class RiskForecastingService:
    """
    Service for forecasting long-term health risks.
    In production, this would use advanced ML models trained on large health datasets.
    """
    
    def __init__(self):
        self.risk_models = {}
        self.scalers = {}
        self._initialize_models()
        logger.info("Risk forecasting service initialized")
    
    def _initialize_models(self):
        """Initialize risk forecasting models."""
        try:
            # Initialize models for different risk types
            risk_types = [
                "diabetes", "cardiovascular", "hypertension", "obesity", "stroke"
            ]
            
            for risk_type in risk_types:
                # Create mock models for demonstration
                self.risk_models[risk_type] = RandomForestRegressor(
                    n_estimators=100, random_state=42
                )
                self.scalers[risk_type] = StandardScaler()
                
                # Generate mock training data
                X_train, y_train = self._generate_mock_training_data(risk_type)
                self.scalers[risk_type].fit(X_train)
                X_train_scaled = self.scalers[risk_type].transform(X_train)
                self.risk_models[risk_type].fit(X_train_scaled, y_train)
            
            logger.info("Risk forecasting models initialized")
        except Exception as e:
            logger.error(f"Failed to initialize models: {str(e)}")
    
    def _generate_mock_training_data(self, risk_type: str) -> tuple[np.ndarray, np.ndarray]:
        """Generate mock training data for demonstration."""
        n_samples = 1000
        n_features = 15  # Health metrics + lifestyle factors
        
        X = np.random.randn(n_samples, n_features)
        
        # Generate realistic risk scores based on risk type
        if risk_type == "diabetes":
            y = np.random.uniform(0, 0.3, n_samples)  # 0-30% risk
        elif risk_type == "cardiovascular":
            y = np.random.uniform(0, 0.25, n_samples)  # 0-25% risk
        elif risk_type == "hypertension":
            y = np.random.uniform(0, 0.4, n_samples)   # 0-40% risk
        elif risk_type == "obesity":
            y = np.random.uniform(0, 0.5, n_samples)  # 0-50% risk
        else:  # stroke
            y = np.random.uniform(0, 0.15, n_samples) # 0-15% risk
        
        return X, y
    
    async def forecast_risk(
        self,
        health_metrics: Dict[str, Any],
        lifestyle_data: Dict[str, Any],
        time_horizon: int = 5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Forecast health risks based on current metrics and lifestyle.
        
        Args:
            health_metrics: Current health measurements
            lifestyle_data: Lifestyle and demographic information
            time_horizon: Time horizon for forecasting in years
            user_id: Optional user ID for personalization
            
        Returns:
            Dictionary with risk forecasts and recommendations
        """
        try:
            # Extract features for risk assessment
            features = self._extract_features(health_metrics, lifestyle_data)
            
            # Calculate risks for different conditions
            risk_predictions = {}
            for risk_type in self.risk_models.keys():
                if risk_type in self.risk_models and risk_type in self.scalers:
                    features_scaled = self.scalers[risk_type].transform([features])
                    risk_score = self.risk_models[risk_type].predict(features_scaled)[0]
                    risk_predictions[risk_type] = max(0, min(1, risk_score))
                else:
                    risk_predictions[risk_type] = self._mock_risk_calculation(
                        risk_type, health_metrics, lifestyle_data
                    )
            
            # Calculate overall health score
            overall_score = self._calculate_overall_health_score(risk_predictions)
            
            # Generate risk factors
            risk_factors = self._identify_risk_factors(health_metrics, lifestyle_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_predictions, risk_factors, health_metrics, lifestyle_data
            )
            
            result = {
                "time_horizon_years": time_horizon,
                "overall_health_score": overall_score,
                "risk_predictions": {
                    risk_type: {
                        "probability": float(risk_score),
                        "risk_level": self._categorize_risk(risk_score),
                        "trend": self._predict_trend(risk_type, risk_score)
                    }
                    for risk_type, risk_score in risk_predictions.items()
                },
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "confidence_interval": {
                    "lower": 0.8,
                    "upper": 0.95
                },
                "last_updated": "2024-01-01T00:00:00Z"
            }
            
            logger.info(f"Risk forecast completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Risk forecasting error: {str(e)}")
            raise Exception(f"Risk forecasting failed: {str(e)}")
    
    def _extract_features(
        self, 
        health_metrics: Dict[str, Any], 
        lifestyle_data: Dict[str, Any]
    ) -> List[float]:
        """Extract features for risk assessment."""
        features = []
        
        # Health metrics features
        features.extend([
            health_metrics.get("weight", 70),
            health_metrics.get("height", 170),
            health_metrics.get("blood_pressure_systolic", 120),
            health_metrics.get("blood_pressure_diastolic", 80),
            health_metrics.get("heart_rate", 70),
            health_metrics.get("cholesterol_total", 200),
            health_metrics.get("cholesterol_hdl", 50),
            health_metrics.get("cholesterol_ldl", 120),
            health_metrics.get("blood_glucose", 90),
            health_metrics.get("hba1c", 5.5)
        ])
        
        # Lifestyle features (encoded)
        features.extend([
            lifestyle_data.get("age", 40),
            1 if lifestyle_data.get("gender") == "male" else 0,
            self._encode_smoking_status(lifestyle_data.get("smoking_status", "never")),
            self._encode_activity_level(lifestyle_data.get("physical_activity_level", "moderate")),
            self._encode_diet_quality(lifestyle_data.get("diet_quality", "fair")),
            lifestyle_data.get("sleep_hours", 7)
        ])
        
        return features
    
    def _encode_smoking_status(self, status: str) -> int:
        """Encode smoking status as numeric value."""
        encoding = {"never": 0, "former": 1, "current": 2}
        return encoding.get(status, 0)
    
    def _encode_activity_level(self, level: str) -> int:
        """Encode physical activity level as numeric value."""
        encoding = {
            "sedentary": 0, "light": 1, "moderate": 2, 
            "active": 3, "very_active": 4
        }
        return encoding.get(level, 2)
    
    def _encode_diet_quality(self, quality: str) -> int:
        """Encode diet quality as numeric value."""
        encoding = {"poor": 0, "fair": 1, "good": 2, "excellent": 3}
        return encoding.get(quality, 1)
    
    def _mock_risk_calculation(
        self, 
        risk_type: str, 
        health_metrics: Dict[str, Any], 
        lifestyle_data: Dict[str, Any]
    ) -> float:
        """Calculate mock risk score when model is not available."""
        base_risk = 0.1
        
        # Age factor
        age = lifestyle_data.get("age", 40)
        if age > 65:
            base_risk += 0.1
        elif age > 45:
            base_risk += 0.05
        
        # Blood pressure factor
        bp_systolic = health_metrics.get("blood_pressure_systolic", 120)
        if bp_systolic > 140:
            base_risk += 0.15
        elif bp_systolic > 130:
            base_risk += 0.08
        
        # Weight factor
        weight = health_metrics.get("weight", 70)
        height = health_metrics.get("height", 170)
        bmi = weight / ((height / 100) ** 2)
        if bmi > 30:
            base_risk += 0.12
        elif bmi > 25:
            base_risk += 0.06
        
        # Activity level factor
        activity_level = lifestyle_data.get("physical_activity_level", "moderate")
        if activity_level == "sedentary":
            base_risk += 0.08
        elif activity_level in ["very_active", "active"]:
            base_risk -= 0.05
        
        return max(0, min(1, base_risk))
    
    def _calculate_overall_health_score(self, risk_predictions: Dict[str, float]) -> int:
        """Calculate overall health score from risk predictions."""
        # Convert risks to health score (0-100)
        avg_risk = sum(risk_predictions.values()) / len(risk_predictions)
        health_score = int((1 - avg_risk) * 100)
        return max(0, min(100, health_score))
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into risk levels."""
        if risk_score < 0.1:
            return "low"
        elif risk_score < 0.3:
            return "moderate"
        else:
            return "high"
    
    def _predict_trend(self, risk_type: str, current_risk: float) -> str:
        """Predict risk trend based on current risk level."""
        if current_risk < 0.1:
            return "stable"
        elif current_risk < 0.3:
            return "increasing"
        else:
            return "rapidly_increasing"
    
    def _identify_risk_factors(
        self, 
        health_metrics: Dict[str, Any], 
        lifestyle_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify key risk factors."""
        risk_factors = []
        
        # Age risk
        age = lifestyle_data.get("age", 40)
        if age > 65:
            risk_factors.append({
                "factor": "age",
                "level": "high",
                "description": f"Age {age} increases risk for multiple conditions"
            })
        
        # Blood pressure risk
        bp_systolic = health_metrics.get("blood_pressure_systolic", 120)
        if bp_systolic > 140:
            risk_factors.append({
                "factor": "hypertension",
                "level": "high",
                "description": "High blood pressure significantly increases cardiovascular risk"
            })
        
        # Weight risk
        weight = health_metrics.get("weight", 70)
        height = health_metrics.get("height", 170)
        bmi = weight / ((height / 100) ** 2)
        if bmi > 30:
            risk_factors.append({
                "factor": "obesity",
                "level": "high",
                "description": "Obesity increases risk for diabetes and cardiovascular disease"
            })
        
        # Activity level risk
        activity_level = lifestyle_data.get("physical_activity_level", "moderate")
        if activity_level == "sedentary":
            risk_factors.append({
                "factor": "physical_inactivity",
                "level": "moderate",
                "description": "Low physical activity increases risk for multiple conditions"
            })
        
        return risk_factors
    
    def _generate_recommendations(
        self,
        risk_predictions: Dict[str, float],
        risk_factors: List[Dict[str, Any]],
        health_metrics: Dict[str, Any],
        lifestyle_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Blood pressure recommendations
        bp_systolic = health_metrics.get("blood_pressure_systolic", 120)
        if bp_systolic > 130:
            recommendations.append({
                "category": "cardiovascular",
                "priority": "high",
                "action": "Monitor blood pressure regularly and consider lifestyle changes",
                "specific_steps": [
                    "Reduce sodium intake",
                    "Increase physical activity",
                    "Manage stress levels",
                    "Consider consulting a healthcare provider"
                ]
            })
        
        # Weight management recommendations
        weight = health_metrics.get("weight", 70)
        height = health_metrics.get("height", 170)
        bmi = weight / ((height / 100) ** 2)
        if bmi > 25:
            recommendations.append({
                "category": "weight_management",
                "priority": "moderate",
                "action": "Focus on sustainable weight management",
                "specific_steps": [
                    "Create a calorie deficit through diet and exercise",
                    "Focus on whole foods and portion control",
                    "Increase daily physical activity",
                    "Set realistic weight loss goals"
                ]
            })
        
        # Physical activity recommendations
        activity_level = lifestyle_data.get("physical_activity_level", "moderate")
        if activity_level in ["sedentary", "light"]:
            recommendations.append({
                "category": "physical_activity",
                "priority": "high",
                "action": "Increase daily physical activity",
                "specific_steps": [
                    "Start with 10-15 minutes of daily walking",
                    "Gradually increase to 150 minutes of moderate activity per week",
                    "Include strength training 2-3 times per week",
                    "Find activities you enjoy to maintain consistency"
                ]
            })
        
        return recommendations
    
    async def get_risk_factors(self) -> Dict[str, Any]:
        """Get information about different health risk factors."""
        return {
            "risk_factors": [
                {
                    "name": "age",
                    "description": "Age is a non-modifiable risk factor",
                    "impact": "Increases risk for most chronic conditions",
                    "modifiable": False
                },
                {
                    "name": "blood_pressure",
                    "description": "High blood pressure increases cardiovascular risk",
                    "impact": "Major risk factor for heart disease and stroke",
                    "modifiable": True
                },
                {
                    "name": "weight",
                    "description": "Excess weight increases risk for multiple conditions",
                    "impact": "Increases risk for diabetes, heart disease, and joint problems",
                    "modifiable": True
                },
                {
                    "name": "physical_activity",
                    "description": "Low physical activity increases health risks",
                    "impact": "Increases risk for cardiovascular disease and diabetes",
                    "modifiable": True
                },
                {
                    "name": "smoking",
                    "description": "Smoking significantly increases health risks",
                    "impact": "Major risk factor for cancer, heart disease, and lung disease",
                    "modifiable": True
                }
            ],
            "total_factors": 5
        }
    
    async def suggest_interventions(
        self,
        health_metrics: Dict[str, Any],
        lifestyle_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Suggest lifestyle interventions to reduce health risks."""
        interventions = []
        
        # Blood pressure interventions
        bp_systolic = health_metrics.get("blood_pressure_systolic", 120)
        if bp_systolic > 130:
            interventions.append({
                "type": "dietary",
                "name": "DASH Diet",
                "description": "Dietary Approaches to Stop Hypertension",
                "expected_benefit": "Reduce systolic BP by 5-10 mmHg",
                "difficulty": "moderate",
                "time_to_effect": "2-4 weeks"
            })
        
        # Weight management interventions
        weight = health_metrics.get("weight", 70)
        height = health_metrics.get("height", 170)
        bmi = weight / ((height / 100) ** 2)
        if bmi > 25:
            interventions.append({
                "type": "lifestyle",
                "name": "Calorie Restriction",
                "description": "Moderate calorie reduction for sustainable weight loss",
                "expected_benefit": "5-10% weight loss over 6 months",
                "difficulty": "moderate",
                "time_to_effect": "4-8 weeks"
            })
        
        # Physical activity interventions
        activity_level = lifestyle_data.get("physical_activity_level", "moderate")
        if activity_level in ["sedentary", "light"]:
            interventions.append({
                "type": "exercise",
                "name": "Progressive Walking Program",
                "description": "Gradually increase daily walking duration",
                "expected_benefit": "Improve cardiovascular fitness and reduce disease risk",
                "difficulty": "easy",
                "time_to_effect": "2-3 weeks"
            })
        
        return {
            "interventions": interventions,
            "total_count": len(interventions),
            "personalization_level": "high" if user_id else "moderate"
        }
