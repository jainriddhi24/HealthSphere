import { Request, Response } from 'express'
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import { prisma } from '../index'
import { asyncHandler, createError } from '../middleware/errorHandler'
import { AuthRequest } from '../middleware/auth'

export const authController = {
  register: asyncHandler(async (req: Request, res: Response) => {
    const { email, password, name, dateOfBirth, gender } = req.body

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    })

    if (existingUser) {
      throw createError('User already exists with this email', 400)
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, parseInt(process.env.BCRYPT_ROUNDS || '12'))

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        dateOfBirth: new Date(dateOfBirth),
        gender,
        role: 'user',
        isActive: true
      },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        createdAt: true
      }
    })

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET!,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    )

    res.status(201).json({
      success: true,
      data: {
        user,
        token
      }
    })
  }),

  login: asyncHandler(async (req: Request, res: Response) => {
    const { email, password } = req.body

    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    })

    if (!user || !user.isActive) {
      throw createError('Invalid credentials', 401)
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password)
    if (!isPasswordValid) {
      throw createError('Invalid credentials', 401)
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET!,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    )

    res.json({
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role
        },
        token
      }
    })
  }),

  logout: asyncHandler(async (req: AuthRequest, res: Response) => {
    // In a real application, you might want to blacklist the token
    res.json({
      success: true,
      message: 'Logged out successfully'
    })
  }),

  getProfile: asyncHandler(async (req: AuthRequest, res: Response) => {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.id },
      select: {
        id: true,
        email: true,
        name: true,
        dateOfBirth: true,
        gender: true,
        role: true,
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

  updateProfile: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { name, dateOfBirth, gender } = req.body

    const user = await prisma.user.update({
      where: { id: req.user!.id },
      data: {
        name,
        dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
        gender
      },
      select: {
        id: true,
        email: true,
        name: true,
        dateOfBirth: true,
        gender: true,
        role: true,
        updatedAt: true
      }
    })

    res.json({
      success: true,
      data: user
    })
  }),

  changePassword: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { currentPassword, newPassword } = req.body

    const user = await prisma.user.findUnique({
      where: { id: req.user!.id }
    })

    if (!user) {
      throw createError('User not found', 404)
    }

    // Verify current password
    const isCurrentPasswordValid = await bcrypt.compare(currentPassword, user.password)
    if (!isCurrentPasswordValid) {
      throw createError('Current password is incorrect', 400)
    }

    // Hash new password
    const hashedNewPassword = await bcrypt.hash(newPassword, parseInt(process.env.BCRYPT_ROUNDS || '12'))

    // Update password
    await prisma.user.update({
      where: { id: req.user!.id },
      data: { password: hashedNewPassword }
    })

    res.json({
      success: true,
      message: 'Password changed successfully'
    })
  }),

  forgotPassword: asyncHandler(async (req: Request, res: Response) => {
    const { email } = req.body

    const user = await prisma.user.findUnique({
      where: { email }
    })

    if (!user) {
      // Don't reveal if user exists or not
      return res.json({
        success: true,
        message: 'If the email exists, a password reset link has been sent'
      })
    }

    // In a real application, you would:
    // 1. Generate a reset token
    // 2. Store it in the database with expiration
    // 3. Send an email with the reset link

    res.json({
      success: true,
      message: 'If the email exists, a password reset link has been sent'
    })
  }),

  resetPassword: asyncHandler(async (req: Request, res: Response) => {
    const { token, newPassword } = req.body

    // In a real application, you would:
    // 1. Verify the reset token
    // 2. Check if it's expired
    // 3. Update the password
    // 4. Invalidate the token

    res.json({
      success: true,
      message: 'Password reset successfully'
    })
  })
}
