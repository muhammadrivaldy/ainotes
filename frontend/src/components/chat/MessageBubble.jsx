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
import TagChips from './TagChips';
import CitationChips from './CitationChips';

export default function MessageBubble({ message, isStreaming = false }) {
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

  // Parse citations from AI response (format: "[Source: filename.pdf, Page X]")
  const parseCitations = (content) => {
    const citationRegex = /\[Source:\s*(.+?)(?=,\s*page\b),\s*page\s*(\d+)\]/gi;
    const citations = [];
    const seen = new Set();
    let match;
    while ((match = citationRegex.exec(content)) !== null) {
      const key = `${match[1].trim()}:${match[2]}`;
      if (!seen.has(key)) {
        seen.add(key);
        citations.push({ filename: match[1].trim(), page: match[2] });
      }
    }
    return citations;
  };

  // Strip citation markers from displayed content
  const stripCitations = (content) => {
    return content.replace(/\n*\[Source:\s*[^\]]+\]/g, '').trim();
  };

  const tags = !isUser && message.role === 'assistant' ? parseTags(message.content) : [];
  const showTags = tags.length > 0;
  const citations = !isUser && message.role === 'assistant' ? parseCitations(message.content) : [];
  const showCitations = citations.length > 0;
  const cleanContent = showCitations ? stripCitations(contentToDisplay) : contentToDisplay;

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
          <div className={`prose prose-sm max-w-none wrap-break-word ${isUser ? 'prose-invert' : 'dark:prose-invert'}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>{cleanContent}</ReactMarkdown>
          </div>
        </div>

        {/* Citation chips - shown below AI message bubble for document sources */}
        <CitationChips citations={citations} visible={showCitations} />

        {/* Tag chips - shown below AI message bubble */}
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
