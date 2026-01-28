import React from 'react';
import { FileText } from 'lucide-react';

export default function CitationChips({ citations, visible }) {
  if (!visible || !citations?.length) {
    return null;
  }

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2">
      <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <FileText size={12} />
        Sources:
      </span>
      {citations.map((citation) => (
        <span
          key={`${citation.filename}-${citation.page}`}
          className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700 dark:border-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
        >
          {citation.filename} (p.{citation.page})
        </span>
      ))}
    </div>
  );
}
