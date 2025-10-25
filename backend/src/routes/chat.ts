import express from 'express'
import { chatController } from '../controllers/chatController'
import { authenticate } from '../middleware/auth'

const router = express.Router()

// All routes require authentication
router.use(authenticate)

// Chat routes
router.get('/history', chatController.getChatHistory)
router.post('/message', chatController.sendMessage)
router.delete('/history', chatController.clearChatHistory)

export default router
