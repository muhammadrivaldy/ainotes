# AI Notes - Landing Page

A clean, simple landing page for AI Notes, your Second Brain application. Built with Astro and Tailwind CSS.

## Overview

AI Notes is a conversational knowledge base that helps you store and retrieve information naturally through conversation. This landing page focuses on explaining why people need this application and how it solves real problems.

## Tech Stack

- **Framework:** Astro 5.16
- **Styling:** Tailwind CSS 3.4
- **Language:** TypeScript (strict mode)

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm package manager

### Installation

1. Install dependencies:

    ```bash
    npm install
    ```

2. Start the development server:

    ```bash
    npm run dev
    ```

3. Open your browser and visit

    ```text
    http://localhost:3000
    ```

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```js
ainotes/
├── public/
│   └── favicon.svg          # Site favicon
├── src/
│   ├── components/
│   │   ├── Hero.astro       # Hero section with image placeholder
│   │   ├── Features.astro   # Why you need AI Notes
│   │   ├── LifeStreamDemo.astro # How it works (with image placeholder)
│   │   ├── Benefits.astro   # Perfect for... use cases
│   │   ├── CTA.astro        # Call-to-action
│   │   └── Footer.astro     # Simple footer
│   ├── layouts/
│   │   └── BaseLayout.astro # Base HTML layout
│   └── pages/
│       └── index.astro      # Landing page entry point
├── astro.config.mjs         # Astro configuration
├── tailwind.config.mjs      # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Page Sections

### Hero Section

- Clean headline: "Your Second Brain"
- Simple description of what the app does
- Image placeholder for your screenshot

### Why You Need AI Notes

- Focuses on problems people face:
  - Forgetting important things
  - Traditional note apps are too complicated
  - Information overload
  - Easy to use (like ChatGPT)

### How It Works

- Simple 3-step process
- Image placeholder for demo screenshot

### Perfect For

- Knowledge workers use cases
- Personal use cases
- Comparison table showing the difference

### Call-to-Action

- Simple, clean CTA section
- Get Started button

### Footer

- Minimal footer with essential links

## Design Philosophy

- **Clean & Simple:** No fancy gradients or decorative elements
- **Content-Focused:** Let the value proposition speak for itself
- **Image Placeholders:** Easy to replace with your actual screenshots
- **Mobile-Responsive:** Works on all screen sizes

## Adding Your Images

Replace the placeholder sections with your actual images:

1. **Hero Image** (src/components/Hero.astro:24): Replace the placeholder div with your main app screenshot
2. **Demo Image** (src/components/LifeStreamDemo.astro:12): Replace with your demo/how-it-works screenshot

## License

ISC
