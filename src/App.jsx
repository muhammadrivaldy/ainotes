import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import AppLayout from './components/layout/AppLayout';
import StreamFeed from './components/chat/StreamFeed';
import InputArea from './components/chat/InputArea';
import { sendMessage, getChatHistory } from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

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
      if (transformedMessages.length === 0) {
        setMessages([
          {
            id: 'welcome',
            role: 'ai',
            content:
              '## Welcome to your Second Brain! 🧠\n\nI am ready to help you store and retrieve your notes. Just start typing whatever is on your mind!',
          },
        ]);
      } else {
        setMessages(transformedMessages);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
      // Show welcome message with error notice
      setMessages([
        {
          id: 'welcome',
          role: 'ai',
          content:
            '## Welcome to your Second Brain! 🧠\n\n⚠️ **Backend connection failed.** Please ensure the backend server is running on port 8000.',
        },
      ]);
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
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== 'loading')
          .concat({
            id: Date.now() + 1,
            role: 'ai',
            content: response.response,
          })
      );
    } catch (err) {
      console.error('Failed to send message:', err);

      // Replace loading message with error
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== 'loading')
          .concat({
            id: Date.now() + 1,
            role: 'ai',
            content: '⚠️ **Error:** Failed to get response from backend. Please try again.',
          })
      );
    }
  };

  const handleClear = () => {
    // Clear only the local view, database remains intact
    setMessages([
      {
        id: 'welcome',
        role: 'ai',
        content:
          '## Welcome to your Second Brain! 🧠\n\nI am ready to help you store and retrieve your notes. Just start typing whatever is on your mind!',
      },
    ]);
  };

  return (
    <ThemeProvider>
      <AppLayout>
        <StreamFeed messages={messages} />
        <InputArea onSend={handleSend} onClear={handleClear} />
      </AppLayout>
    </ThemeProvider>
  );
}

export default App;
