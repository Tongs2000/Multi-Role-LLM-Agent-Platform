import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Select, MenuItem, FormControl, InputLabel, Typography } from '@mui/material';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import axios from 'axios';

const NoteEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const editor = useEditor({
    extensions: [StarterKit],
    content: '<p>Start writing your note here...</p>',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes, noteRes] = await Promise.all([
          axios.get('/categories/'),
          id ? axios.get(`/notes/${id}`) : Promise.resolve(null)
        ]);
        
        setCategories(categoriesRes.data);
        
        if (noteRes) {
          setTitle(noteRes.data.title);
          setCategory(noteRes.data.category_id || '');
          editor.commands.setContent(noteRes.data.content);
        }
        
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    
    fetchData();
  }, [id, editor]);

  const handleSave = async () => {
    try {
      const noteData = {
        title,
        content: editor.getHTML(),
        category_id: category || null
      };
      
      if (id) {
        await axios.put(`/notes/${id}`, noteData);
      } else {
        await axios.post('/notes/', noteData);
      }
      
      navigate('/notes');
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  if (isLoading) return <Typography>Loading...</Typography>;

  return (
    <Box sx={{ mt: 3 }}>
      <TextField
        fullWidth
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        sx={{ mb: 2 }}
      />
      
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Category</InputLabel>
        <Select
          value={category}
          label="Category"
          onChange={(e) => setCategory(e.target.value)}
        >
          <MenuItem value="">None</MenuItem>
          {categories.map((cat) => (
            <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <Box sx={{ 
        border: '1px solid #ccc', 
        borderRadius: 1, 
        p: 2, 
        minHeight: 300,
        mb: 2
      }}>
        <EditorContent editor={editor} />
      </Box>
      
      <Button variant="contained" onClick={handleSave}>
        Save
      </Button>
    </Box>
  );
};

export default NoteEditor;