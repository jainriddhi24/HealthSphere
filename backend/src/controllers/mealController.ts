import { Request, Response } from 'express'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'
import axios from 'axios'

export const mealController = {
  getMeals: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { limit = 30, offset = 0, startDate, endDate } = req.query

    const where: any = { userId: req.user!.id }
    
    if (startDate && endDate) {
      where.timestamp = {
        gte: new Date(startDate as string),
        lte: new Date(endDate as string)
      }
    }

    const meals = await prisma.meal.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: meals
    })
  }),

  getMealById: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params

    const meal = await prisma.meal.findUnique({
      where: { id }
    })

    if (!meal) {
      throw createError('Meal not found', 404)
    }

    res.json({
      success: true,
      data: meal
    })
  }),

  createMeal: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { name, calories, protein, carbs, fat, imageUrl } = req.body

    const meal = await prisma.meal.create({
      data: {
        userId: req.user!.id,
        name,
        calories,
        protein,
        carbs,
        fat,
        imageUrl,
        timestamp: new Date()
      }
    })

    res.status(201).json({
      success: true,
      data: meal
    })
  }),

  updateMeal: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params
    const { name, calories, protein, carbs, fat, imageUrl } = req.body

    // Verify ownership
    const existingMeal = await prisma.meal.findFirst({
      where: { id, userId: req.user!.id }
    })

    if (!existingMeal) {
      throw createError('Meal not found', 404)
    }

    const meal = await prisma.meal.update({
      where: { id },
      data: {
        name,
        calories,
        protein,
        carbs,
        fat,
        imageUrl
      }
    })

    res.json({
      success: true,
      data: meal
    })
  }),

  deleteMeal: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params

    // Verify ownership
    const existingMeal = await prisma.meal.findFirst({
      where: { id, userId: req.user!.id }
    })

    if (!existingMeal) {
      throw createError('Meal not found', 404)
    }

    await prisma.meal.delete({
      where: { id }
    })

    res.json({
      success: true,
      message: 'Meal deleted successfully'
    })
  }),

  recognizeFood: asyncHandler(async (req: AuthRequest, res: Response) => {
    if (!req.file) {
      throw createError('No image file provided', 400)
    }

    try {
      // Convert buffer to base64 for ML API
      const base64Image = req.file.buffer.toString('base64')
      
      // Call ML API for food recognition
      const mlApiUrl = process.env.ML_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${mlApiUrl}/food-recognition`, {
        image: base64Image
      }, {
        timeout: 10000 // 10 second timeout
      })

      const recognitionResult = response.data

      // Save the meal to database
      const meal = await prisma.meal.create({
        data: {
          userId: req.user!.id,
          name: recognitionResult.foodName,
          calories: recognitionResult.nutrition.calories,
          protein: recognitionResult.nutrition.protein,
          carbs: recognitionResult.nutrition.carbs,
          fat: recognitionResult.nutrition.fat,
          imageUrl: `data:image/jpeg;base64,${base64Image}`,
          timestamp: new Date()
        }
      })

      res.json({
        success: true,
        data: {
          recognition: recognitionResult,
          meal
        }
      })

    } catch (error) {
      console.error('Food recognition error:', error)
      
      // Fallback: create meal with manual entry
      res.status(200).json({
        success: true,
        data: {
          recognition: {
            foodName: 'Unknown Food',
            confidence: 0,
            nutrition: {
              calories: 0,
              protein: 0,
              carbs: 0,
              fat: 0
            },
            ingredients: []
          },
          meal: null,
          error: 'Food recognition service unavailable. Please enter nutrition information manually.'
        }
      })
    }
  })
}
