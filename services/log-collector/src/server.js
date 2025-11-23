require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const morgan = require('morgan');
const logRoutes = require('./routes/logRoutes');

const app = express();
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/safeops-logminer';

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/logs', logRoutes);

// Database Connection
mongoose.connect(MONGODB_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));

// Start Server
app.listen(PORT, () => {
    console.log(`LogCollector service running on port ${PORT}`);
});
