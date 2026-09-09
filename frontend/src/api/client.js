import axios from 'axios';

const API_BASE = '/api/v1';

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE}/upload/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getDocuments = async (status = null) => {
  const params = status ? { status } : {};
  const response = await axios.get(`${API_BASE}/documents/`, { params });
  return response.data;
};

export const getDocumentById = async (id) => {
  const response = await axios.get(`${API_BASE}/documents/${id}`);
  return response.data;
};

export const verifyDocument = async (id, payload) => {
  const response = await axios.post(`${API_BASE}/review/${id}/verify`, payload);
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await axios.get(`${API_BASE}/dashboard/stats`);
  return response.data;
};
