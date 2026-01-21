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
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Bot, User } from 'lucide-react';
import { useTypewriter } from '../../hooks/useTypewriter';
import { useAuth } from '../../context/AuthContext';
import SuggestionChips from './SuggestionChips';
import TagChips from './TagChips';

export default function MessageBubble({ message, isStreaming = false, suggestions = [], onSuggestionClick }) {
  const { user } = useAuth();
  const isUser = message.role === 'user';
  const { displayedText, isComplete } = useTypewriter(message.content, 20, isStreaming && !isUser);

  const contentToDisplay = isStreaming && !isUser ? displayedText : message.content;

  // Parse tags from AI response (format: "Information stored successfully with tags: work, meeting")
  const parseTags = (content) => {
    const tagMatch = content.match(/with tags?: ([^\n.]+)/i);
    if (tagMatch) {
      return tagMatch[1].split(',').map(tag => tag.trim()).filter(t => t);
    }
    return [];
  };

  const tags = !isUser && message.role === 'assistant' ? parseTags(message.content) : [];
  const showTags = tags.length > 0;

  // Show suggestions only for AI messages after typewriter completes
  const showSuggestions = !isUser && isComplete && suggestions.length > 0;

  return (
    <div className={`group mb-6 flex w-full items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* AI Avatar - Left side */}
      {!isUser && (
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-purple-500 to-indigo-600 shadow-sm">
          <Bot className="h-5 w-5 text-white" />
        </div>
      )}

      <div className="flex max-w-[80%] flex-col md:max-w-[70%]">
        <div
          className={`relative rounded-2xl p-4 shadow-sm ${
            isUser ? 'rounded-br-sm bg-blue-600 text-white' : 'rounded-bl-sm border border-gray-200 bg-white text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100'
          }`}
        >
          <div className={`prose prose-sm max-w-none break-words ${isUser ? 'prose-invert' : 'dark:prose-invert'}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{contentToDisplay}</ReactMarkdown>
          </div>
        </div>

        {/* Suggestion chips - shown below AI message bubble */}
        <SuggestionChips suggestions={suggestions} onSuggestionClick={onSuggestionClick} visible={showSuggestions} />
        <TagChips tags={tags} visible={showTags} />
      </div>

      {/* User Avatar - Right side */}
      {isUser && (
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full shadow-sm">
          {user?.picture ? (
            <img src={user.picture} alt={user.name || 'User'} referrerPolicy="no-referrer" className="h-12 w-12 rounded-full object-cover" />
          ) : (
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-linear-to-br from-blue-500 to-blue-700">
              <User className="h-5 w-5 text-white" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
