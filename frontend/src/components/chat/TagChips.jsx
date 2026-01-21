import React from 'react';
import { Tag } from 'lucide-react';

export default function TagChips({ tags, visible }) {
  if (!visible || !tags?.length) {
    return null;
  }

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2">
      <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <Tag size={12} />
        Tags:
      </span>
      {tags.map((tag, index) => (
        <span
          key={index}
          className="rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs text-purple-700 dark:border-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
        >
          #{tag}
        </span>
      ))}
    </div>
  );
}
