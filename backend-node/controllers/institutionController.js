import Institution from '../models/Institution.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// Register Institution
export const registerInstitution = async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const existingUser = await Institution.findOne({ email });
        if (existingUser) return res.status(400).json({ message: 'Institution already exists' });

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new Institution({ name, email, password: hashedPassword });

        await newUser.save();
        res.status(201).json({ message: 'Institution registered successfully', user: { name, email } });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Login Institution
export const loginInstitution = async (req, res) => {
    try {
        const { email, password } = req.body;
        const user = await Institution.findOne({ email });
        if (!user) return res.status(400).json({ message: 'Institution not found' });

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).json({ message: 'Invalid credentials' });

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.json({ token, user: { email: user.email, name: user.name } });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get All Institutions
export const getInstitutions = async (req, res) => {
    try {
        const institutions = await Institution.find({}, 'name'); // Fetch only _id and name
        res.json(institutions);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};