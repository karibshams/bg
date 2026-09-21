/**
 * BhromonGhuri On-Page Language Translator (English <-> বাংলা)
 * Direct on-page translation without page reload or redirect.
 * Language state persists across navigation via localStorage & cookies.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'bhromon_selected_lang';
  const COOKIE_NAME = 'googtrans';

  // Comprehensive bilingual dictionary for instant on-page UI translation
  const translations = {
    // Nav & Common Headers
    'হোম (Home)': { en: 'Home', bn: 'হোম (Home)' },
    'হোম': { en: 'Home', bn: 'হোম' },
    'ট্যুরস (Tours)': { en: 'Tours', bn: 'ট্যুরস (Tours)' },
    'ট্যুর প্যাকেজ (All Tours)': { en: 'All Tour Packages', bn: 'ট্যুর প্যাকেজ (All Tours)' },
    'ট্যুর প্যাকেজ': { en: 'Tour Packages', bn: 'ট্যুর প্যাকেজ' },
    'ট্যুরস': { en: 'Tours', bn: 'ট্যুরস' },
    'গন্তব্য (Destinations)': { en: 'Destinations', bn: 'গন্তব্য (Destinations)' },
    'দর্শনীয় স্থান (Destinations)': { en: 'Destinations', bn: 'দর্শনীয় স্থান (Destinations)' },
    'দর্শনীয় স্থান': { en: 'Destinations', bn: 'দর্শনীয় স্থান' },
    'গন্তব্য': { en: 'Destinations', bn: 'গন্তব্য' },
    'গল্প (Stories)': { en: 'Stories', bn: 'গল্প (Stories)' },
    'ভ্রমণ কাহিনী (Travel Stories)': { en: 'Travel Stories', bn: 'ভ্রমণ কাহিনী (Travel Stories)' },
    'ভ্রমণ কাহিনী': { en: 'Travel Stories', bn: 'ভ্রমণ কাহিনী' },
    'ভ্রমণ গল্প ও টিপস': { en: 'Travel Stories & Tips', bn: 'ভ্রমণ গল্প ও টিপস' },
    'গল্প': { en: 'Stories', bn: 'গল্প' },
    'গ্যালারি (Gallery)': { en: 'Gallery', bn: 'গ্যালারি (Gallery)' },
    'ফটো গ্যালারি (Gallery)': { en: 'Photo Gallery', bn: 'ফটো গ্যালারি (Gallery)' },
    'ফটো গ্যালারি': { en: 'Photo Gallery', bn: 'ফটো গ্যালারি' },
    'গ্যালারি': { en: 'Gallery', bn: 'গ্যালারি' },
    'আমাদের কথা (About)': { en: 'About Us', bn: 'আমাদের কথা (About)' },
    'আমাদের কথা (About Us)': { en: 'About Us', bn: 'আমাদের কথা (About Us)' },
    'আমাদের সম্পর্কে': { en: 'About Us', bn: 'আমাদের সম্পর্কে' },
    'আমাদের কথা': { en: 'About Us', bn: 'আমাদের কথা' },
    'যোগাযোগ (Contact)': { en: 'Contact', bn: 'যোগাযোগ (Contact)' },
    'যোগাযোগ': { en: 'Contact', bn: 'যোগাযোগ' },
    'যোগাযোগ করুন': { en: 'Contact Us', bn: 'যোগাযোগ করুন' },
    'বুকিং চেক': { en: 'Check Booking', bn: 'বুকিং চেক' },
    'বুকিং স্ট্যাটাস চেক': { en: 'Check Booking Status', bn: 'বুকিং স্ট্যাটাস চেক' },
    'বুকিং স্ট্যাটাস চেক (Check Booking)': { en: 'Check Booking Status', bn: 'বুকিং স্ট্যাটাস চেক (Check Booking)' },
    'ট্যুর বুক করুন': { en: 'Book a Tour', bn: 'ট্যুর বুক করুন' },
    'ট্যুর নির্বাচন করুন': { en: 'Select a Tour', bn: 'ট্যুর নির্বাচন করুন' },
    'অ্যাডমিন প্যানেল': { en: 'Admin Panel', bn: 'অ্যাডমিন প্যানেল' },
    'সর্বস্বত্ব সংরক্ষিত।': { en: 'All rights reserved.', bn: 'সর্বস্বত্ব সংরক্ষিত।' },

    // Hero & Taglines
    'অদেখা বাংলাকে নতুন চোখে দেখা': { en: 'Looking at the unseen Bengal with a new eye', bn: 'অদেখা বাংলাকে নতুন চোখে দেখা' },
    'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি': { en: 'New places, new stories, new emotions', bn: 'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি' },
    'ভ্রমণঘুড়ির সাথে আবিষ্কার করুন বাংলাদেশ ও বিদেশের অনন্য সব দর্শনীয় স্থান। নিরাপদ ও আধুনিক ভ্রমণ অভিজ্ঞতা।': {
      en: 'Discover unique destinations in Bangladesh and beyond with BhromonGhuri. Safe, modern, and exciting travel.',
      bn: 'ভ্রমণঘুড়ির সাথে আবিষ্কার করুন বাংলাদেশ ও বিদেশের অনন্য সব দর্শনীয় স্থান। নিরাপদ ও আধুনিক ভ্রমণ অভিজ্ঞতা।'
    },
    'ভ্রমণঘুড়ির সাথে আবিষ্কার করুন পাহাড়, সমুদ্র, মেঘের দেশ আর সবুজ বনানীর অপূর্ব সৌন্দর্য। প্রতিটি পদক্ষেপে নিরাপদ ও রোমাঞ্চকর ভ্রমণ।': {
      en: 'Discover mountains, seas, clouds, and lush green forests with BhromonGhuri. Safe and thrilling travel every step of the way.',
      bn: 'ভ্রমণঘুড়ির সাথে আবিষ্কার করুন পাহাড়, সমুদ্র, মেঘের দেশ আর সবুজ বনানীর অপূর্ব সৌন্দর্য। প্রতিটি পদক্ষেপে নিরাপদ ও রোমাঞ্চকর ভ্রমণ।'
    },
    'প্যাকেজসমূহ দেখুন': { en: 'Check out packages', bn: 'প্যাকেজসমূহ দেখুন' },
    'প্যাকেজ দেখুন': { en: 'View Packages', bn: 'প্যাকেজ দেখুন' },
    'ভ্রমণ গল্প পড়ুন': { en: 'Read Travel Stories', bn: 'ভ্রমণ গল্প পড়ুন' },
    'কখন কোথায় ভ্রমণ করতে চান?': { en: 'When and where do you want to travel?', bn: 'কখন কোথায় ভ্রমণ করতে চান?' },
    'অনুসন্ধান করুন': { en: 'Search', bn: 'অনুসন্ধান করুন' },
    'অনুসন্ধান': { en: 'Search', bn: 'অনুসন্ধান' },
    'সকল ট্যুর প্যাকেজ': { en: 'All Tour Packages', bn: 'সকল ট্যুর প্যাকেজ' },
    'জনপ্রিয় গন্তব্যসমূহ': { en: 'Popular Destinations', bn: 'জনপ্রিয় গন্তব্যসমূহ' },
    'দ্রুত লিঙ্ক': { en: 'Quick Links', bn: 'দ্রুত লিঙ্ক' },
    'তথ্য ও সহায়তা': { en: 'Information & Support', bn: 'তথ্য ও সহায়তা' },
    'সচরাচর জিজ্ঞাসা (FAQ)': { en: 'Frequently Asked Questions (FAQ)', bn: 'সচরাচর জিজ্ঞাসা (FAQ)' },
    'নিরাপদ ভ্রমণ • আধুনিক অভিজ্ঞতা • দায়িত্বশীল পর্যটন': {
      en: 'Safe Travel • Modern Experience • Responsible Tourism',
      bn: 'নিরাপদ ভ্রমণ • আধুনিক অভিজ্ঞতা • দায়িত্বশীল পর্যটন'
    },

    // Card details & filters
    'বুকিং করুন': { en: 'Book Now', bn: 'বুকিং করুন' },
    'বিস্তারিত দেখুন': { en: 'View Details', bn: 'বিস্তারিত দেখুন' },
    'দিন': { en: 'Days', bn: 'দিন' },
    'রাত': { en: 'Nights', bn: 'রাত' },
    'জনপ্রতি': { en: 'per person', bn: 'জনপ্রতি' },
    'আসন বাকি': { en: 'seats left', bn: 'আসন বাকি' },
    'সর্বোচ্চ আসন': { en: 'Total Seats', bn: 'সর্বোচ্চ আসন' },
    'যাত্রা শুরু': { en: 'Departure', bn: 'যাত্রা শুরু' },
    'সকল ক্যাটাগরি': { en: 'All Categories', bn: 'সকল ক্যাটাগরি' },
    'পাহাড় ও ক্লাউড': { en: 'Mountains & Clouds', bn: 'পাহাড় ও ক্লাউড' },
    'সমুদ্র ও দ্বীপ': { en: 'Sea & Islands', bn: 'সমুদ্র ও দ্বীপ' },
    'হাওর ও জলরাশি': { en: 'Haor & Wetlands', bn: 'হাওর ও জলরাশি' },
    'ঐতিহ্য ও প্রত্নতত্ত্ব': { en: 'Heritage & Archaeology', bn: 'ঐতিহ্য ও প্রত্নতত্ত্ব' },
    'জঙ্গল ও বন্যপ্রাণী': { en: 'Forest & Wildlife', bn: 'জঙ্গল ও বন্যপ্রাণী' },

    // Story & details
    'ভ্রমণ গল্প ও বাস্তব অভিজ্ঞতা': { en: 'Travel Stories and Real Experiences', bn: 'ভ্রমণ গল্প ও বাস্তব অভিজ্ঞতা' },
    'পুরো গল্প পড়ুন': { en: 'Read full story', bn: 'পুরো গল্প পড়ুন' },
    'আপনার গল্প শেয়ার করুন': { en: 'Share Your Story', bn: 'আপনার গল্প শেয়ার করুন' },
    'গল্প শেয়ার করুন': { en: 'Share Story', bn: 'গল্প শেয়ার করুন' },

    // Tour detail & booking
    'ট্যুর পরিচিতি ও হাইলাইটস': { en: 'Tour Overview & Highlights', bn: 'ট্যুর পরিচিতি ও হাইলাইটস' },
    'আগামী যাত্রার তারিখ': { en: 'Upcoming Departure Dates', bn: 'আগামী যাত্রার তারিখ' },
    'দিনভিত্তিক ভ্রমণ পরিকল্পনা': { en: 'Day-by-Day Itinerary', bn: 'দিনভিত্তিক ভ্রমণ পরিকল্পনা' },
    'প্যাকেজে যা যা অন্তর্ভুক্ত': { en: 'What is included in the package', bn: 'প্যাকেজে যা যা অন্তর্ভুক্ত' },
    'প্যাকেজে যা অন্তর্ভুক্ত নয়': { en: 'What is not included (excluded)', bn: 'প্যাকেজে যা অন্তর্ভুক্ত নয়' },
    'বুকিং সারাংশ': { en: 'Booking Summary', bn: 'বুকিং সারাংশ' },
    'ভ্রমণকারী সংখ্যা': { en: 'Number of Travelers', bn: 'ভ্রমণকারী সংখ্যা' },
    'গ্রাহকের তথ্য': { en: 'Customer Details', bn: 'গ্রাহকের তথ্য' },
    'সম্পূর্ণ নাম': { en: 'Full Name', bn: 'সম্পূর্ণ নাম' },
    'ইমেইল ঠিকানা': { en: 'Email Address', bn: 'ইমেইল ঠিকানা' },
    'মোবাইল নম্বর': { en: 'Mobile Number', bn: 'মোবাইল নম্বর' },
    'পেমেন্টে এগিয়ে যান': { en: 'Proceed to Payment', bn: 'পেমেন্টে এগিয়ে যান' },
    'পেমেন্ট পদ্ধতি নির্বাচন করুন': { en: 'Select Payment Method', bn: 'পেমেন্ট পদ্ধতি নির্বাচন করুন' },
    'পেমেন্ট সম্পন্ন করুন': { en: 'Complete Payment', bn: 'পেমেন্ট সম্পন্ন করুন' },
    'যেকোনো বিশেষ নির্দেশনা (যদি থাকে)': { en: 'Special instructions (if any)', bn: 'যেকোনো বিশেষ নির্দেশনা (যদি থাকে)' },
    'বুকিং রেফারেন্স আইডি': { en: 'Booking Reference ID', bn: 'বুকিং রেফারেন্স আইডি' },
    'ট্রানজেকশন আইডি (TrxID)': { en: 'Transaction ID (TrxID)', bn: 'ট্রানজেকশন আইডি (TrxID)' },
    'ট্যুর ও ব্যাচ': { en: 'Tour & Batch', bn: 'ট্যুর ও ব্যাচ' },
    'পেমেন্ট স্ট্যাটাস': { en: 'Payment Status', bn: 'পেমেন্ট স্ট্যাটাস' },
    'কনফার্মেশন ভাউচার ডাউনলোড': { en: 'Download Confirmation Voucher', bn: 'কনফার্মেশন ভাউচার ডাউনলোড' }
  };

  // Cache original text for text nodes to allow seamless round-trip switching
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

  function applyDictionaryTranslation(targetLang) {
    // Walk through all text-containing elements
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

      // Check reverse match (if page text was already in English or vice-versa)
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

    // Also update input placeholders
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach((input) => {
      const ph = input.getAttribute('placeholder').trim();
      if (translations[ph] && translations[ph][targetLang]) {
        input.setAttribute('placeholder', translations[ph][targetLang]);
      }
    });
  }

  // Google Translate bridge for arbitrary dynamic text paragraphs
  function triggerGoogleTranslate(lang) {
    try {
      // Set the standard Google Translate cookie
      const cookieVal = lang === 'en' ? '/auto/en' : '/auto/bn';
      setCookie(COOKIE_NAME, cookieVal, 30);

      const select = document.querySelector('.goog-te-combo');
      if (select) {
        select.value = lang;
        select.dispatchEvent(new Event('change'));
      }
    } catch (e) {
      console.warn('Google translate bridge note:', e);
    }
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

    // Update html lang attribute
    document.documentElement.lang = lang;
  }

  window.setSiteLanguage = function (targetLang) {
    if (targetLang !== 'en' && targetLang !== 'bn') return;

    localStorage.setItem(STORAGE_KEY, targetLang);
    updateNavbarUI(targetLang);

    // Apply fast dictionary-based DOM translation immediately
    applyDictionaryTranslation(targetLang);

    // Also trigger Google Translate for any dynamic text blocks
    triggerGoogleTranslate(targetLang);

    // Dispatch event for other components if needed
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: targetLang } }));
  };

  // Initialize on page load
  document.addEventListener('DOMContentLoaded', () => {
    const preferredLang = getStoredLanguage();
    updateNavbarUI(preferredLang);
    if (preferredLang === 'en') {
      // Apply translation right after DOM is ready
      applyDictionaryTranslation('en');
      setTimeout(() => {
        triggerGoogleTranslate('en');
      }, 500);
    }
  });

  // Also hook into HTMX content swaps
  document.body.addEventListener('htmx:afterSwap', () => {
    const currentLang = getStoredLanguage();
    if (currentLang === 'en') {
      applyDictionaryTranslation('en');
    }
  });
})();
