/*
    AI Notes - A modern web-based "Second Brain" application
    Copyright (C) 2026 Rivaldy

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
import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2 } from 'lucide-react';

export default function InputArea({ onSend, onClear, disabled }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  return (
    <div className="mx-auto w-full max-w-4xl p-4 pb-6">
      <div className="relative flex items-center gap-2 rounded-3xl border border-gray-200 bg-white p-2 shadow-lg transition-colors dark:border-gray-700 dark:bg-gray-800">
        {/* Clear Button */}
        <button
          type="button"
          onClick={onClear}
          className="rounded-full p-3 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/20"
          title="Clear conversation"
        >
          <Trash2 size={20} />
        </button>

        {/* Text Area */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a note or ask anything..."
          rows={1}
          className="max-h-48 w-full resize-none border-0 bg-transparent p-0 leading-6 text-gray-900 outline-none placeholder:text-gray-400 focus:ring-0 focus:outline-none dark:text-gray-100"
          style={{ minHeight: '24px' }}
        />

        {/* Send Button */}
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || disabled}
          className={`rounded-full p-3 transition-all duration-200 ${
            input.trim() && !disabled
              ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
              : 'cursor-not-allowed bg-gray-100 text-gray-400 dark:bg-gray-700'
          }`}
        >
          <Send size={20} />
        </button>
      </div>
      <div className="mt-2 text-center">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          AI Notes can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
