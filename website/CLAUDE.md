# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
npm run dev       # Start development server (http://localhost:4321)
npm run build     # Build for production (output: dist/)
npm run preview   # Preview production build locally
```

## Architecture

This is an open-source landing page template for AI Notes built with **Astro 5.16**, **Tailwind CSS**, and **React** for interactive components. Users can fork, customize, and self-host/deploy this project.

### Key Directories

- `src/components/` - Astro and React components (Hero, Features, LifeStreamDemo, Benefits, CTA, Footer)
- `src/layouts/BaseLayout.astro` - Master HTML layout
- `src/pages/index.astro` - Landing page entry point
- `src/lib/translations.ts` - i18n translation strings (English & Indonesian)
- `src/scripts/i18n.ts` - Client-side language switching logic

### Internationalization System

The site supports English (en) and Indonesian (id) using a custom i18n approach:
1. Astro components use `data-i18n` attributes on translatable elements
2. `src/scripts/i18n.ts` listens for `languageChange` events and updates DOM
3. `LanguageSwitcher.tsx` (React) handles user language selection and persists to localStorage
4. Translations are defined in `src/lib/translations.ts`

When adding new translatable content, add the translation key to `translations.ts` and use `data-i18n="key"` in the markup.

### Styling

All styling uses Tailwind utility classes. Custom primary colors are defined in `tailwind.config.mjs`.
