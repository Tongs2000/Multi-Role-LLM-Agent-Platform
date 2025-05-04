const express = require('express');
const router = express.Router();
const notesController = require('../controllers/notesController');

// Define routes
router.get('/', notesController.getNotes);
router.get('/:id', notesController.getNoteById);
router.post('/', notesController.saveNote);
router.put('/:id', notesController.saveNote);
router.delete('/:id', notesController.deleteNote);
router.get('/search', notesController.searchNotes);

module.exports = router;