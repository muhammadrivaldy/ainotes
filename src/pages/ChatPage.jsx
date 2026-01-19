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
import React, { useState, useEffect } from 'react';
import AppLayout from '../components/layout/AppLayout';
import StreamFeed from '../components/chat/StreamFeed';
import InputArea from '../components/chat/InputArea';
import { sendMessage, getChatHistory, clearChatHistory } from '../services/api';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [streamingMessageId, setStreamingMessageId] = useState(null);

  // Load chat history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const history = await getChatHistory();

      // Transform backend format to frontend format
      const transformedMessages = history.map((msg) => ({
        id: msg.id,
        role: msg.role === 'assistant' ? 'ai' : msg.role,
        content: msg.content,
      }));

      // Add welcome message if history is empty
      if (transformedMessages.length > 0) {
        setMessages(transformedMessages);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (text) => {
    // 1. Add User Message immediately
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);

    // 2. Add loading indicator
    const loadingMsg = {
      id: 'loading',
      role: 'ai',
      content: '_Thinking..._',
    };

    setMessages((prev) => [...prev, loadingMsg]);

    try {
      // 3. Call backend API
      const response = await sendMessage(text);

      // 4. Replace loading message with AI response
      const aiMessageId = Date.now() + 1;
      const messageContent = response.response;
      setStreamingMessageId(aiMessageId);

      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== 'loading')
          .concat({
            id: aiMessageId,
            role: 'ai',
            content: messageContent,
          })
      );

      // Clear streaming state after typewriter effect completes
      // Speed is 20ms per character
      const estimatedDuration = messageContent.length * 20 + 500;
      setTimeout(() => {
        setStreamingMessageId(null);
      }, estimatedDuration);
    } catch (err) {
      console.error('Failed to send message:', err);

      // Replace loading message with error
      const errorMessageId = Date.now() + 1;
      const errorContent = '⚠️ **Error:** Failed to get response from backend. Please try again.';
      setStreamingMessageId(errorMessageId);

      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== 'loading')
          .concat({
            id: errorMessageId,
            role: 'ai',
            content: errorContent,
          })
      );

      // Clear streaming state after typewriter effect completes
      const estimatedDuration = errorContent.length * 20 + 500;
      setTimeout(() => {
        setStreamingMessageId(null);
      }, estimatedDuration);
    }
  };

  const handleClear = async () => {
    try {
      // Clear chat history from backend database
      await clearChatHistory();

      // Clear local state to remove chat bubbles immediately
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
      // Show error message to user
      const errorMsg = {
        id: Date.now(),
        role: 'ai',
        content: '⚠️ **Error:** Failed to clear chat history. Please try again.',
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <AppLayout>
      <StreamFeed messages={messages} streamingMessageId={streamingMessageId} />
      <InputArea onSend={handleSend} onClear={handleClear} />
    </AppLayout>
  );
}
