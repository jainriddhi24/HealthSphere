import express from 'express'
import { userController } from '../controllers/userController'
import { authenticate, authorize } from '../middleware/auth'

const router = express.Router()

// All routes require authentication
router.use(authenticate)

// User management routes
router.get('/', authorize('admin'), userController.getAllUsers)
router.get('/:id', userController.getUserById)
router.put('/:id', userController.updateUser)
router.delete('/:id', authorize('admin'), userController.deleteUser)

// User health data
router.get('/:id/health-metrics', userController.getHealthMetrics)
router.post('/:id/health-metrics', userController.createHealthMetrics)

export default router
