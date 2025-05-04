import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [results, setResults] = useState([]);

  const onDrop = useCallback(acceptedFiles => {
    setFiles(prevFiles => [
      ...prevFiles,
      ...acceptedFiles.map(file => ({
        file,
        preview: URL.createObjectURL(file),
        id: Math.random().toString(36).substr(2, 9)
      }))
    ]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: 'image/*, .pdf, .doc, .docx, .txt',
    multiple: true,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  const removeFile = (id) => {
    setFiles(files.filter(file => file.id !== id));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setResults([]);
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file.file);
    });

    try {
      const token = localStorage.getItem('token') || 'demo-token';
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
        onUploadProgress: progressEvent => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(prev => ({
            ...prev,
            [progressEvent.target.upload.filename]: percentCompleted
          }));
        }
      });

      setResults(response.data.results);
      setFiles([]);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container">
      <h1>Secure File Upload</h1>
      
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the files here ...</p>
        ) : (
          <p>Drag 'n' drop files here, or click to select files</p>
        )}
      </div>

      <div className="preview-container">
        <h3>Files to upload:</h3>
        <ul>
          {files.map(file => (
            <li key={file.id}>
              <div className="file-info">
                {file.file.type.startsWith('image/') ? (
                  <img src={file.preview} alt="preview" width="50" />
                ) : (
                  <div className="file-icon">{file.file.type}</div>
                )}
                <span>{file.file.name}</span>
                <span>{(file.file.size / 1024 / 1024).toFixed(2)} MB</span>
                {uploadProgress[file.file.name] && (
                  <progress 
                    value={uploadProgress[file.file.name]} 
                    max="100"
                  />
                )}
              </div>
              <button onClick={() => removeFile(file.id)}>Remove</button>
            </li>
          ))}
        </ul>
      </div>

      <button 
        onClick={uploadFiles} 
        disabled={files.length === 0 || uploading}
        className="upload-button"
      >
        {uploading ? 'Uploading...' : 'Upload Files'}
      </button>

      {results.length > 0 && (
        <div className="results">
          <h3>Upload Results:</h3>
          <ul>
            {results.map((result, index) => (
              <li key={index} className={result.status}>
                {result.filename} - {result.status}
                {result.error && <span>: {result.error}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;