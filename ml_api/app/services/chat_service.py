import logging
from typing import Dict, Any, List, Optional
import random
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for AI-powered health coaching chat.
    In production, this would integrate with advanced language models.
    """
    
    def __init__(self):
        self.conversations = {}
        self.contexts = {
            "health_coaching": {
                "description": "General health and wellness coaching",
                "personality": "supportive and knowledgeable",
                "expertise": ["nutrition", "exercise", "sleep", "stress_management"]
            },
            "diabetes_management": {
                "description": "Specialized diabetes care and management",
                "personality": "clinical and precise",
                "expertise": ["blood_glucose", "medication", "diet", "complications"]
            },
            "cardiovascular_health": {
                "description": "Heart health and cardiovascular disease prevention",
                "personality": "encouraging and evidence-based",
                "expertise": ["blood_pressure", "cholesterol", "exercise", "diet"]
            },
            "mental_wellness": {
                "description": "Mental health and emotional well-being support",
                "personality": "empathetic and understanding",
                "expertise": ["stress", "anxiety", "depression", "mindfulness"]
            }
        }
        logger.info("Chat service initialized")
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        context: str = "health_coaching",
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate AI response.
        
        Args:
            message: User's message
            user_id: User identifier
            context: Conversation context
            conversation_id: Optional conversation ID
            
        Returns:
            Dictionary with AI response and metadata
        """
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = await self.start_conversation(user_id, context)
            
            # Store user message
            self._store_message(conversation_id, message, True, user_id)
            
            # Generate AI response
            response = await self._generate_response(message, context, conversation_id)
            
            # Store AI response
            self._store_message(conversation_id, response["message"], False, user_id)
            
            return {
                "message": response["message"],
                "conversation_id": conversation_id,
                "suggestions": response.get("suggestions", []),
                "context": response.get("context", {})
            }
            
        except Exception as e:
            logger.error(f"Chat processing error: {str(e)}")
            raise Exception(f"Chat processing failed: {str(e)}")
    
    async def start_conversation(self, user_id: str, context: str = "health_coaching") -> str:
        """Start a new conversation session."""
        conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = {
            "user_id": user_id,
            "context": context,
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        logger.info(f"Started conversation {conversation_id} for user {user_id}")
        return conversation_id
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
        
        return self.conversations[conversation_id]["messages"]
    
    async def delete_conversation(self, conversation_id: str):
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")
    
    async def get_available_contexts(self) -> Dict[str, Any]:
        """Get available conversation contexts."""
        return {
            "contexts": self.contexts,
            "total_count": len(self.contexts)
        }
    
    def _store_message(self, conversation_id: str, message: str, is_user: bool, user_id: str):
        """Store message in conversation history."""
        if conversation_id not in self.conversations:
            return
        
        self.conversations[conversation_id]["messages"].append({
            "message": message,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })
        
        self.conversations[conversation_id]["last_activity"] = datetime.now()
    
    async def _generate_response(self, message: str, context: str, conversation_id: str) -> Dict[str, Any]:
        """Generate AI response based on message and context."""
        # In production, this would use a trained language model
        # For now, we'll use rule-based responses
        
        message_lower = message.lower()
        context_info = self.contexts.get(context, self.contexts["health_coaching"])
        
        # Generate contextual response
        response = self._generate_contextual_response(message_lower, context_info)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(message_lower, context)
        
        return {
            "message": response,
            "suggestions": suggestions,
            "context": {
                "context_type": context,
                "personality": context_info["personality"],
                "expertise": context_info["expertise"]
            }
        }
    
    def _generate_contextual_response(self, message: str, context_info: Dict[str, Any]) -> str:
        """Generate contextual response based on message content."""
        personality = context_info["personality"]
        expertise = context_info["expertise"]
        
        # Health coaching responses
        if "workout" in message or "exercise" in message:
            responses = [
                "I'd be happy to help with your workout routine! Based on your health profile, I recommend starting with low-impact cardio exercises like walking or swimming. Would you like me to create a personalized workout plan for you?",
                "Great question about exercise! For optimal health, aim for at least 150 minutes of moderate-intensity activity per week. I can help you design a program that fits your fitness level and goals.",
                "Exercise is crucial for maintaining good health! Let's discuss your current fitness level and any health conditions to create the best workout plan for you."
            ]
        elif "diet" in message or "food" in message or "meal" in message:
            responses = [
                "Nutrition is a key pillar of good health! I recommend focusing on whole foods like vegetables, lean proteins, and complex carbohydrates. What specific dietary goals are you working towards?",
                "Great question about nutrition! A balanced diet with plenty of fruits, vegetables, and lean proteins can significantly improve your health. I can help you track your meals and suggest healthy alternatives.",
                "Food choices have a huge impact on your health! Let's discuss your current eating habits and create a plan that works for your lifestyle and health goals."
            ]
        elif "blood pressure" in message or "heart" in message:
            responses = [
                "Managing cardiovascular health is crucial! Regular exercise, a balanced diet, and stress management can help maintain healthy blood pressure. I recommend monitoring your readings and consulting with your healthcare provider.",
                "Heart health is so important! Lifestyle changes like reducing sodium, increasing physical activity, and managing stress can make a big difference. Would you like tips for heart-healthy lifestyle changes?",
                "Your cardiovascular health is a priority! I can help you understand your risk factors and create a plan to improve your heart health through diet, exercise, and lifestyle modifications."
            ]
        elif "sleep" in message or "insomnia" in message:
            responses = [
                "Quality sleep is essential for overall health! Try maintaining a consistent sleep schedule, creating a relaxing bedtime routine, and avoiding screens before bed. I can help you track your sleep patterns and suggest improvements.",
                "Sleep is when your body repairs and rejuvenates! Aim for 7-9 hours of quality sleep per night. Let's discuss your current sleep habits and create a plan for better rest.",
                "Good sleep is foundational to good health! I can help you optimize your sleep environment and routine. How many hours of sleep are you currently getting?"
            ]
        elif "stress" in message or "anxiety" in message:
            responses = [
                "Mental wellness is just as important as physical health! Consider incorporating mindfulness practices, deep breathing exercises, or gentle yoga into your routine. I'm here to support your mental health journey.",
                "Stress management is crucial for overall well-being! I can teach you relaxation techniques and help you develop healthy coping strategies. What's causing you the most stress right now?",
                "Your mental health matters! Let's work together to develop stress management techniques that fit your lifestyle. Remember, it's okay to seek professional help when needed."
            ]
        elif "weight" in message or "lose" in message or "gain" in message:
            responses = [
                "Healthy weight management involves a combination of balanced nutrition and regular physical activity. Remember, sustainable changes work best! I can help you set realistic goals and track your progress.",
                "Weight management is about creating healthy habits that last! Focus on nourishing your body with whole foods and staying active. What's your current approach to weight management?",
                "Let's create a sustainable plan for healthy weight management! I'll help you set realistic goals and develop habits that support your long-term health and well-being."
            ]
        elif "diabetes" in message:
            responses = [
                "Diabetes management requires careful attention to diet, exercise, and blood glucose monitoring. I can help you understand how different foods and activities affect your blood sugar levels.",
                "Managing diabetes effectively involves balancing medication, diet, and lifestyle. Let's create a comprehensive plan that helps you maintain stable blood glucose levels.",
                "I'm here to support your diabetes management journey! Together, we can develop strategies for healthy eating, regular exercise, and effective blood glucose monitoring."
            ]
        else:
            responses = [
                "I'm here to help with your health and wellness journey! I can provide guidance on exercise, nutrition, sleep, stress management, and more. What specific aspect of your health would you like to focus on today?",
                "Your health is my priority! I can assist with personalized advice on fitness, nutrition, mental wellness, and chronic disease management. What would you like to work on together?",
                "I'm your personal health coach, ready to support you! Whether it's improving your fitness, optimizing your nutrition, or managing stress, I'm here to help you achieve your health goals."
            ]
        
        return random.choice(responses)
    
    def _generate_suggestions(self, message: str, context: str) -> List[str]:
        """Generate follow-up suggestions based on message content."""
        suggestions = []
        
        if "workout" in message or "exercise" in message:
            suggestions.extend([
                "Create a personalized workout plan",
                "Learn about different exercise types",
                "Track your fitness progress"
            ])
        elif "diet" in message or "food" in message:
            suggestions.extend([
                "Get nutrition analysis for your meals",
                "Learn about healthy food choices",
                "Create a meal planning strategy"
            ])
        elif "sleep" in message:
            suggestions.extend([
                "Improve your sleep hygiene",
                "Track your sleep patterns",
                "Learn relaxation techniques"
            ])
        elif "stress" in message:
            suggestions.extend([
                "Practice mindfulness exercises",
                "Learn stress management techniques",
                "Create a self-care routine"
            ])
        else:
            suggestions.extend([
                "Set health goals",
                "Track your progress",
                "Get personalized recommendations"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
