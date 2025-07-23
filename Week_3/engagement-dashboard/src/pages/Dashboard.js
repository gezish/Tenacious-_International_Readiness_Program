import React, { useEffect, useState } from 'react';
import { fetchEngagement, exportCSV } from '../api/engagement';

function Dashboard() {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState({});

  useEffect(() => {
    fetchEngagement().then(res => {
      setData(res.data.details);
      setSummary(res.data.summary);
    });
  }, []);

  const handleExport = async () => {
    const res = await exportCSV();
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'engagement_export.csv');
    document.body.appendChild(link);
    link.click();
  };

  return (
    <div>
      <h2>Engagement Summary</h2>
      <pre>{JSON.stringify(summary, null, 2)}</pre>

      <h3>Engagement Logs</h3>
      <table border="1">
        <thead>
          <tr><th>User</th><th>User Type</th><th>Actions</th><th>Date</th></tr>
        </thead>
        <tbody>
          {data.map((log, idx) => (
            <tr key={idx}>
              <td>{log.user}</td>
              <td>{log.user_type}</td>
              <td>{log.actions}</td>
              <td>{log.date}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <button onClick={handleExport}>📤 Export CSV</button>
    </div>
  );
}

export default Dashboard;
