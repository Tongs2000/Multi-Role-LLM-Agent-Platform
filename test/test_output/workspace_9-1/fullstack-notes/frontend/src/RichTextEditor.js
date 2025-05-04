import React, { useState } from 'react';
import { Editor } from '@tinymce/tinymce-react';

const RichTextEditor = ({ onSave }) => {
  const [content, setContent] = useState('');

  return (
    <div className="rich-text-editor">
      <Editor
        apiKey="your-api-key" // Replace with your TinyMCE API key
        value={content}
        onEditorChange={(newContent) => setContent(newContent)}
        init={{
          height: 400,
          menubar: false,
          plugins: 'lists link image paste help wordcount',
          toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | help',
        }}
      />
      <button onClick={() => onSave(content)}>Save Note</button>
    </div>
  );
};

export default RichTextEditor;