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
