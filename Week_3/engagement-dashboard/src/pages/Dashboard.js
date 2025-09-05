import React, { useEffect, useState } from 'react';
import { fetchEngagement, exportCSV } from '../api/engagement';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

function Dashboard() {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState({});

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch("http://localhost:8000/engagement");
        const result = await res.json();

        setSummary(result.summary || {});
        setData(result.details || []);
      } catch (err) {
        console.error("❌ Failed to fetch engagement:", err);
        setSummary({});
        setData([]);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000);
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
      console.error("❌ Export failed:", err);
    }
  };

  // ✅ Aggregate data for charts
  const actionsByDate = data.reduce((acc, log) => {
    if (!acc[log.date]) acc[log.date] = 0;
    acc[log.date] += log.actions;
    return acc;
  }, {});
  const actionsByDateData = Object.entries(actionsByDate).map(([date, actions]) => ({
    date,
    actions
  }));

  const actionsByUserType = data.reduce((acc, log) => {
    if (!acc[log.user_type]) acc[log.user_type] = 0;
    acc[log.user_type] += log.actions;
    return acc;
  }, {});
  const actionsByUserTypeData = Object.entries(actionsByUserType).map(([user_type, actions]) => ({
    user_type,
    actions
  }));

  return (
    <div className="p-6 space-y-6">
      {/* Summary Cards */}
      <h2 className="text-2xl font-bold mb-4">📊 Engagement Summary</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow-md rounded-2xl p-6 text-center">
          <p className="text-gray-500">Active Users</p>
          <h3 className="text-3xl font-semibold">{summary.active_users ?? 0}</h3>
        </div>
        <div className="bg-white shadow-md rounded-2xl p-6 text-center">
          <p className="text-gray-500">Engagement Score</p>
          <h3 className="text-3xl font-semibold">{summary.engagement_score ?? 0}</h3>
        </div>
        <div className="bg-white shadow-md rounded-2xl p-6 text-center">
          <p className="text-gray-500">Avg Session Time</p>
          <h3 className="text-3xl font-semibold">{summary.avg_session_time ?? 0}</h3>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Line Chart */}
        <div className="bg-white shadow-md rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-4">📈 Actions Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={actionsByDateData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="actions" stroke="#2563eb" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Bar Chart */}
        <div className="bg-white shadow-md rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-4">📊 Actions by User Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={actionsByUserTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="user_type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="actions" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white shadow-md rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-4">📝 Engagement Logs</h3>
        {data.length === 0 ? (
          <p className="text-gray-500">No logs available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 border">User</th>
                  <th className="px-4 py-2 border">User Type</th>
                  <th className="px-4 py-2 border">Actions</th>
                  <th className="px-4 py-2 border">Date</th>
                </tr>
              </thead>
              <tbody>
                {data.map((log, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 border">{log.user}</td>
                    <td className="px-4 py-2 border">{log.user_type}</td>
                    <td className="px-4 py-2 border">{log.actions}</td>
                    <td className="px-4 py-2 border">{log.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Export Button */}
      <div className="flex justify-end">
        <button
          onClick={handleExport}
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg shadow-md transition"
        >
          📤 Export CSV
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
