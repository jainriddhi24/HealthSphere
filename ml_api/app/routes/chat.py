from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.chat_service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = ChatService()

class ChatMessage(BaseModel):
    message: str
    user_id: str
    context: str = "health_coaching"
    conversation_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str
    context: str = "health_coaching"
    conversation_id: Optional[str] = None

@router.post("/")
async def chat(request: ChatRequest):
    """
    Process chat message and return AI response.
    
    Args:
        request: ChatRequest containing message and context
        
    Returns:
        JSON response with AI-generated response
    """
    try:
        # Process chat message
        response = await chat_service.process_message(
            message=request.message,
            user_id=request.user_id,
            context=request.context,
            conversation_id=request.conversation_id
        )
        
        return {
            "success": True,
            "data": {
                "response": response["message"],
                "conversation_id": response.get("conversation_id"),
                "suggestions": response.get("suggestions", []),
                "context": response.get("context", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/conversation")
async def start_conversation(user_id: str, context: str = "health_coaching"):
    """
    Start a new conversation session.
    
    Args:
        user_id: User identifier
        context: Conversation context
        
    Returns:
        JSON response with conversation ID
    """
    try:
        conversation_id = await chat_service.start_conversation(user_id, context)
        
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "context": context
            }
        }
        
    except Exception as e:
        logger.error(f"Start conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@router.get("/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        JSON response with conversation history
    """
    try:
        history = await chat_service.get_conversation_history(conversation_id)
        
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "messages": history
            }
        }
        
    except Exception as e:
        logger.error(f"Get conversation history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        JSON response confirming deletion
    """
    try:
        await chat_service.delete_conversation(conversation_id)
        
        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@router.get("/contexts")
async def get_available_contexts():
    """
    Get available conversation contexts.
    
    Returns:
        JSON response with available contexts
    """
    try:
        contexts = await chat_service.get_available_contexts()
        
        return {
            "success": True,
            "data": contexts
        }
        
    except Exception as e:
        logger.error(f"Get contexts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get contexts: {str(e)}")
