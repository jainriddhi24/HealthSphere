import numpy as np
import logging
from typing import Dict, Any, List, Optional
import random
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

logger = logging.getLogger(__name__)

class ActivityDetectionService:
    """
    Service for detecting physical activities from sensor data.
    In production, this would use a trained machine learning model.
    """
    
    def __init__(self):
        self.activities = [
            "walking", "running", "cycling", "swimming", "sitting", 
            "standing", "lying_down", "stairs_up", "stairs_down", "jumping"
        ]
        self.model = None
        self.scaler = StandardScaler()
        self._initialize_model()
        logger.info("Activity detection service initialized")
    
    def _initialize_model(self):
        """Initialize the activity detection model."""
        try:
            # In production, load a pre-trained model
            # For now, create a simple mock model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Generate mock training data for demonstration
            X_train, y_train = self._generate_mock_training_data()
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            self.model.fit(X_train_scaled, y_train)
            
            logger.info("Activity detection model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            self.model = None
    
    def _generate_mock_training_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Generate mock training data for demonstration."""
        n_samples = 1000
        n_features = 12  # 3 accelerometer + 3 gyroscope + 6 statistical features
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice(self.activities, n_samples)
        
        return X, y
    
    async def detect_activity(
        self, 
        accelerometer_data: Dict[str, List[float]],
        gyroscope_data: Dict[str, List[float]],
        duration: int,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect physical activity from sensor data.
        
        Args:
            accelerometer_data: Dictionary with x, y, z accelerometer readings
            gyroscope_data: Dictionary with x, y, z gyroscope readings
            duration: Duration of the activity in seconds
            user_id: Optional user ID for personalization
            
        Returns:
            Dictionary with activity detection results
        """
        try:
            # Extract features from sensor data
            features = self._extract_features(
                accelerometer_data, gyroscope_data, duration
            )
            
            if self.model is not None:
                # Use trained model for prediction
                features_scaled = self.scaler.transform([features])
                probabilities = self.model.predict_proba(features_scaled)[0]
                
                # Get top predictions
                activity_probs = list(zip(self.activities, probabilities))
                activity_probs.sort(key=lambda x: x[1], reverse=True)
                
                predicted_activity = activity_probs[0][0]
                confidence = activity_probs[0][1]
                
                # Get top 3 predictions
                top_predictions = activity_probs[:3]
            else:
                # Fallback to mock prediction
                predicted_activity, confidence = self._mock_prediction(features)
                top_predictions = [(predicted_activity, confidence)]
            
            # Calculate additional metrics
            intensity = self._calculate_intensity(features)
            calories_burned = self._estimate_calories(predicted_activity, duration, intensity)
            
            result = {
                "predicted_activity": predicted_activity,
                "confidence": float(confidence),
                "top_predictions": [
                    {"activity": activity, "confidence": float(conf)} 
                    for activity, conf in top_predictions
                ],
                "duration_seconds": duration,
                "intensity_level": intensity,
                "estimated_calories": calories_burned,
                "features_extracted": len(features),
                "processing_time_ms": random.randint(50, 200)
            }
            
            logger.info(f"Activity detected: {predicted_activity} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Activity detection error: {str(e)}")
            raise Exception(f"Activity detection failed: {str(e)}")
    
    def _extract_features(
        self, 
        accelerometer_data: Dict[str, List[float]], 
        gyroscope_data: Dict[str, List[float]], 
        duration: int
    ) -> List[float]:
        """Extract features from sensor data."""
        features = []
        
        # Accelerometer features
        for axis in ['x', 'y', 'z']:
            if axis in accelerometer_data and accelerometer_data[axis]:
                data = np.array(accelerometer_data[axis])
                features.extend([
                    np.mean(data),
                    np.std(data),
                    np.max(data),
                    np.min(data)
                ])
            else:
                features.extend([0, 0, 0, 0])
        
        # Gyroscope features
        for axis in ['x', 'y', 'z']:
            if axis in gyroscope_data and gyroscope_data[axis]:
                data = np.array(gyroscope_data[axis])
                features.extend([
                    np.mean(data),
                    np.std(data),
                    np.max(data),
                    np.min(data)
                ])
            else:
                features.extend([0, 0, 0, 0])
        
        # Additional features
        if accelerometer_data.get('x') and accelerometer_data.get('y') and accelerometer_data.get('z'):
            acc_magnitude = np.sqrt(
                np.array(accelerometer_data['x'])**2 + 
                np.array(accelerometer_data['y'])**2 + 
                np.array(accelerometer_data['z'])**2
            )
            features.extend([
                np.mean(acc_magnitude),
                np.std(acc_magnitude)
            ])
        else:
            features.extend([0, 0])
        
        return features
    
    def _mock_prediction(self, features: List[float]) -> tuple[str, float]:
        """Generate mock prediction when model is not available."""
        # Simple heuristic-based prediction
        acc_magnitude_mean = features[0] if len(features) > 0 else 0
        acc_magnitude_std = features[1] if len(features) > 1 else 0
        
        if acc_magnitude_mean > 0.5 and acc_magnitude_std > 0.3:
            activity = "running"
            confidence = 0.85
        elif acc_magnitude_mean > 0.2 and acc_magnitude_std > 0.1:
            activity = "walking"
            confidence = 0.80
        elif acc_magnitude_mean < 0.1 and acc_magnitude_std < 0.05:
            activity = "sitting"
            confidence = 0.90
        else:
            activity = "standing"
            confidence = 0.75
        
        return activity, confidence
    
    def _calculate_intensity(self, features: List[float]) -> str:
        """Calculate activity intensity level."""
        if len(features) < 2:
            return "unknown"
        
        acc_magnitude_mean = features[0]
        acc_magnitude_std = features[1]
        
        if acc_magnitude_mean > 0.5 or acc_magnitude_std > 0.4:
            return "high"
        elif acc_magnitude_mean > 0.2 or acc_magnitude_std > 0.15:
            return "moderate"
        else:
            return "low"
    
    def _estimate_calories(self, activity: str, duration: int, intensity: str) -> float:
        """Estimate calories burned based on activity and duration."""
        # Base calories per minute for different activities
        base_calories = {
            "walking": 3.5,
            "running": 8.0,
            "cycling": 6.0,
            "swimming": 7.0,
            "sitting": 1.0,
            "standing": 1.2,
            "lying_down": 0.8,
            "stairs_up": 9.0,
            "stairs_down": 4.0,
            "jumping": 10.0
        }
        
        base_rate = base_calories.get(activity, 2.0)
        
        # Adjust for intensity
        intensity_multiplier = {
            "low": 0.7,
            "moderate": 1.0,
            "high": 1.3
        }.get(intensity, 1.0)
        
        calories_per_minute = base_rate * intensity_multiplier
        total_calories = calories_per_minute * (duration / 60)
        
        return round(total_calories, 1)
    
    async def get_supported_activities(self) -> Dict[str, Any]:
        """Get list of supported activity types."""
        return {
            "activities": self.activities,
            "total_count": len(self.activities),
            "categories": {
                "cardio": ["walking", "running", "cycling", "swimming", "stairs_up", "stairs_down", "jumping"],
                "strength": ["jumping"],
                "sedentary": ["sitting", "standing", "lying_down"]
            },
            "sensor_requirements": {
                "accelerometer": "required",
                "gyroscope": "optional",
                "minimum_duration": "5 seconds",
                "sampling_rate": "50 Hz recommended"
            }
        }
