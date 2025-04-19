import express from 'express';
import { registerInstitution, loginInstitution, getInstitutions } from '../controllers/institutionController.js';
import authMiddleware from '../middlewares/authMiddleware.js';
import { validateUser } from '../middlewares/validateUser.js';

const router = express.Router();

router.post('/register', validateUser, registerInstitution);
router.post('/login', validateUser, loginInstitution);
router.get('/institutions', getInstitutions); // Changed from /users and removed authMiddleware

export default router;