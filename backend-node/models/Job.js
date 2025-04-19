import mongoose from 'mongoose';

const jobSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, required: true },
  required_skills: [{ type: String, required: true }],
  target_years: [{ type: Number, enum: [1, 2, 3, 4], required: true }],
  target_departments: [{
    type: String,
    enum: [
      'Computer Science and Engineering (CSE)',
      'CSE – Data Science (CSD)',
      'CSE – Artificial Intelligence and Machine Learning (CSM / AI & ML)',
      'Artificial Intelligence and Data Science (AI&DS)',
      'Information Technology (IT)',
      'Electronics and Communication Engineering (ECE)',
      'Electrical and Electronics Engineering (EEE)',
      'Mechanical Engineering',
      'Civil Engineering',
      'Chemical Engineering',
      'Biomedical Engineering',
      'Pharmaceutical Engineering'
    ],
    required: true
  }],
  institution: { type: mongoose.Schema.Types.ObjectId, ref: 'Institution', required: true },
  created_at: { type: Date, default: Date.now }
}, { timestamps: true });

export default mongoose.models.Job || mongoose.model('Job', jobSchema);