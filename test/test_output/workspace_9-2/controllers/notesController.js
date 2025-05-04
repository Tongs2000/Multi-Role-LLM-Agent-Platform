const Note = require('../models/Note');

// Get all notes
const getNotes = async (req, res) => {
  try {
    const notes = await Note.find().populate('category');
    res.json(notes);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Get a specific note
const getNoteById = async (req, res) => {
  try {
    const note = await Note.findById(req.params.id).populate('category');
    if (!note) return res.status(404).json({ message: 'Note not found' });
    res.json(note);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Create or update a note
const saveNote = async (req, res) => {
  const { title, content, category } = req.body;
  if (!title || !content) {
    return res.status(400).json({ message: 'Title and content are required' });
  }

  try {
    let note;
    if (req.params.id) {
      note = await Note.findByIdAndUpdate(
        req.params.id,
        { title, content, category, updatedAt: Date.now() },
        { new: true }
      );
    } else {
      note = new Note({ title, content, category });
      await note.save();
    }
    res.status(201).json(note);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Delete a note
const deleteNote = async (req, res) => {
  try {
    const note = await Note.findByIdAndDelete(req.params.id);
    if (!note) return res.status(404).json({ message: 'Note not found' });
    res.json({ message: 'Note deleted' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// Search notes
const searchNotes = async (req, res) => {
  const { query } = req.query;
  try {
    const notes = await Note.find({
      $or: [
        { title: { $regex: query, $options: 'i' } },
        { content: { $regex: query, $options: 'i' } },
      ],
    }).populate('category');
    res.json(notes);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

module.exports = {
  getNotes,
  getNoteById,
  saveNote,
  deleteNote,
  searchNotes,
};