import axios from 'axios';

const BASE_URL = 'http://localhost:8000';  // backend running port

export const fetchEngagement = async (params) => {
  return axios.get(`${BASE_URL}/engagement`, { params });
};

export const importCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${BASE_URL}/engagement/import`, formData);
};

export const exportCSV = async (params) => {
  return axios.get(`${BASE_URL}/engagement/export`, {
    params,
    responseType: 'blob'  // important for file download
  });
};
