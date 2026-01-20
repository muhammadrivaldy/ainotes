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
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { loginWithGoogle } from '../services/api';
import { BookOpen, Moon, Sun } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSuccess = async (credentialResponse) => {
    setError(null);
    setIsLoading(true);

    try {
      // Authenticate with backend
      const authData = await loginWithGoogle(credentialResponse.credential);

      // Store user data from backend response
      const userData = {
        id: authData.user.id,
        name: authData.user.name,
        email: authData.user.email,
        picture: authData.user.picture,
      };

      login(userData);
      navigate('/');
    } catch (err) {
      console.error('Failed to authenticate:', err);
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleError = () => {
    console.error('Google Login Failed');
    setError('Google sign-in failed. Please try again.');
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-50 dark:bg-gray-900">
      {/* Theme Toggle */}
      <div className="absolute top-4 right-4">
        <button onClick={toggleTheme} className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-gray-800">
          {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col items-center justify-center px-4">
        {/* Logo */}
        <div className="mb-8 flex items-center">
          <BookOpen className="h-12 w-12 text-blue-600 dark:text-blue-400" />
          <span className="ml-3 text-3xl font-bold text-gray-900 dark:text-gray-100">AI Notes</span>
        </div>

        {/* Login Card */}
        <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg dark:bg-gray-800">
          <h1 className="mb-2 text-center text-2xl font-bold text-gray-900 dark:text-gray-100">Welcome Back</h1>
          <p className="mb-8 text-center text-gray-600 dark:text-gray-400">Sign in to access your notes</p>

          {/* Error Message */}
          {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-center text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">{error}</div>}

          {/* Loading State */}
          {isLoading && <div className="mb-4 text-center text-gray-600 dark:text-gray-400">Signing in...</div>}

          {/* Google Sign-In Button */}
          <div className="flex justify-center">
            <GoogleLogin onSuccess={handleSuccess} onError={handleError} theme={theme === 'dark' ? 'filled_black' : 'outline'} size="large" shape="rectangular" text="signin_with" width="300" />
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-sm text-gray-500 dark:text-gray-400">Your second brain for notes and ideas</p>
      </div>
    </div>
  );
}
