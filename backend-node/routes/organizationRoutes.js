import express from 'express';
import { registerOrganization, loginOrganization, getOrganizations, getInstitutions, getStudents } from '../controllers/organizationController.js';
import authMiddleware from '../middlewares/authMiddleware.js';
import { validateUser } from '../middlewares/validateUser.js';

const router = express.Router();

// Organization authentication routes
router.post('/register', validateUser, registerOrganization);
router.post('/login', validateUser, loginOrganization);

// Fetch all organizations (requires authentication)
router.get('/users', authMiddleware, getOrganizations);

// Fetch all institutions (accessible to authenticated organizations)
router.get('/institutions', authMiddleware, getInstitutions);

// Fetch students with filters, sorting, and pagination (accessible to authenticated organizations)
router.get('/students', authMiddleware, getStudents);

export default router;