import { Request, Response } from 'express'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'

export const workoutController = {
  getWorkouts: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { type, difficulty, limit = 20, offset = 0 } = req.query

    const where: any = {}
    if (type) where.type = type
    if (difficulty) where.difficulty = difficulty

    const workouts = await prisma.workout.findMany({
      where,
      include: {
        exercises: true
      },
      orderBy: { createdAt: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: workouts
    })
  }),

  getWorkoutById: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params

    const workout = await prisma.workout.findUnique({
      where: { id },
      include: {
        exercises: true
      }
    })

    if (!workout) {
      throw createError('Workout not found', 404)
    }

    res.json({
      success: true,
      data: workout
    })
  }),

  createWorkout: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { name, type, duration, difficulty, description, exercises } = req.body

    const workout = await prisma.workout.create({
      data: {
        name,
        type,
        duration,
        difficulty,
        description,
        exercises: {
          create: exercises
        }
      },
      include: {
        exercises: true
      }
    })

    res.status(201).json({
      success: true,
      data: workout
    })
  }),

  updateWorkout: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params
    const { name, type, duration, difficulty, description, exercises } = req.body

    // Delete existing exercises and create new ones
    await prisma.exercise.deleteMany({
      where: { workoutId: id }
    })

    const workout = await prisma.workout.update({
      where: { id },
      data: {
        name,
        type,
        duration,
        difficulty,
        description,
        exercises: {
          create: exercises
        }
      },
      include: {
        exercises: true
      }
    })

    res.json({
      success: true,
      data: workout
    })
  }),

  deleteWorkout: asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params

    await prisma.workout.delete({
      where: { id }
    })

    res.json({
      success: true,
      message: 'Workout deleted successfully'
    })
  }),

  getWorkoutProgress: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params
    const { limit = 30, offset = 0 } = req.query

    const progress = await prisma.workoutProgress.findMany({
      where: { 
        workoutId: id,
        userId: req.user!.id
      },
      orderBy: { completedAt: 'desc' },
      take: parseInt(limit as string),
      skip: parseInt(offset as string)
    })

    res.json({
      success: true,
      data: progress
    })
  }),

  recordWorkoutProgress: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { id } = req.params
    const { duration, caloriesBurned, notes } = req.body

    const progress = await prisma.workoutProgress.create({
      data: {
        workoutId: id,
        userId: req.user!.id,
        duration,
        caloriesBurned,
        notes,
        completedAt: new Date()
      }
    })

    res.status(201).json({
      success: true,
      data: progress
    })
  })
}
