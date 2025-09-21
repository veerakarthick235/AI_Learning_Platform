// src/services/api.js

import axios from 'axios';

// Get the backend URL from the environment variable
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

// Create a configured instance of axios
const apiClient = axios.create({
  baseURL: API_URL,
});

/**
 * Gets a token from localStorage and sets it in the request header.
 */
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// ======================= MODIFIED SECTION START =======================
/**
 * Sends a request to the backend to generate learning resources.
 * @param {object} params - The parameters for the resource (subtopic, description, etc.).
 * @returns {Promise<string>} - The generated markdown text from the AI.
 */
export const generateResource = async (params) => {
  try {
    const response = await apiClient.post('/api/generate-resource', params);
    return response.data; // Assuming the backend returns the markdown directly
  } catch (error) {
    console.error("Error generating resource:", error);
    // Re-throw a more user-friendly error message
    throw new Error(error.response?.data?.error || "Failed to generate resources.");
  }
};
// ======================== MODIFIED SECTION END ========================

// Add other API functions like loginUser, getProfile, etc., here.
export const loginUser = async (credentials) => {
  const response = await apiClient.post('/login', credentials);
  return response.data;
};