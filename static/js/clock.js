/**
 * BhromonGhuri Real-Time Live Clock & Date Display Engine
 * Updates every second with live time (12-hour AM/PM with seconds) and date.
 * Fully bilingual (English <-> বাংলা) with Bangla numeral conversion.
 */

(function () {
  'use strict';

  const BENGALI_DIGITS = {
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
  };

  const EN_DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const BN_DAYS = ['রবিবার', 'সোমবার', 'মঙ্গলবার', 'বুধবার', 'বৃহস্পতিবার', 'শুক্রবার', 'শনিবার'];

  const EN_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const BN_MONTHS = ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'];

  function toBanglaDigits(str) {
    return String(str).replace(/[0-9]/g, (d) => BENGALI_DIGITS[d] || d);
  }

  function getLanguage() {
    return localStorage.getItem('bhromon_selected_lang') || 'en';
  }

  function updateLiveClock() {
    const now = new Date();
    const lang = getLanguage();

    let hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    const isPM = hours >= 12;
    hours = hours % 12;
    hours = hours ? hours : 12; // 0 hour is 12 AM

    const padZero = (n) => (n < 10 ? '0' + n : String(n));
    const hStr = padZero(hours);
    const mStr = padZero(minutes);
    const sStr = padZero(seconds);

    const dayIdx = now.getDay();
    const monthIdx = now.getMonth();
    const dateNum = now.getDate();
    const year = now.getFullYear();

    let timeText = '';
    let dateText = '';
    let badgeText = '';

    if (lang === 'bn') {
      timeText = `${toBanglaDigits(hStr)}:${toBanglaDigits(mStr)}:${toBanglaDigits(sStr)} ${toBanglaDigits(isPM ? 'অপরাহ্ন' : 'পূর্বাহ্ন')}`;
      dateText = `${BN_DAYS[dayIdx]}, ${toBanglaDigits(dateNum)} ${BN_MONTHS[monthIdx]} ${toBanglaDigits(year)}`;
      badgeText = 'বিএসটি (BST)';
    } else {
      const enAmPm = isPM ? 'PM' : 'AM';
      timeText = `${hStr}:${mStr}:${sStr} ${enAmPm}`;
      dateText = `${EN_DAYS[dayIdx].slice(0, 3)}, ${dateNum} ${EN_MONTHS[monthIdx]} ${year}`;
      badgeText = 'BST';
    }

    // Update all clock elements across the DOM
    document.querySelectorAll('.live-time-display').forEach((el) => {
      el.textContent = timeText;
    });

    document.querySelectorAll('.live-date-display').forEach((el) => {
      el.textContent = dateText;
    });

    document.querySelectorAll('.live-timezone-badge').forEach((el) => {
      el.textContent = badgeText;
    });
  }

  // Run on page load and tick every 1000ms
  document.addEventListener('DOMContentLoaded', () => {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
  });

  // Re-render immediately on bilingual toggle
  window.addEventListener('languageChanged', () => {
    updateLiveClock();
  });

  // Also support HTMX content swap
  if (document.body) {
    document.body.addEventListener('htmx:afterSwap', () => {
      updateLiveClock();
    });
  }
})();
