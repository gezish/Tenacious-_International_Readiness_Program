import React, { useEffect, useState } from 'react';
import { fetchEngagement, exportCSV } from '../api/engagement';

function Dashboard() {
  const [data, setData] = useState([]);        // engagement details (array)
  const [summary, setSummary] = useState({});  // summary stats (object)

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch("http://localhost:8000/engagement");
        const json = await res.json();

        // ✅ Expecting { summary: {...}, details: [...] }
        setSummary(json.summary || {});
        setData(json.details || []);
      } catch (err) {
        console.error("Failed to fetch engagement data:", err);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000); // auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleExport = async () => {
    try {
      const res = await exportCSV();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'engagement_export.csv');
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error("Export failed:", err);
    }
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
          {data.length > 0 ? (
            data.map((log, idx) => (
              <tr key={idx}>
                <td>{log.user}</td>
                <td>{log.user_type}</td>
                <td>{log.actions}</td>
                <td>{log.date}</td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="4">No engagement data available</td></tr>
          )}
        </tbody>
      </table>

      <button onClick={handleExport}>📤 Export CSV</button>
    </div>
  );
}

export default Dashboard;
