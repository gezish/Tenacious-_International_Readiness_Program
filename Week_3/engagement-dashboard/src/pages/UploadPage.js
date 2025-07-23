import React, { useState } from 'react';
import { importCSV } from '../api/engagement';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    try {
      await importCSV(file);
      setMsg("CSV uploaded successfully!");
    } catch (err) {
      setMsg("Upload failed.");
    }
  };

  return (
    <div>
      <h2>Upload Engagement CSV</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit">Upload</button>
      </form>
      <p>{msg}</p>
    </div>
  );
}

export default UploadPage;
