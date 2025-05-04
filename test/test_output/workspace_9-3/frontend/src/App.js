import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CssBaseline, Container, Box } from '@mui/material';
import NotesList from './components/NotesList';
import NoteEditor from './components/NoteEditor';
import NavBar from './components/NavBar';
import Categories from './components/Categories';
import SearchResults from './components/SearchResults';

function App() {
  return (
    <BrowserRouter>
      <CssBaseline />
      <NavBar />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Routes>
            <Route path="/" element={<NotesList />} />
            <Route path="/notes" element={<NotesList />} />
            <Route path="/notes/:id" element={<NoteEditor />} />
            <Route path="/notes/new" element={<NoteEditor />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/search" element={<SearchResults />} />
          </Routes>
        </Box>
      </Container>
    </BrowserRouter>
  );
}

export default App;