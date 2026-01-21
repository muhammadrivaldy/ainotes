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
import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

export default function StreamFeed({ messages, streamingMessageId }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-full flex-1 overflow-y-auto scroll-smooth px-4 pt-8">
      <div className="mx-auto flex min-h-full max-w-4xl flex-col justify-end">
        {messages.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center space-y-4 text-gray-400 dark:text-gray-600">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100 dark:bg-gray-800">
              <span className="text-4xl">✨</span>
            </div>
            <p className="text-lg font-medium">Start your note stream...</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isStreaming={msg.id === streamingMessageId}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
