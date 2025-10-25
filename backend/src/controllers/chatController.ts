import { Request, Response } from 'express'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'
import axios from 'axios'

export const chatController = {
  getChatHistory: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { limit = 50, offset = 0 } = req.query

    const messages = await prisma.chatMessage.findMany({
      where: { userId: req.user!.id },
      orderBy: { timestamp: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: messages.reverse() // Return in chronological order
    })
  }),

  sendMessage: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { message } = req.body

    if (!message || message.trim().length === 0) {
      throw createError('Message cannot be empty', 400)
    }

    // Save user message
    const userMessage = await prisma.chatMessage.create({
      data: {
        userId: req.user!.id,
        message: message.trim(),
        isUser: true,
        timestamp: new Date()
      }
    })

    try {
      // Call ML API for AI response
      const mlApiUrl = process.env.ML_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${mlApiUrl}/chat`, {
        message: message.trim(),
        userId: req.user!.id,
        context: 'health_coaching'
      }, {
        timeout: 15000 // 15 second timeout
      })

      const aiResponse = response.data.response

      // Save AI response
      const aiMessage = await prisma.chatMessage.create({
        data: {
          userId: req.user!.id,
          message: aiResponse,
          isUser: false,
          timestamp: new Date()
        }
      })

      res.json({
        success: true,
        data: {
          userMessage,
          aiMessage
        }
      })

    } catch (error) {
      console.error('AI chat error:', error)
      
      // Fallback response
      const fallbackResponse = generateFallbackResponse(message)
      
      const aiMessage = await prisma.chatMessage.create({
        data: {
          userId: req.user!.id,
          message: fallbackResponse,
          isUser: false,
          timestamp: new Date()
        }
      })

      res.json({
        success: true,
        data: {
          userMessage,
          aiMessage
        }
      })
    }
  }),

  clearChatHistory: asyncHandler(async (req: AuthRequest, res: Response) => {
    await prisma.chatMessage.deleteMany({
      where: { userId: req.user!.id }
    })

    res.json({
      success: true,
      message: 'Chat history cleared successfully'
    })
  })
}

function generateFallbackResponse(userMessage: string): string {
  const message = userMessage.toLowerCase()
  
  if (message.includes('workout') || message.includes('exercise')) {
    return "I'd be happy to help with your workout routine! Based on your health profile, I recommend starting with low-impact cardio exercises like walking or swimming. Would you like me to create a personalized workout plan for you?"
  }
  
  if (message.includes('diet') || message.includes('food') || message.includes('meal')) {
    return "Great question about nutrition! For optimal health, focus on whole foods like vegetables, lean proteins, and complex carbohydrates. I can help you track your meals and suggest healthy alternatives. What specific dietary goals are you working towards?"
  }
  
  if (message.includes('blood pressure') || message.includes('heart')) {
    return "Managing cardiovascular health is crucial! Regular exercise, a balanced diet, and stress management can help maintain healthy blood pressure. I recommend monitoring your readings and consulting with your healthcare provider. Would you like tips for heart-healthy lifestyle changes?"
  }
  
  if (message.includes('sleep') || message.includes('insomnia')) {
    return "Quality sleep is essential for overall health! Try maintaining a consistent sleep schedule, creating a relaxing bedtime routine, and avoiding screens before bed. I can help you track your sleep patterns and suggest improvements. How many hours of sleep are you currently getting?"
  }
  
  if (message.includes('stress') || message.includes('anxiety')) {
    return "Mental wellness is just as important as physical health! Consider incorporating mindfulness practices, deep breathing exercises, or gentle yoga into your routine. I'm here to support your mental health journey. What's causing you the most stress right now?"
  }
  
  if (message.includes('weight') || message.includes('lose') || message.includes('gain')) {
    return "Healthy weight management involves a combination of balanced nutrition and regular physical activity. Remember, sustainable changes work best! I can help you set realistic goals and track your progress. What's your current approach to weight management?"
  }
  
  return "I'm here to help with your health and wellness journey! I can provide guidance on exercise, nutrition, sleep, stress management, and more. What specific aspect of your health would you like to focus on today?"
}
