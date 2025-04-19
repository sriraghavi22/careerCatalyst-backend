import express from 'express';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import cors from 'cors';
import individualRoutes from './routes/individualRoutes.js';
import institutionRoutes from './routes/institutionRoutes.js';
import organizationRoutes from './routes/organizationRoutes.js';
import jobRoutes from './routes/jobRoutes.js';

dotenv.config();
const app = express();

// Middleware
app.use(cors({
  origin: ['http://localhost:5173', 'https://career-catalyst-six.vercel.app'],
  methods: ['GET', 'POST', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));
app.use(express.json());

// Routes
app.use('/individuals', individualRoutes);
app.use('/institutions', institutionRoutes);
app.use('/organizations', organizationRoutes);
app.use('/institutions', jobRoutes);

// Database Connection
mongoose.connect(process.env.MONGO_URI, {
}).then(() => console.log('MongoDB Connected'))
  .catch(err => console.error(err));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));