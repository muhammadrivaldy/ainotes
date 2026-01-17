import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useTypewriter } from '../../hooks/useTypewriter';

export default function MessageBubble({ message, isStreaming = false }) {
  const isUser = message.role === 'user';
  const { displayedText, isComplete } = useTypewriter(
    message.content,
    20,
    isStreaming && !isUser
  );

  const contentToDisplay = isStreaming && !isUser ? displayedText : message.content;

  const displayContent = useMemo(() => {
    const safeSplitParts = contentToDisplay.split(/(```[\s\S]*?```)/g);

    return safeSplitParts
      .map((part) => {
        if (part.startsWith('```')) return part;

        return part.replace(/\n{2,}/g, (match) => {
          return '\n&nbsp;\n'.repeat(match.length - 1);
        });
      })
      .join('');
  }, [contentToDisplay]);

  return (
    <div className={`group mb-6 flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`relative max-w-[80%] rounded-2xl p-4 shadow-sm md:max-w-[70%] ${
          isUser
            ? 'rounded-br-sm bg-blue-600 text-white'
            : 'rounded-bl-sm border border-gray-200 bg-white text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100'
        }`}
      >
        <div className="prose prose-sm dark:prose-invert wrap-break-words max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{displayContent}</ReactMarkdown>
          {isStreaming && !isUser && !isComplete && (
            <span className="ml-1 inline-block h-4 w-0.5 animate-pulse bg-gray-800 dark:bg-gray-100" />
          )}
        </div>
      </div>
    </div>
  );
}
