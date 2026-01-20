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

import { translations, type Language } from '../lib/translations';

function getCurrentLanguage(): Language {
  const saved = localStorage.getItem('language') as Language;
  return saved === 'en' || saved === 'id' ? saved : 'en';
}

function updatePageContent(lang: Language) {
  const t = translations[lang];

  // Update nav links
  const navLinks = document.querySelectorAll('.nav-link');
  if (navLinks[0]) navLinks[0].textContent = t.nav.whyAiNotes;
  if (navLinks[1]) navLinks[1].textContent = t.nav.howItWorks;

  const navCta = document.querySelector('.nav-cta');
  if (navCta) navCta.textContent = t.nav.getStarted;

  // Update hero section
  updateElementText('[data-i18n="hero.badge"]', t.hero.badge);
  updateElementText('[data-i18n="hero.title"]', t.hero.title);
  updateElementText('[data-i18n="hero.titleHighlight"]', t.hero.titleHighlight);
  updateElementText('[data-i18n="hero.subtitle"]', t.hero.subtitle);
  updateElementText('[data-i18n="hero.ctaPrimary"]', t.hero.ctaPrimary);
  updateElementText('[data-i18n="hero.ctaSecondary"]', t.hero.ctaSecondary);
  updateElementText('[data-i18n="hero.openSource"]', t.hero.openSource);
  updateElementText('[data-i18n="hero.selfHost"]', t.hero.selfHost);
  updateElementText('[data-i18n="hero.yourData"]', t.hero.yourData);
  updateElementText('[data-i18n="hero.imageAlt"]', t.hero.imageAlt);

  // Update features section
  updateElementText('[data-i18n="features.badge"]', t.features.badge);
  updateElementText('[data-i18n="features.title"]', t.features.title);
  updateElementText('[data-i18n="features.subtitle"]', t.features.subtitle);
  updateElementText('[data-i18n="features.forgetThings.title"]', t.features.forgetThings.title);
  updateElementText('[data-i18n="features.forgetThings.description"]', t.features.forgetThings.description);
  updateElementText('[data-i18n="features.tooComplicated.title"]', t.features.tooComplicated.title);
  updateElementText('[data-i18n="features.tooComplicated.description"]', t.features.tooComplicated.description);
  updateElementText('[data-i18n="features.dataOwnership.title"]', t.features.dataOwnership.title);
  updateElementText('[data-i18n="features.dataOwnership.description"]', t.features.dataOwnership.description);
  updateElementText('[data-i18n="features.customizable.title"]', t.features.customizable.title);
  updateElementText('[data-i18n="features.customizable.description"]', t.features.customizable.description);

  // Update demo section
  updateElementText('[data-i18n="demo.badge"]', t.demo.badge);
  updateElementText('[data-i18n="demo.title"]', t.demo.title);
  updateElementText('[data-i18n="demo.subtitle"]', t.demo.subtitle);
  updateElementText('[data-i18n="demo.imagePlaceholder"]', t.demo.imagePlaceholder);
  updateElementText('[data-i18n="demo.step1.title"]', t.demo.step1.title);
  updateElementText('[data-i18n="demo.step1.description"]', t.demo.step1.description);
  updateElementText('[data-i18n="demo.step2.title"]', t.demo.step2.title);
  updateElementText('[data-i18n="demo.step2.description"]', t.demo.step2.description);
  updateElementText('[data-i18n="demo.step3.title"]', t.demo.step3.title);
  updateElementText('[data-i18n="demo.step3.description"]', t.demo.step3.description);

  // Update benefits section
  updateElementText('[data-i18n="benefits.title"]', t.benefits.title);
  updateElementText('[data-i18n="benefits.subtitle"]', t.benefits.subtitle);
  updateElementText('[data-i18n="benefits.knowledgeWorkers.title"]', t.benefits.knowledgeWorkers.title);
  updateElementText('[data-i18n="benefits.personalUse.title"]', t.benefits.personalUse.title);
  updateElementText('[data-i18n="benefits.developers.title"]', t.benefits.developers.title);

  // Update knowledge workers items
  t.benefits.knowledgeWorkers.items.forEach((item, index) => {
    updateElementText(`[data-i18n="benefits.knowledgeWorkers.item${index}"]`, item);
  });

  // Update personal use items
  t.benefits.personalUse.items.forEach((item, index) => {
    updateElementText(`[data-i18n="benefits.personalUse.item${index}"]`, item);
  });

  // Update developers items
  t.benefits.developers.items.forEach((item, index) => {
    updateElementText(`[data-i18n="benefits.developers.item${index}"]`, item);
  });

  updateElementText('[data-i18n="benefits.comparison.title"]', t.benefits.comparison.title);
  updateElementText('[data-i18n="benefits.comparison.traditional.title"]', t.benefits.comparison.traditional.title);
  updateElementText('[data-i18n="benefits.comparison.aiNotes.title"]', t.benefits.comparison.aiNotes.title);

  // Update traditional items
  t.benefits.comparison.traditional.items.forEach((item, index) => {
    updateElementText(`[data-i18n="benefits.comparison.traditional.item${index}"]`, item);
  });

  // Update AI Notes items
  t.benefits.comparison.aiNotes.items.forEach((item, index) => {
    updateElementText(`[data-i18n="benefits.comparison.aiNotes.item${index}"]`, item);
  });

  // Update CTA section
  updateElementText('[data-i18n="cta.title"]', t.cta.title);
  updateElementText('[data-i18n="cta.subtitle"]', t.cta.subtitle);
  updateElementText('[data-i18n="cta.primaryButton"]', t.cta.primaryButton);
  updateElementText('[data-i18n="cta.secondaryButton"]', t.cta.secondaryButton);
  updateElementText('[data-i18n="cta.openSource"]', t.cta.openSource);
  updateElementText('[data-i18n="cta.selfHostReady"]', t.cta.selfHostReady);
  updateElementText('[data-i18n="cta.license"]', t.cta.license);

  // Update footer
  updateElementText('[data-i18n="footer.description"]', t.footer.description);
  updateElementText('[data-i18n="footer.product.title"]', t.footer.product.title);
  updateElementText('[data-i18n="footer.product.features"]', t.footer.product.features);
  updateElementText('[data-i18n="footer.product.selfHosting"]', t.footer.product.selfHosting);
  updateElementText('[data-i18n="footer.product.documentation"]', t.footer.product.documentation);
  updateElementText('[data-i18n="footer.resources.title"]', t.footer.resources.title);
  updateElementText('[data-i18n="footer.resources.github"]', t.footer.resources.github);
  updateElementText('[data-i18n="footer.resources.contributing"]', t.footer.resources.contributing);
  updateElementText('[data-i18n="footer.resources.community"]', t.footer.resources.community);
  updateElementText('[data-i18n="footer.resources.license"]', t.footer.resources.license);
  updateElementText('[data-i18n="footer.copyright"]', t.footer.copyright);
}

function updateElementText(selector: string, text: string) {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = text;
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  const lang = getCurrentLanguage();
  document.documentElement.lang = lang;
  updatePageContent(lang);

  // Listen for language changes
  window.addEventListener('languageChange', ((event: CustomEvent<Language>) => {
    updatePageContent(event.detail);
  }) as EventListener);
});

export { getCurrentLanguage, updatePageContent };
