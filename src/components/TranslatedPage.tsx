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
