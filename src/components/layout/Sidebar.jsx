import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { Settings, User, Moon, Sun, BookOpen, PanelLeftClose, LogOut } from 'lucide-react';

export default function Sidebar({ onClose }) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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

      {/* User Profile Section */}
      {user && (
        <div className="border-t border-gray-200 p-4 dark:border-gray-800">
          <div className="flex items-center gap-3">
            {user.picture ? (
              <img
                src={user.picture}
                alt={user.name}
                referrerPolicy="no-referrer"
                className="h-10 w-10 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white">
                {user.name?.charAt(0) || 'U'}
              </div>
            )}
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                {user.name}
              </p>
              <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Footer / Theme Toggle & Logout */}
      <div className="border-t border-gray-200 p-4 dark:border-gray-800">
        <button
          onClick={toggleTheme}
          className="flex w-full items-center rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          <span className="ml-3 font-medium">{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
        </button>
        <button
          onClick={handleLogout}
          className="mt-2 flex w-full items-center rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          <LogOut className="h-5 w-5" />
          <span className="ml-3 font-medium">Logout</span>
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
