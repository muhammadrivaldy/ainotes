/*
    AI Notes Landing Page - Open-source landing page template
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

import { useState, useEffect } from 'react';
import { translations, type Language } from '../lib/translations';

interface TranslatedPageProps {
  children: (t: typeof translations.en) => React.ReactNode;
}

export default function TranslatedPage({ children }: TranslatedPageProps) {
  const [language, setLanguage] = useState<Language>('en');

  useEffect(() => {
    const saved = localStorage.getItem('language') as Language;
    if (saved && (saved === 'en' || saved === 'id')) {
      setLanguage(saved);
    }

    const handleLanguageChange = (event: CustomEvent<Language>) => {
      setLanguage(event.detail);
    };

    window.addEventListener('languageChange', handleLanguageChange as EventListener);
    return () => {
      window.removeEventListener('languageChange', handleLanguageChange as EventListener);
    };
  }, []);

  return <>{children(translations[language])}</>;
}
