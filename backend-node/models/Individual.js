import mongoose from 'mongoose';

const individualSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    college: { type: mongoose.Schema.Types.ObjectId, ref: 'Institution', required: true },
    year: { type: Number, required: true, enum: [1, 2, 3, 4] },
    department: { 
        type: String, 
        required: true, 
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
        ] 
    },
    resumeFilePath: { type: String, required: true },
    resumeScore: { type: Number, default: 0 }, // Added for resume scoring
    reportFilePath: { type: String } // Added for future report generation
}, { timestamps: true });

export default mongoose.models.Individual || mongoose.model('Individual', individualSchema);