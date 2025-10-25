import express from 'express'
import { authController } from '../controllers/authController'
import { authLimiter } from '../middleware/rateLimiter'
import { authenticate } from '../middleware/auth'

const router = express.Router()

// Public routes
router.post('/register', authLimiter, authController.register)
router.post('/login', authLimiter, authController.login)
router.post('/forgot-password', authLimiter, authController.forgotPassword)
router.post('/reset-password', authLimiter, authController.resetPassword)

// Protected routes
router.post('/logout', authenticate, authController.logout)
router.get('/me', authenticate, authController.getProfile)
router.put('/profile', authenticate, authController.updateProfile)
router.post('/change-password', authenticate, authController.changePassword)

export default router
