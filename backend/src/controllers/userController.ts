import { Request, Response } from 'express'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'

export const userController = {
  getAllUsers: asyncHandler(async (req: Request, res: Response) => {
    const users = await prisma.user.findMany({
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        isActive: true,
        createdAt: true
      },
      orderBy: { createdAt: 'desc' }
    })

    res.json({
      success: true,
      data: users
    })
  }),

  getUserById: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params

    const user = await prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        name: true,
        dateOfBirth: true,
        gender: true,
        role: true,
        isActive: true,
        createdAt: true,
        updatedAt: true
      }
    })

    if (!user) {
      throw createError('User not found', 404)
    }

    res.json({
      success: true,
      data: user
    })
  }),

  updateUser: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params
    const { name, dateOfBirth, gender, role, isActive } = req.body

    const user = await prisma.user.update({
      where: { id },
      data: {
        name,
        dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
        gender,
        role,
        isActive
      },
      select: {
        id: true,
        email: true,
        name: true,
        dateOfBirth: true,
        gender: true,
        role: true,
        isActive: true,
        updatedAt: true
      }
    })

    res.json({
      success: true,
      data: user
    })
  }),

  deleteUser: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params

    await prisma.user.delete({
      where: { id }
    })

    res.json({
      success: true,
      message: 'User deleted successfully'
    })
  }),

  getHealthMetrics: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params
    const { limit = 30, offset = 0 } = req.query

    const metrics = await prisma.healthMetrics.findMany({
      where: { userId: id },
      orderBy: { date: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: metrics
    })
  }),

  createHealthMetrics: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params
    const { date, weight, bloodPressure, heartRate, sleepHours, steps, caloriesBurned } = req.body

    const metrics = await prisma.healthMetrics.create({
      data: {
        userId: id,
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
  })
}
