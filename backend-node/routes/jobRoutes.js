import express from 'express';
import Job from '../models/Job.js';
import Individual from '../models/Individual.js';
import authMiddleware from '../middlewares/authMiddleware.js';
import axios from 'axios';

const router = express.Router();

// Create a new job
router.post('/api/jobs', authMiddleware, async (req, res) => {
  try {
    const { title, description, required_skills, target_years, target_departments } = req.body;
    const job = new Job({
      title,
      description,
      required_skills,
      target_years,
      target_departments,
      institution: req.user.id // From JWT
    });
    await job.save();
    res.status(201).json({ success: true, data: job });
  } catch (error) {
    console.error('Error creating job:', error);
    res.status(500).json({ success: false, message: 'Error creating job' });
  }
});

// Fetch all jobs for the institution
router.get('/api/jobs', authMiddleware, async (req, res) => {
  try {
    const jobs = await Job.find({ institution: req.user.id });
    res.json({ success: true, data: jobs });
  } catch (error) {
    console.error('Error fetching jobs:', error);
    res.status(500).json({ success: false, message: 'Error fetching jobs' });
  }
});

// Delete a job
router.delete('/api/jobs/:id', authMiddleware, async (req, res) => {
  try {
    const job = await Job.findOneAndDelete({ _id: req.params.id, institution: req.user.id });
    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }
    res.json({ success: true, message: 'Job deleted' });
  } catch (error) {
    console.error('Error deleting job:', error);
    res.status(500).json({ success: false, message: 'Error deleting job' });
  }
});

// Fetch matches for a job
router.get('/api/jobs/:id/matches', authMiddleware, async (req, res) => {
  try {
    const job = await Job.findOne({ _id: req.params.id, institution: req.user.id });
    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }

    // Fetch students matching target years and departments
    const students = await Individual.find({
      year: { $in: job.target_years },
      department: { $in: job.target_departments }
    }).select('name email department year resumeFilePath skills');

    // Call Flask server for match scores
    const matches = await Promise.all(students.map(async (student) => {
      try {
        const flaskResponse = await axios.post('http://localhost:5001/match_resume_job', {
          resumeFilePath: student.resumeFilePath,
          jobDescription: job.description,
          jobRole: job.title
        }, {
          headers: { 'Content-Type': 'application/json' }
        });

        const matchScore = flaskResponse.data.match_score || 0;

        return {
          student_id: student._id,
          job_id: job._id,
          match_score: matchScore,
          student: {
            _id: student._id,
            name: student.name,
            email: student.email,
            department: student.department,
            year: student.year,
            resume_url: `http://localhost:3000/${student.resumeFilePath}`,
            skills: student.skills || [],
            created_at: student.created_at
          },
          job
        };
      } catch (error) {
        console.error(`Error fetching match score for student ${student._id}:`, error.message);
        return {
          student_id: student._id,
          job_id: job._id,
          match_score: 0,
          student: {
            _id: student._id,
            name: student.name,
            email: student.email,
            department: student.department,
            year: student.year,
            resume_url: `http://localhost:3000/${student.resumeFilePath}`,
            skills: student.skills || [],
            created_at: student.created_at
          },
          job
        };
      }
    }));

    res.json({ success: true, data: matches });
  } catch (error) {
    console.error('Error fetching matches:', error);
    res.status(500).json({ success: false, message: 'Error fetching matches' });
  }
});

export default router;