const mongoose = require('mongoose');

const logSchema = new mongoose.Schema({
  source: {
    type: String,
    required: true,
    enum: ['github', 'gitlab', 'jenkins']
  },
  repo: {
    type: String,
    required: true
  },
  pipelineId: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  content: {
    type: String,
    required: true
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
  }
});

module.exports = mongoose.model('Log', logSchema);
