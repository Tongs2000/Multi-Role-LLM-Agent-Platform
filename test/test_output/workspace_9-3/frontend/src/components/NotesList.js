import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { List, ListItem, ListItemText, Typography, Button, Box, Paper } from '@mui/material';
import axios from 'axios';

const NotesList = () => {
  const [notes, setNotes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const response = await axios.get('/notes/');
        setNotes(response.data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching notes:', error);
      }
    };
    
    fetchNotes();
  }, []);

  if (isLoading) return <Typography>Loading notes...</Typography>;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        Your Notes
      </Typography>
      
      {notes.length === 0 ? (
        <Typography>No notes yet. Create your first note!</Typography>
      ) : (
        <List>
          {notes.map((note) => (
            <ListItem 
              key={note.id} 
              component={Link} 
              to={`/notes/${note.id}`}
              sx={{ 
                mb: 1, 
                border: '1px solid #eee', 
                borderRadius: 1,
                '&:hover': { backgroundColor: '#f5f5f5' }
              }}
            >
              <ListItemText
                primary={note.title}
                secondary={
                  <>
                    <Typography component="span" variant="body2" color="text.primary">
                      {note.category?.name || 'No category'}
                    </Typography>
                    {' — ' + new Date(note.updated_at).toLocaleString()}
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      )}
      
      <Box sx={{ mt: 2 }}>
        <Button 
          variant="contained" 
          component={Link} 
          to="/notes/new"
        >
          Create New Note
        </Button>
      </Box>
    </Paper>
  );
};

export default NotesList;