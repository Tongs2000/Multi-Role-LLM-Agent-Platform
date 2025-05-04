import React, { useReducer, useState } from 'react';
import ImageUploader from './ImageUploader';
import FabricCanvas from './FabricCanvas';
import Toolbar from './Toolbar';
import FilterPanel from './FilterPanel';
import PresetFilters from './PresetFilters';
import LayerPanel from './LayerPanel';
import SaveButton from './SaveButton';
import './styles.css';

const initialState = {
  image: null,
  edits: [],
  activeTool: null,
  selectedRegion: null,
  filters: { brightness: 50, contrast: 50, saturation: 50 },
  presets: [
    { id: 1, name: 'Vintage', config: { brightness: 70, contrast: 30 } },
    { id: 2, name: 'Monochrome', config: { saturation: 0 } },
  ],
  layers: [{ id: 1, name: 'Base Layer', visible: true, opacity: 100 }],
  loading: false,
  error: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_IMAGE':
      return { ...state, image: action.payload, edits: [] };
    case 'ADD_EDIT':
      return { ...state, edits: [...state.edits, action.payload] };
    case 'SET_ACTIVE_TOOL':
      return { ...state, activeTool: action.payload };
    case 'SET_SELECTED_REGION':
      return { ...state, selectedRegion: action.payload };
    case 'SET_FILTERS':
      return { ...state, filters: action.payload };
    case 'SET_LAYERS':
      return { ...state, layers: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const handleFilterChange = (name, value) => {
    dispatch({ type: 'SET_FILTERS', payload: { ...state.filters, [name]: value } });
  };

  const handlePresetSelect = (preset) => {
    dispatch({ type: 'SET_FILTERS', payload: { ...state.filters, ...preset.config } });
  };

  const handleLayerUpdate = (id, updates) => {
    const updatedLayers = state.layers.map((layer) =>
      layer.id === id ? { ...layer, ...updates } : layer
    );
    dispatch({ type: 'SET_LAYERS', payload: updatedLayers });
  };

  return (
    <div className="app">
      <h1>Image Processing System</h1>
      <ImageUploader dispatch={dispatch} />
      <div className="editor-container">
        <FabricCanvas image={state.image} />
        <Toolbar state={state} dispatch={dispatch} />
        <FilterPanel filters={state.filters} onFilterChange={handleFilterChange} />
        <PresetFilters presets={state.presets} onPresetSelect={handlePresetSelect} />
        <LayerPanel layers={state.layers} onLayerUpdate={handleLayerUpdate} />
      </div>
      <SaveButton state={state} dispatch={dispatch} />
      {state.error && <div className="error">{state.error}</div>}
      {state.loading && <div className="loading">Loading...</div>}
    </div>
  );
}