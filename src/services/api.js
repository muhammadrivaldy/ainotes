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

/**
 * Send a message to the AI assistant
 * @param {string} message - The user's message
 * @returns {Promise<{response: string}>} - The AI's response
 */
export const sendMessage = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        history: [], // Backend tracks history in database
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return await response.json();
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
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch history');
    }

    return await response.json();
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
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to clear history');
    }

    return await response.json();
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
