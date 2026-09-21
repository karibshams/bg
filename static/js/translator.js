/**
 * BhromonGhuri Pure Bilingual Translator (English <-> বাংলা)
 * Direct on-page translation without page reload.
 * Language state persists across navigation via localStorage & cookies.
 * STRICT RULE:
 * - In Bengali mode: 100% Bengali, NO English words.
 * - In English mode: 100% English, NO Bengali words.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'bhromon_selected_lang';
  const COOKIE_NAME = 'googtrans';

  // Comprehensive bilingual dictionary for instant on-page UI translation
  // Every 'bn' value is strictly Bengali. Every 'en' value is strictly English.
  const translations = {
    // Navigation
    'হোম': { en: 'Home', bn: 'হোম' },
    'ট্যুর প্যাকেজ': { en: 'Tour Packages', bn: 'ট্যুর প্যাকেজ' },
    'ট্যুরস': { en: 'Tours', bn: 'ট্যুর প্যাকেজ' },
    'গন্তব্য': { en: 'Destinations', bn: 'গন্তব্য' },
    'দর্শনীয় স্থান': { en: 'Destinations', bn: 'দর্শনীয় স্থান' },
    'ভ্রমণ গল্প': { en: 'Travel Stories', bn: 'ভ্রমণ গল্প' },
    'ভ্রমণ কাহিনী': { en: 'Travel Stories', bn: 'ভ্রমণ কাহিনী' },
    'গল্প': { en: 'Stories', bn: 'গল্প' },
    'গ্যালারি': { en: 'Gallery', bn: 'গ্যালারি' },
    'ফটো গ্যালারি': { en: 'Photo Gallery', bn: 'ফটো গ্যালারি' },
    'আমাদের সম্পর্কে': { en: 'About Us', bn: 'আমাদের সম্পর্কে' },
    'আমাদের কথা': { en: 'About Us', bn: 'আমাদের কথা' },
    'যোগাযোগ': { en: 'Contact', bn: 'যোগাযোগ' },
    'যোগাযোগ করুন': { en: 'Contact Us', bn: 'যোগাযোগ করুন' },
    'বুকিং যাচাই': { en: 'Track Booking', bn: 'বুকিং যাচাই' },
    'বুকিং চেক': { en: 'Check Booking', bn: 'বুকিং যাচাই' },
    'বুকিং স্ট্যাটাস চেক': { en: 'Check Booking Status', bn: 'বুকিং স্ট্যাটাস চেক' },
    'ট্যুর বুক করুন': { en: 'Book a Tour', bn: 'ট্যুর বুক করুন' },
    'ট্যুর নির্বাচন করুন': { en: 'Select a Tour', bn: 'ট্যুর নির্বাচন করুন' },
    'অ্যাডমিন প্যানেল': { en: 'Admin Control Panel', bn: 'অ্যাডমিন প্যানেল' },
    'লগআউট': { en: 'Logout', bn: 'লগআউট' },
    'গুগল লগইন': { en: 'Google Sign In', bn: 'গুগল লগইন' },
    'গুগল দিয়ে প্রবেশ': { en: 'Continue with Google', bn: 'গুগল দিয়ে প্রবেশ' },
    'গল্প লিখুন': { en: 'Share Your Story', bn: 'গল্প লিখুন' },
    'আমার বুকিং': { en: 'My Bookings', bn: 'আমার বুকিং' },
    'সর্বস্বত্ব সংরক্ষিত।': { en: 'All rights reserved.', bn: 'সর্বস্বত্ব সংরক্ষিত।' },

    // Hero & Taglines
    'অভিযান • অভিজ্ঞতা • আবিষ্কার': { en: 'Explore • Experience • Discover', bn: 'অভিযান • অভিজ্ঞতা • আবিষ্কার' },
    'অদেখা বাংলাকে নতুন চোখে দেখা': { en: 'Explore Unseen Bangladesh With Fresh Eyes', bn: 'অদেখা বাংলাকে নতুন চোখে দেখা' },
    'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি': { en: 'New places, new stories, new emotions', bn: 'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি' },
    'ট্যুর প্যাকেজগুলো দেখুন': { en: 'Explore Tour Packages', bn: 'ট্যুর প্যাকেজগুলো দেখুন' },
    'ভ্রমণ গল্প পড়ুন': { en: 'Read Travel Stories', bn: 'ভ্রমণ গল্প পড়ুন' },
    'খুঁজুন': { en: 'Search', bn: 'খুঁজুন' },
    'অনুসন্ধান': { en: 'Search', bn: 'অনুসন্ধান' },
    'নিচে দেখুন': { en: 'Scroll Down', bn: 'নিচে দেখুন' },
    'ভ্রমণকারীদের রেটিং': { en: 'Traveler Rating', bn: 'ভ্রমণকারীদের রেটিং' },
    '১০০% নিরাপদ ভ্রমণ': { en: '100% Safe Travel', bn: '১০০% নিরাপদ ভ্রমণ' },

    // Trust stats
    'সফল ট্যুর প্যাকেজ': { en: 'Successful Tour Packages', bn: 'সফল ট্যুর প্যাকেজ' },
    'সন্তুষ্ট ভ্রমণকারী': { en: 'Satisfied Travelers', bn: 'সন্তুষ্ট ভ্রমণকারী' },
    'গড় রেটিং রিভিউ': { en: 'Average Review Rating', bn: 'গড় রেটিং রিভিউ' },
    'রোমাঞ্চকর গন্তব্য': { en: 'Thrilling Destinations', bn: 'রোমাঞ্চকর গন্তব্য' },

    // Section Titles
    'আমাদের অসাধারণ ট্যুরসমূহ': { en: 'Explore Our Journeys', bn: 'আমাদের অসাধারণ ট্যুরসমূহ' },
    'আমাদের সেরা ট্যুর প্যাকেজসমূহ': { en: 'Our Best Tour Packages', bn: 'আমাদের সেরা ট্যুর প্যাকেজসমূহ' },
    'সবগুলো ট্যুর দেখুন': { en: 'View All Tours', bn: 'সবগুলো ট্যুর দেখুন' },
    'আপনার পছন্দের গন্তব্য': { en: 'Where Do You Want To Go?', bn: 'আপনার পছন্দের গন্তব্য' },
    'জনপ্রিয় দর্শনীয় স্থান ও গন্তব্য': { en: 'Popular Attractions & Destinations', bn: 'জনপ্রিয় দর্শনীয় স্থান ও গন্তব্য' },
    'আসন্ন যাত্রাসমূহ': { en: 'Upcoming Journeys', bn: 'আসন্ন যাত্রাসমূহ' },
    'আসন্ন যাত্রার সূচি ও আসন সংখ্যা': { en: 'Upcoming Journey Schedule & Seats', bn: 'আসন্ন যাত্রার সূচি ও আসন সংখ্যা' },
    'সব তারিখ দেখুন →': { en: 'View All Dates →', bn: 'সব তারিখ দেখুন →' },
    'ভ্রমণ কাহিনী ও বাস্তব অভিজ্ঞতা': { en: 'Authentic Travel Logs', bn: 'ভ্রমণ কাহিনী ও বাস্তব অভিজ্ঞতা' },
    'ভ্রমণের গল্প ও বাস্তব অভিজ্ঞতা': { en: 'Travel Stories & Genuine Experiences', bn: 'ভ্রমণের গল্প ও বাস্তব অভিজ্ঞতা' },
    'সব গল্প পড়ুন →': { en: 'Read All Stories →', bn: 'সব গল্প পড়ুন →' },
    'ছবি ও ভিডিও গ্যালারি': { en: 'Photo & Video Gallery', bn: 'ছবি ও ভিডিও গ্যালারি' },
    'স্মৃতির ফ্রেমে বাঁধা বাংলাদেশের সৌন্দর্য': { en: 'Memories of Beautiful Bangladesh', bn: 'স্মৃতির ফ্রেমে বাঁধা বাংলাদেশের সৌন্দর্য' },
    'পুরো গ্যালারি এক্সপ্লোর করুন': { en: 'Explore Full Gallery', bn: 'পুরো গ্যালারি এক্সপ্লোর করুন' },
    'ভ্রমণকারীদের মন্তব্য': { en: 'Traveler Testimonials', bn: 'ভ্রমণকারীদের মন্তব্য' },
    'ভ্রমণকারীদের ভালোলাগার কথা': { en: 'Words of Joy from Travelers', bn: 'ভ্রমণকারীদের ভালোলাগার কথা' },

    // Card details & actions
    'জনপ্রতি প্যাকেজ মূল্য': { en: 'Price per person', bn: 'জনপ্রতি প্যাকেজ মূল্য' },
    'বিস্তারিত': { en: 'View Details', bn: 'বিস্তারিত' },
    'বিস্তারিত দেখুন': { en: 'View Details', bn: 'বিস্তারিত দেখুন' },
    'বুকিং করুন': { en: 'Book Now', bn: 'বুকিং করুন' },
    'বুক করুন': { en: 'Book Now', bn: 'বুক করুন' },
    'দিন': { en: 'Days', bn: 'দিন' },
    'রাত': { en: 'Nights', bn: 'রাত' },
    'জন': { en: 'persons', bn: 'জন' },
    'টি বাকি': { en: 'seats left', bn: 'টি বাকি' },
    'আসন বাকি': { en: 'seats left', bn: 'আসন বাকি' },
    'ট্যুরগুলো দেখুন': { en: 'View Tours', bn: 'ট্যুরগুলো দেখুন' },
    'প্যাকেজ দেখুন': { en: 'View Packages', bn: 'প্যাকেজ দেখুন' },
    'দ্রুত লিঙ্ক': { en: 'Quick Links', bn: 'দ্রুত লিঙ্ক' },
    'তথ্য ও সহায়তা': { en: 'Support & Information', bn: 'তথ্য ও সহায়তা' },
    'সচরাচর জিজ্ঞাসা': { en: 'Frequently Asked Questions', bn: 'সচরাচর জিজ্ঞাসা' },
    'পেমেন্ট মাধ্যম': { en: 'Payment Methods', bn: 'পেমেন্ট মাধ্যম' },

    // Payment & Verification Page
    'পেমেন্ট জমা সম্পন্ন • ভেরিফিকেশন চলছে': { en: 'Payment Submitted • Under Verification', bn: 'পেমেন্ট জমা সম্পন্ন • ভেরিফিকেশন চলছে' },
    'আপনার পেমেন্ট ভেরিফিকেশনের অধীনে রয়েছে': { en: 'Your Payment is Under Verification', bn: 'আপনার পেমেন্ট ভেরিফিকেশনের অধীনে রয়েছে' },
    'বুকিং রেফারেন্স নম্বর': { en: 'Booking Reference ID', bn: 'বুকিং রেফারেন্স নম্বর' },
    'ভেরিফিকেশন অপেক্ষমাণ': { en: 'Pending Verification', bn: 'ভেরিফিকেশন অপেক্ষমাণ' },
    'ট্যুর প্যাকেজ:': { en: 'Tour Package:', bn: 'ট্যুর প্যাকেজ:' },
    'ভ্রমণের তারিখ:': { en: 'Travel Date:', bn: 'ভ্রমণের তারিখ:' },
    'গ্রাহকের নাম:': { en: 'Customer Name:', bn: 'গ্রাহকের নাম:' },
    'যাত্রী সংখ্যা:': { en: 'Travelers:', bn: 'যাত্রী সংখ্যা:' },
    'পেমেন্ট মাধ্যম:': { en: 'Payment Method:', bn: 'পেমেন্ট মাধ্যম:' },
    'প্রেরক নম্বর:': { en: 'Sender Number:', bn: 'প্রেরক নম্বর:' },
    'লেনদেন নম্বর:': { en: 'Transaction ID:', bn: 'লেনদেন নম্বর:' },
    'পরিশোধিত টাকা:': { en: 'Paid Amount:', bn: 'পরিশোধিত টাকা:' },
    'পরবর্তী পদক্ষেপ': { en: 'What happens next?', bn: 'পরবর্তী পদক্ষেপ' },
    'বুকিং স্ট্যাটাস ট্র্যাক করুন': { en: 'Track Booking Status', bn: 'বুকিং স্ট্যাটাস ট্র্যাক করুন' },
    'হোম পেজে ফিরুন': { en: 'Return to Home', bn: 'হোম পেজে ফিরুন' },
    'ফ্লেক্সিবল': { en: 'Flexible', bn: 'ফ্লেক্সিবল' }
  };

  const originalTextNodes = new Map();

  function getStoredLanguage() {
    return localStorage.getItem(STORAGE_KEY) || 'bn';
  }

  function setCookie(name, value, days) {
    let expires = '';
    if (days) {
      const d = new Date();
      d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
      expires = '; expires=' + d.toUTCString();
    }
    document.cookie = name + '=' + (value || '') + expires + '; path=/';
  }

  function applyPureBilingualTranslation(targetLang) {
    // 1. First priority: Pure DOM element swaps with data-en & data-bn
    document.querySelectorAll('[data-en][data-bn]').forEach((el) => {
      const targetText = targetLang === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-bn');
      if (targetText && el.textContent.trim() !== targetText.trim()) {
        el.textContent = targetText;
      }
    });

    // 2. Input Placeholders with data-en-placeholder & data-bn-placeholder
    document.querySelectorAll('[data-en-placeholder][data-bn-placeholder]').forEach((el) => {
      const targetPlaceholder = targetLang === 'en' ? el.getAttribute('data-en-placeholder') : el.getAttribute('data-bn-placeholder');
      if (targetPlaceholder) {
        el.setAttribute('placeholder', targetPlaceholder);
      }
    });

    // 3. Fallback dictionary replacement across all text nodes
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          const tag = parent.tagName.toLowerCase();
          if (tag === 'script' || tag === 'style' || tag === 'noscript' || tag === 'textarea') {
            return NodeFilter.FILTER_REJECT;
          }
          if (parent.closest('#language-dropdown-menu') || parent.closest('#language-mobile-menu')) {
            return NodeFilter.FILTER_REJECT;
          }
          if (parent.hasAttribute('data-en') && parent.hasAttribute('data-bn')) {
            return NodeFilter.FILTER_REJECT;
          }
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    const nodesToTranslate = [];
    while (walker.nextNode()) {
      nodesToTranslate.push(walker.currentNode);
    }

    nodesToTranslate.forEach((node) => {
      if (!originalTextNodes.has(node)) {
        originalTextNodes.set(node, node.nodeValue);
      }
      const rawText = originalTextNodes.get(node);
      const trimmed = rawText.trim();

      if (!trimmed) return;

      // Exact match check
      if (translations[trimmed] && translations[trimmed][targetLang]) {
        const replacement = translations[trimmed][targetLang];
        node.nodeValue = rawText.replace(trimmed, replacement);
        return;
      }

      // Reverse match check
      for (const [key, mapping] of Object.entries(translations)) {
        if (mapping.en === trimmed || mapping.bn === trimmed) {
          const replacement = mapping[targetLang] || (targetLang === 'en' ? mapping.en : mapping.bn);
          node.nodeValue = rawText.replace(trimmed, replacement);
          return;
        }
      }

      // Substring replace for multi-item phrases
      let updatedText = rawText;
      let modified = false;
      for (const [key, mapping] of Object.entries(translations)) {
        if (key.length > 5 && updatedText.includes(key) && targetLang === 'en') {
          updatedText = updatedText.replaceAll(key, mapping.en);
          modified = true;
        } else if (mapping.en.length > 5 && updatedText.includes(mapping.en) && targetLang === 'bn') {
          updatedText = updatedText.replaceAll(mapping.en, mapping.bn);
          modified = true;
        }
      }
      if (modified) {
        node.nodeValue = updatedText;
      }
    });

    // 4. Update input placeholders
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach((input) => {
      const ph = input.getAttribute('placeholder').trim();
      if (translations[ph] && translations[ph][targetLang]) {
        input.setAttribute('placeholder', translations[ph][targetLang]);
      }
    });
  }

  function updateNavbarUI(lang) {
    const currentCodeElements = document.querySelectorAll('.current-lang-code');
    const checkElements = document.querySelectorAll('.lang-check');

    currentCodeElements.forEach((el) => {
      el.textContent = lang === 'en' ? 'EN' : 'বাংলা';
    });

    checkElements.forEach((el) => {
      const itemLang = el.getAttribute('data-lang');
      if (itemLang === lang) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    });

    document.documentElement.lang = lang;
  }

  // Clear any lingering Google Translate cookies so Chrome never shows the translator banner
  function clearGoogleTranslateArtifacts() {
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + window.location.hostname + ';';
  }

  window.setSiteLanguage = function (targetLang) {
    if (targetLang !== 'en' && targetLang !== 'bn') return;

    localStorage.setItem(STORAGE_KEY, targetLang);
    updateNavbarUI(targetLang);

    // Apply instantaneous pure bilingual translation without external widgets
    applyPureBilingualTranslation(targetLang);
    clearGoogleTranslateArtifacts();

    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: targetLang } }));
  };

  document.addEventListener('DOMContentLoaded', () => {
    clearGoogleTranslateArtifacts();
    const preferredLang = getStoredLanguage();
    updateNavbarUI(preferredLang);
    applyPureBilingualTranslation(preferredLang);
  });

  document.body.addEventListener('htmx:afterSwap', () => {
    const currentLang = getStoredLanguage();
    applyPureBilingualTranslation(currentLang);
  });
})();
