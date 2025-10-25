import { Request, Response } from 'express'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'

export const healthController = {
  getHealthMetrics: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { limit = 30, offset = 0, startDate, endDate } = req.query

    const where: any = { userId: req.user!.id }
    
    if (startDate && endDate) {
      where.date = {
        gte: new Date(startDate as string),
        lte: new Date(endDate as string)
      }
    }

    const metrics = await prisma.healthMetrics.findMany({
      where,
      orderBy: { date: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: metrics
    })
  }),

  createHealthMetrics: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { date, weight, bloodPressure, heartRate, sleepHours, steps, caloriesBurned } = req.body

    const metrics = await prisma.healthMetrics.create({
      data: {
        userId: req.user!.id,
        date: new Date(date),
        weight,
        bloodPressure,
        heartRate,
        sleepHours,
        steps,
        caloriesBurned
      }
    })

    res.status(201).json({
      success: true,
      data: metrics
    })
  }),

  updateHealthMetrics: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params
    const { date, weight, bloodPressure, heartRate, sleepHours, steps, caloriesBurned } = req.body

    // Verify ownership
    const existingMetrics = await prisma.healthMetrics.findFirst({
      where: { id, userId: req.user!.id }
    })

    if (!existingMetrics) {
      throw createError('Health metrics not found', 404)
    }

    const metrics = await prisma.healthMetrics.update({
      where: { id },
      data: {
        date: date ? new Date(date) : undefined,
        weight,
        bloodPressure,
        heartRate,
        sleepHours,
        steps,
        caloriesBurned
      }
    })

    res.json({
      success: true,
      data: metrics
    })
  }),

  deleteHealthMetrics: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params

    // Verify ownership
    const existingMetrics = await prisma.healthMetrics.findFirst({
      where: { id, userId: req.user!.id }
    })

    if (!existingMetrics) {
      throw createError('Health metrics not found', 404)
    }

    await prisma.healthMetrics.delete({
      where: { id }
    })

    res.json({
      success: true,
      message: 'Health metrics deleted successfully'
    })
  }),

  getHealthInsights: asyncHandler(async (req: AuthRequest, res: Response) => {
    const userId = req.user!.id

    // Get recent metrics
    const recentMetrics = await prisma.healthMetrics.findMany({
      where: { userId },
      orderBy: { date: 'desc' },
      take: 30
    })

    if (recentMetrics.length === 0) {
      return res.json({
        success: true,
        data: {
          insights: [],
          recommendations: []
        }
      })
    }

    // Calculate insights
    const insights = []
    const recommendations = []

    // Weight trend
    if (recentMetrics.length >= 7) {
      const weightTrend = recentMetrics.slice(0, 7).map(m => m.weight)
      const avgWeight = weightTrend.reduce((a, b) => a + b, 0) / weightTrend.length
      const weightChange = weightTrend[0] - weightTrend[6]
      
      insights.push({
        type: 'weight',
        value: avgWeight,
        change: weightChange,
        trend: weightChange > 0 ? 'increasing' : weightChange < 0 ? 'decreasing' : 'stable'
      })

      if (Math.abs(weightChange) > 2) {
        recommendations.push({
          type: 'weight',
          message: weightChange > 0 
            ? 'Consider adjusting your diet and increasing physical activity'
            : 'Ensure you\'re maintaining a balanced diet with adequate nutrition'
        })
      }
    }

    // Blood pressure analysis
    const avgBP = recentMetrics.reduce((sum, m) => sum + m.bloodPressure, 0) / recentMetrics.length
    insights.push({
      type: 'blood_pressure',
      value: avgBP,
      status: avgBP < 120 ? 'normal' : avgBP < 140 ? 'elevated' : 'high'
    })

    if (avgBP >= 140) {
      recommendations.push({
        type: 'blood_pressure',
        message: 'Consider consulting with a healthcare provider about your blood pressure'
      })
    }

    // Sleep analysis
    const avgSleep = recentMetrics.reduce((sum, m) => sum + m.sleepHours, 0) / recentMetrics.length
    insights.push({
      type: 'sleep',
      value: avgSleep,
      status: avgSleep >= 7 ? 'good' : avgSleep >= 6 ? 'fair' : 'poor'
    })

    if (avgSleep < 7) {
      recommendations.push({
        type: 'sleep',
        message: 'Try to get 7-9 hours of sleep per night for optimal health'
      })
    }

    res.json({
      success: true,
      data: {
        insights,
        recommendations
      }
    })
  }),

  getRiskAssessment: asyncHandler(async (req: AuthRequest, res: Response) => {
    const userId = req.user!.id

    // Get user profile and recent metrics
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { dateOfBirth: true, gender: true }
    })

    const recentMetrics = await prisma.healthMetrics.findMany({
      where: { userId },
      orderBy: { date: 'desc' },
      take: 7
    })

    if (!user || recentMetrics.length === 0) {
      return res.json({
        success: true,
        data: {
          riskLevel: 'unknown',
          factors: [],
          recommendations: []
        }
      })
    }

    // Calculate age
    const age = new Date().getFullYear() - new Date(user.dateOfBirth).getFullYear()

    // Calculate risk factors
    const factors = []
    const recommendations = []
    let riskScore = 0

    // Age factor
    if (age > 65) {
      factors.push({ factor: 'age', level: 'high', description: 'Age over 65' })
      riskScore += 3
    } else if (age > 45) {
      factors.push({ factor: 'age', level: 'medium', description: 'Age 45-65' })
      riskScore += 1
    }

    // Blood pressure factor
    const avgBP = recentMetrics.reduce((sum, m) => sum + m.bloodPressure, 0) / recentMetrics.length
    if (avgBP >= 140) {
      factors.push({ factor: 'blood_pressure', level: 'high', description: 'High blood pressure' })
      riskScore += 3
      recommendations.push('Consult a healthcare provider about blood pressure management')
    } else if (avgBP >= 130) {
      factors.push({ factor: 'blood_pressure', level: 'medium', description: 'Elevated blood pressure' })
      riskScore += 1
    }

    // Weight factor (simplified BMI calculation)
    const avgWeight = recentMetrics.reduce((sum, m) => sum + m.weight, 0) / recentMetrics.length
    const avgHeight = 170 // Default height in cm - in real app, store user height
    const bmi = avgWeight / Math.pow(avgHeight / 100, 2)
    
    if (bmi >= 30) {
      factors.push({ factor: 'weight', level: 'high', description: 'Obesity (BMI ≥ 30)' })
      riskScore += 2
      recommendations.push('Consider weight management strategies with healthcare guidance')
    } else if (bmi >= 25) {
      factors.push({ factor: 'weight', level: 'medium', description: 'Overweight (BMI 25-29.9)' })
      riskScore += 1
    }

    // Activity level factor
    const avgSteps = recentMetrics.reduce((sum, m) => sum + m.steps, 0) / recentMetrics.length
    if (avgSteps < 5000) {
      factors.push({ factor: 'activity', level: 'high', description: 'Low physical activity' })
      riskScore += 2
      recommendations.push('Increase daily physical activity to at least 7,500 steps')
    } else if (avgSteps < 7500) {
      factors.push({ factor: 'activity', level: 'medium', description: 'Moderate physical activity' })
      riskScore += 1
    }

    // Determine overall risk level
    let riskLevel = 'low'
    if (riskScore >= 6) {
      riskLevel = 'high'
    } else if (riskScore >= 3) {
      riskLevel = 'medium'
    }

    res.json({
      success: true,
      data: {
        riskLevel,
        riskScore,
        factors,
        recommendations
      }
    })
  })
}
