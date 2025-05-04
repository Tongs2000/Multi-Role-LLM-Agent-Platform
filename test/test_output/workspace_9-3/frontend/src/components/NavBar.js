import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, TextField, Button, Box, IconButton } from '@mui/material';
import { Search, Add, Category } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const NavBar = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/search?q=${searchQuery}`);
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Notes App
        </Typography>
        
        <Box component="form" onSubmit={handleSearch} sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ mr: 1, backgroundColor: 'white', borderRadius: 1 }}
          />
          <IconButton type="submit" color="inherit">
            <Search />
          </IconButton>
        </Box>
        
        <Button color="inherit" startIcon={<Add />} onClick={() => navigate('/notes/new')}>
          New Note
        </Button>
        <Button color="inherit" startIcon={<Category />} onClick={() => navigate('/categories')}>
          Categories
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;