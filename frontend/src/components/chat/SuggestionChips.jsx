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
import { Lightbulb } from 'lucide-react';

export default function SuggestionChips({ suggestions, onSuggestionClick, visible }) {
  if (!visible || !suggestions?.length) {
    return null;
  }

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <Lightbulb size={12} />
        Related:
      </span>
      {suggestions.map((suggestion) => (
        <button
          key={suggestion.id}
          onClick={() => onSuggestionClick(suggestion)}
          className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-700 transition-all hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:border-blue-500 dark:hover:bg-blue-900/30 dark:hover:text-blue-400"
          title={suggestion.full_content}
        >
          {suggestion.content}
        </button>
      ))}
    </div>
  );
}
