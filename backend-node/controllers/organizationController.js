import Organization from '../models/Organization.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import mongoose from 'mongoose';
import Institution from '../models/Institution.js';
import Individual from '../models/Individual.js';

// Register Organization
export const registerOrganization = async (req, res) => {
    try {
        const { email, password } = req.body;
        const existingUser = await Organization.findOne({ email });
        if (existingUser) return res.status(400).json({ message: 'Organization already exists' });

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new Organization({ email, password: hashedPassword });

        await newUser.save();
        res.status(201).json({ message: 'Organization registered successfully' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Login Organization
export const loginOrganization = async (req, res) => {
    try {
        const { email, password } = req.body;
        const user = await Organization.findOne({ email });
        if (!user) return res.status(400).json({ message: 'Organization not found' });

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return res.status(400).json({ message: 'Invalid credentials' });

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.json({ token, user: { email: user.email } });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

// Get All Organizations
export const getOrganizations = async (req, res) => {
    try {
        const users = await Organization.find();
        res.json(users);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};

export const getInstitutions = async (req, res) => {
    try {
      const institutions = await Institution.find({}, 'name').lean();
      const institutionsWithCounts = await Promise.all(
        institutions.map(async (inst) => {
          const studentCount = await Individual.countDocuments({ college: inst._id });
          return {
            id: inst._id,
            name: inst.name,
            studentCount,
          };
        })
      );
      res.status(200).json(institutionsWithCounts);
    } catch (error) {
      console.error('Error fetching institutions:', error);
      res.status(500).json({ message: 'Server error' });
    }
  };
  
  // New controller to fetch students with filters, sorting, and pagination
  export const getStudents = async (req, res) => {
    try {
      const {
        institutionId,
        search = '',
        year = '',
        course = '',
        sortBy = 'resumeScore',
        sortOrder = 'desc',
        page = 1,
        limit = 8,
      } = req.query;
  
      // Build query object
      const query = {};
  
      // Filter by institution
      if (institutionId && mongoose.Types.ObjectId.isValid(institutionId)) {
        query.college = institutionId;
      }
  
      // Filter by student name (case-insensitive)
      if (search) {
        query.name = { $regex: search, $options: 'i' };
      }
  
      // Filter by year
      if (year && ['1st', '2nd', '3rd', '4th'].includes(year)) {
        const yearMap = { '1st': 1, '2nd': 2, '3rd': 3, '4th': 4 };
        query.year = yearMap[year];
      }
  
      // Filter by course (department)
      if (course) {
        query.department = course;
      }
  
      // Sorting
      const sort = {};
      if (sortBy === 'resumeScore') {
        sort.resumeScore = sortOrder === 'desc' ? -1 : 1;
      }
  
      // Pagination
      const pageNum = parseInt(page, 10) || 1;
      const limitNum = parseInt(limit, 10) || 8;
      const skip = (pageNum - 1) * limitNum;
  
      // Fetch students
      const students = await Individual.find(query)
        .select('name department year resumeFilePath college')
        .populate('college', 'name')
        .sort(sort)
        .skip(skip)
        .limit(limitNum)
        .lean();
  
      // Total count for pagination
      const total = await Individual.countDocuments(query);
  
      // Map students to match frontend format
      const formattedStudents = students.map((student) => ({
        id: student._id,
        name: student.name,
        course: student.department,
        year: `${student.year}${['st', 'nd', 'rd', 'th'][student.year - 1]}`,
        institution: student.college._id,
        resumeScore: student.resumeScore || Math.floor(Math.random() * 30) + 70, // Placeholder: Replace with actual score logic
        resumeUrl: student.resumeFilePath,
        hasReport: false, // Placeholder: Implement report logic if needed
      }));
  
      res.status(200).json({
        students: formattedStudents,
        total,
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(total / limitNum),
      });
    } catch (error) {
      console.error('Error fetching students:', error);
      res.status(500).json({ message: 'Server error' });
    }
  };