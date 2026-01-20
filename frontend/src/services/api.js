/*
    AI Notes - A modern web-based "Second Brain" application
    Copyright (C) 2026 AI Notes

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
// API Service for AI Notes Backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token management
const TOKEN_KEY = 'auth_token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const removeToken = () => localStorage.removeItem(TOKEN_KEY);

/**
 * Get authorization headers with JWT token
 * @returns {Object} Headers object with Authorization if token exists
 */
const getAuthHeaders = () => {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

/**
 * Handle API response and check for auth errors
 * @param {Response} response - Fetch response object
 * @returns {Promise<any>} - Parsed response data
 */
const handleResponse = async (response) => {
  if (response.status === 401) {
    // Token expired or invalid - clear auth state
    removeToken();
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
};

/**
 * Authenticate with Google OAuth credential
 * @param {string} credential - Google OAuth credential token
 * @returns {Promise<{access_token: string, user: object}>}
 */
export const loginWithGoogle = async (credential) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ credential }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Authentication failed');
    }

    const data = await response.json();
    setToken(data.access_token);
    return data;
  } catch (error) {
    console.error('Error during Google authentication:', error);
    throw error;
  }
};

/**
 * Get current authenticated user info
 * @returns {Promise<object>} - User object
 */
export const getCurrentUser = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  } catch (error) {
    console.error('Error fetching current user:', error);
    throw error;
  }
};

/**
 * Send a message to the AI assistant
 * @param {string} message - The user's message
 * @returns {Promise<{response: string}>} - The AI's response
 */
export const sendMessage = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        message: message,
        history: [], // Backend tracks history in database
      }),
    });

    return handleResponse(response);
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Retrieve chat history from the backend
 * @returns {Promise<Array<{id: number, role: string, content: string, timestamp: string}>>}
 */
export const getChatHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/history`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  } catch (error) {
    console.error('Error fetching history:', error);
    throw error;
  }
};

/**
 * Clear all chat history from the backend
 * @returns {Promise<{status: string}>}
 */
export const clearChatHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/history`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  } catch (error) {
    console.error('Error clearing history:', error);
    throw error;
  }
};

/**
 * Check if the backend is healthy
 * @returns {Promise<{status: string}>}
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Backend is not responding');
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

/**
 * Logout - clear all auth data
 */
export const logout = () => {
  removeToken();
  localStorage.removeItem('user');
};
