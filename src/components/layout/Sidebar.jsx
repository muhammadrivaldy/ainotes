import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { Settings, User, Moon, Sun, BookOpen, PanelLeftClose } from 'lucide-react';

export default function Sidebar({ onClose }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="flex h-full w-64 flex-col">
      {/* Header / Logo */}
      <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4 dark:border-gray-800">
        <div className="flex items-center">
          <BookOpen className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          <span className="ml-3 text-lg font-bold text-gray-900 dark:text-gray-100">AI Notes</span>
        </div>
        <button
          onClick={onClose}
          className="rounded-md p-1.5 text-gray-500 transition-colors hover:bg-gray-200 dark:hover:bg-gray-800"
          title="Close Sidebar"
        >
          <PanelLeftClose size={20} />
        </button>
      </div>

      {/* Navigation (Placeholder) */}
      <nav className="flex flex-1 flex-col gap-2 px-3 py-6">
        <SidebarItem icon={<Settings />} label="Settings" />
        <SidebarItem icon={<User />} label="Profile" />
      </nav>

      {/* Footer / Theme Toggle */}
      <div className="border-t border-gray-200 p-4 dark:border-gray-800">
        <button
          onClick={toggleTheme}
          className="flex w-full items-center rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          <span className="ml-3 font-medium">{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
        </button>
      </div>
    </aside>
  );
}

function SidebarItem({ icon, label }) {
  return (
    <button className="flex w-full items-center rounded-lg p-2.5 text-gray-700 transition-colors hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800">
      <div className="h-5 w-5">{React.cloneElement(icon, { size: 20 })}</div>
      <span className="ml-3 text-sm font-medium">{label}</span>
    </button>
  );
}
