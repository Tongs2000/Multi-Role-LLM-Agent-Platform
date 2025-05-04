const express = require('express');
const router = express.Router();
const categoriesController = require('../controllers/categoriesController');

// Define routes
router.get('/', categoriesController.getCategories);
router.post('/', categoriesController.createCategory);

module.exports = router;