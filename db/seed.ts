import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Starting database seeding...')

  // Create demo users
  const hashedPassword = await bcrypt.hash('password123', 12)

  const demoUser = await prisma.user.upsert({
    where: { email: 'demo@healthsphere.com' },
    update: {},
    create: {
      email: 'demo@healthsphere.com',
      password: hashedPassword,
      name: 'John Doe',
      dateOfBirth: new Date('1990-01-15'),
      gender: 'male',
      role: 'user',
      isActive: true
    }
  })

  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@healthsphere.com' },
    update: {},
    create: {
      email: 'admin@healthsphere.com',
      password: hashedPassword,
      name: 'Admin User',
      dateOfBirth: new Date('1985-05-20'),
      gender: 'female',
      role: 'admin',
      isActive: true
    }
  })

  console.log('✅ Created users:', { demoUser: demoUser.email, adminUser: adminUser.email })

  // Create demo health metrics
  const healthMetrics = []
  for (let i = 0; i < 30; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    
    healthMetrics.push({
      userId: demoUser.id,
      date: date,
      weight: 70 + Math.random() * 2 - 1, // 69-71 kg
      bloodPressure: 115 + Math.floor(Math.random() * 10), // 115-125
      heartRate: 60 + Math.floor(Math.random() * 20), // 60-80 bpm
      sleepHours: 7 + Math.random() * 2, // 7-9 hours
      steps: 5000 + Math.floor(Math.random() * 5000), // 5000-10000 steps
      caloriesBurned: 2000 + Math.floor(Math.random() * 500) // 2000-2500 calories
    })
  }

  await prisma.healthMetrics.createMany({
    data: healthMetrics,
    skipDuplicates: true
  })

  console.log('✅ Created health metrics')

  // Create demo workouts
  const workouts = [
    {
      name: 'Cardio Blast',
      type: 'cardio',
      duration: 30,
      difficulty: 'intermediate',
      description: 'High-intensity cardio workout to boost your heart health',
      exercises: [
        { name: 'Jumping Jacks', sets: 3, reps: 20, restTime: 30 },
        { name: 'Burpees', sets: 3, reps: 10, restTime: 45 },
        { name: 'Mountain Climbers', sets: 3, duration: 30, restTime: 30 },
        { name: 'High Knees', sets: 3, duration: 30, restTime: 30 }
      ]
    },
    {
      name: 'Strength Training',
      type: 'strength',
      duration: 45,
      difficulty: 'advanced',
      description: 'Build muscle and improve bone density with resistance training',
      exercises: [
        { name: 'Push-ups', sets: 4, reps: 15, restTime: 60 },
        { name: 'Squats', sets: 4, reps: 20, restTime: 60 },
        { name: 'Plank', sets: 3, duration: 45, restTime: 60 },
        { name: 'Lunges', sets: 3, reps: 12, restTime: 45 }
      ]
    },
    {
      name: 'Flexibility Flow',
      type: 'flexibility',
      duration: 25,
      difficulty: 'beginner',
      description: 'Gentle stretching and mobility exercises for joint health',
      exercises: [
        { name: 'Cat-Cow Stretch', sets: 2, reps: 10, restTime: 15 },
        { name: 'Downward Dog', sets: 3, duration: 30, restTime: 30 },
        { name: 'Hip Flexor Stretch', sets: 2, duration: 45, restTime: 30 },
        { name: 'Spinal Twist', sets: 2, duration: 30, restTime: 30 }
      ]
    },
    {
      name: 'Balance & Stability',
      type: 'balance',
      duration: 20,
      difficulty: 'beginner',
      description: 'Improve coordination and prevent falls with balance exercises',
      exercises: [
        { name: 'Single Leg Stand', sets: 3, duration: 30, restTime: 30 },
        { name: 'Heel-to-Toe Walk', sets: 2, duration: 20, restTime: 30 },
        { name: 'Tree Pose', sets: 2, duration: 30, restTime: 30 },
        { name: 'Standing Leg Swings', sets: 2, reps: 10, restTime: 30 }
      ]
    }
  ]

  for (const workoutData of workouts) {
    const { exercises, ...workoutInfo } = workoutData
    const workout = await prisma.workout.create({
      data: {
        ...workoutInfo,
        exercises: {
          create: exercises
        }
      }
    })
    console.log(`✅ Created workout: ${workout.name}`)
  }

  // Create demo meals
  const meals = [
    {
      name: 'Grilled Chicken Salad',
      calories: 320,
      protein: 28,
      carbs: 12,
      fat: 18
    },
    {
      name: 'Quinoa Bowl with Vegetables',
      calories: 280,
      protein: 12,
      carbs: 45,
      fat: 8
    },
    {
      name: 'Salmon with Sweet Potato',
      calories: 450,
      protein: 35,
      carbs: 30,
      fat: 22
    },
    {
      name: 'Greek Yogurt with Berries',
      calories: 150,
      protein: 15,
      carbs: 20,
      fat: 3
    }
  ]

  for (const mealData of meals) {
    const meal = await prisma.meal.create({
      data: {
        userId: demoUser.id,
        ...mealData,
        timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000) // Random time in last 7 days
      }
    })
    console.log(`✅ Created meal: ${meal.name}`)
  }

  // Create demo chat messages
  const chatMessages = [
    {
      message: 'Hi! I\'m new to HealthSphere. Can you help me get started?',
      isUser: true
    },
    {
      message: 'Welcome to HealthSphere! I\'m here to help you on your health journey. I can assist with workout recommendations, nutrition advice, sleep optimization, and stress management. What would you like to focus on first?',
      isUser: false
    },
    {
      message: 'I want to improve my cardiovascular health. What exercises do you recommend?',
      isUser: true
    },
    {
      message: 'Great goal! For cardiovascular health, I recommend starting with low-impact cardio exercises like brisk walking, swimming, or cycling. Aim for at least 150 minutes of moderate-intensity exercise per week. Would you like me to create a personalized cardio workout plan for you?',
      isUser: false
    }
  ]

  for (const messageData of chatMessages) {
    await prisma.chatMessage.create({
      data: {
        userId: demoUser.id,
        ...messageData,
        timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000) // Random time in last 24 hours
      }
    })
  }

  console.log('✅ Created chat messages')

  console.log('🎉 Database seeding completed successfully!')
}

main()
  .catch((e) => {
    console.error('❌ Error during seeding:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
