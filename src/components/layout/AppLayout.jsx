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
import React, { useState } from 'react';
import Sidebar from './Sidebar';
import { PanelLeftOpen } from 'lucide-react';

export default function AppLayout({ children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-white text-gray-900 transition-colors duration-200 dark:bg-gray-900 dark:text-gray-100">
      <div
        className={`${isSidebarOpen ? 'w-64' : 'w-0'} shrink-0 overflow-hidden border-r border-gray-200 bg-gray-50 transition-all duration-300 ease-in-out dark:border-gray-800 dark:bg-gray-950`}
      >
        <Sidebar onClose={() => setIsSidebarOpen(false)} />
      </div>

      <main className="relative flex h-full flex-1 flex-col">
        {!isSidebarOpen && (
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="absolute top-4 left-4 z-50 rounded-md p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
            title="Open Sidebar"
          >
            <PanelLeftOpen size={24} />
          </button>
        )}
        {children}
      </main>
    </div>
  );
}
