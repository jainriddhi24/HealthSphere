import express from 'express'
import { mealController } from '../controllers/mealController'
import { authenticate } from '../middleware/auth'
import multer from 'multer'

const router = express.Router()

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE || '10485760') // 10MB
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true)
    } else {
      cb(new Error('Only image files are allowed'))
    }
  }
})

// All routes require authentication
router.use(authenticate)

// Meal routes
router.get('/', mealController.getMeals)
router.get('/:id', mealController.getMealById)
router.post('/', mealController.createMeal)
router.put('/:id', mealController.updateMeal)
router.delete('/:id', mealController.deleteMeal)

// Food recognition route
router.post('/recognize', upload.single('image'), mealController.recognizeFood)

export default router
