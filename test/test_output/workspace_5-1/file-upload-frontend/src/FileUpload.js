import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = () => {
  const onDrop = useCallback((acceptedFiles) => {
    console.log(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.png', '.jpg'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 5 * 1024 * 1024, // 5MB
  });

  return (
    <div {...getRootProps()} style={{
      border: '2px dashed #ccc',
      borderRadius: '4px',
      padding: '20px',
      textAlign: 'center',
      cursor: 'pointer',
      backgroundColor: isDragActive ? '#f0f0f0' : 'white',
    }}>
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop the files here ...</p>
      ) : (
        <p>Drag and drop files here, or click to select files</p>
      )}
    </div>
  );
};

export default FileUpload;