const express = require('express');
const router = express.Router();
const logController = require('../controllers/logController');

router.post('/upload', logController.uploadLogs);
router.get('/github', logController.fetchGithubLogs);

module.exports = router;
