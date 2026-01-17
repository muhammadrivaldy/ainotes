import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

export default function StreamFeed({ messages, streamingMessageId }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-full flex-1 overflow-y-auto scroll-smooth px-4 py-8">
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
