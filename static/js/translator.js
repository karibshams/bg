/**
 * BhromonGhuri Pure Bilingual Translator (English <-> বাংলা)
 * Direct on-page translation without page reload.
 * Language state persists across navigation via localStorage & cookies.
 * Default language: English ('en').
 * STRICT RULES:
 * - Brand logo ("ভ্রমণঘুড়ি") remains unchanged in Bengali brand identity.
 * - In English mode: 100% English.
 * - In Bengali mode: 100% Bengali.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'bhromon_selected_lang';
  const COOKIE_NAME = 'googtrans';

  // Comprehensive bilingual dictionary for instant on-page UI translation
  const translations = {
    // Navigation & General
    'Home': { en: 'Home', bn: 'হোম' },
    'হোম': { en: 'Home', bn: 'হোম' },
    'Tour Packages': { en: 'Tour Packages', bn: 'ট্যুর প্যাকেজ' },
    'ট্যুর প্যাকেজ': { en: 'Tour Packages', bn: 'ট্যুর প্যাকেজ' },
    'Tours': { en: 'Tours', bn: 'ট্যুরস' },
    'ট্যুরস': { en: 'Tours', bn: 'ট্যুরস' },
    'Destinations': { en: 'Destinations', bn: 'গন্তব্য' },
    'গন্তব্য': { en: 'Destinations', bn: 'গন্তব্য' },
    'Popular Destinations': { en: 'Popular Destinations', bn: 'জনপ্রিয় গন্তব্যসমূহ' },
    'জনপ্রিয় গন্তব্যসমূহ': { en: 'Popular Destinations', bn: 'জনপ্রিয় গন্তব্যসমূহ' },
    'Travel Stories': { en: 'Travel Stories', bn: 'ভ্রমণ গল্প' },
    'ভ্রমণ গল্প': { en: 'Travel Stories', bn: 'ভ্রমণ গল্প' },
    'Stories': { en: 'Stories', bn: 'গল্প' },
    'গল্প': { en: 'Stories', bn: 'গল্প' },
    'Gallery': { en: 'Gallery', bn: 'গ্যালারি' },
    'গ্যালারি': { en: 'Gallery', bn: 'গ্যালারি' },
    'Photo Gallery': { en: 'Photo Gallery', bn: 'ফটো গ্যালারি' },
    'ফটো গ্যালারি': { en: 'Photo Gallery', bn: 'ফটো গ্যালারি' },
    'About Us': { en: 'About Us', bn: 'আমাদের সম্পর্কে' },
    'আমাদের সম্পর্কে': { en: 'About Us', bn: 'আমাদের সম্পর্কে' },
    'Contact': { en: 'Contact', bn: 'যোগাযোগ' },
    'যোগাযোগ': { en: 'Contact', bn: 'যোগাযোগ' },
    'Contact Us': { en: 'Contact Us', bn: 'যোগাযোগ করুন' },
    'যোগাযোগ করুন': { en: 'Contact Us', bn: 'যোগাযোগ করুন' },
    'Track Booking': { en: 'Track Booking', bn: 'বুকিং যাচাই' },
    'বুকিং যাচাই': { en: 'Track Booking', bn: 'বুকিং যাচাই' },
    'Check Booking Status': { en: 'Check Booking Status', bn: 'বুকিং স্ট্যাটাস চেক' },
    'বুকিং স্ট্যাটাস চেক': { en: 'Check Booking Status', bn: 'বুকিং স্ট্যাটাস চেক' },
    'Book a Tour': { en: 'Book a Tour', bn: 'ট্যুর বুক করুন' },
    'ট্যুর বুক করুন': { en: 'Book a Tour', bn: 'ট্যুর বুক করুন' },
    'Select a Tour': { en: 'Select a Tour', bn: 'ট্যুর নির্বাচন করুন' },
    'ট্যুর নির্বাচন করুন': { en: 'Select a Tour', bn: 'ট্যুর নির্বাচন করুন' },
    'Admin Control Panel': { en: 'Admin Control Panel', bn: 'অ্যাডমিন প্যানেল' },
    'অ্যাডমিন প্যানেল': { en: 'Admin Control Panel', bn: 'অ্যাডমিন প্যানেল' },
    'Logout': { en: 'Logout', bn: 'লগআউট' },
    'লগআউট': { en: 'Logout', bn: 'লগআউট' },
    'Google Sign In': { en: 'Google Sign In', bn: 'গুগল লগইন' },
    'গুগল লগইন': { en: 'Google Sign In', bn: 'গুগল লগইন' },
    'Sign in with Google': { en: 'Sign in with Google', bn: 'গুগল দিয়ে সাইন ইন' },
    'গুগল দিয়ে সাইন ইন': { en: 'Sign in with Google', bn: 'গুগল দিয়ে সাইন ইন' },
    'Share Your Story': { en: 'Share Your Story', bn: 'গল্প লিখুন' },
    'গল্প লিখুন': { en: 'Share Your Story', bn: 'গল্প লিখুন' },
    'My Bookings': { en: 'My Bookings', bn: 'আমার বুকিং' },
    'আমার বুকিং': { en: 'My Bookings', bn: 'আমার বুকিং' },
    'Language:': { en: 'Language:', bn: 'ভাষা:' },
    'ভাষা:': { en: 'Language:', bn: 'ভাষা:' },

    // Hero & Taglines
    'EXPLORE • EXPERIENCE • DISCOVER': { en: 'EXPLORE • EXPERIENCE • DISCOVER', bn: 'অভিযান • অভিজ্ঞতা • আবিষ্কার' },
    'অভিযান • অভিজ্ঞতা • আবিষ্কার': { en: 'EXPLORE • EXPERIENCE • DISCOVER', bn: 'অভিযান • অভিজ্ঞতা • আবিষ্কার' },
    'Explore Unseen Bangladesh With Fresh Eyes': { en: 'Explore Unseen Bangladesh With Fresh Eyes', bn: 'অদেখা বাংলাকে নতুন চোখে দেখা' },
    'অদেখা বাংলাকে নতুন চোখে দেখা': { en: 'Explore Unseen Bangladesh With Fresh Eyes', bn: 'অদেখা বাংলাকে নতুন চোখে দেখা' },
    'New places, new stories, new emotions': { en: 'New places, new stories, new emotions', bn: 'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি' },
    'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি': { en: 'New places, new stories, new emotions', bn: 'নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি' },
    'Explore Tour Packages': { en: 'Explore Tour Packages', bn: 'ট্যুর প্যাকেজগুলো দেখুন' },
    'ট্যুর প্যাকেজগুলো দেখুন': { en: 'Explore Tour Packages', bn: 'ট্যুর প্যাকেজগুলো দেখুন' },
    'Read Travel Stories': { en: 'Read Travel Stories', bn: 'ভ্রমণ গল্প পড়ুন' },
    'ভ্রমণ গল্প পড়ুন': { en: 'Read Travel Stories', bn: 'ভ্রমণ গল্প পড়ুন' },
    'Search': { en: 'Search', bn: 'খুঁজুন' },
    'খুঁজুন': { en: 'Search', bn: 'খুঁজুন' },
    'SCROLL': { en: 'SCROLL', bn: 'নিচে দেখুন' },
    'নিচে দেখুন': { en: 'SCROLL', bn: 'নিচে দেখুন' },
    'Traveler Rating': { en: 'Traveler Rating', bn: 'ভ্রমণকারীদের রেটিং' },
    'ভ্রমণকারীদের রেটিং': { en: 'Traveler Rating', bn: 'ভ্রমণকারীদের রেটিং' },
    '100% Verified & Safe': { en: '100% Verified & Safe', bn: '১০০% নিরাপদ ভ্রমণ' },
    '১০০% নিরাপদ ভ্রমণ': { en: '100% Verified & Safe', bn: '১০০% নিরাপদ ভ্রমণ' },
    'Official Tourism Partner': { en: 'Official Tourism Partner', bn: 'অফিসিয়াল ট্যুরিজম পার্টনার' },
    'অফিসিয়াল ট্যুরিজম পার্টনার': { en: 'Official Tourism Partner', bn: 'অফিসিয়াল ট্যুরিজম পার্টনার' },
    'FEATURED DESTINATION': { en: 'FEATURED DESTINATION', bn: 'জনপ্রিয় গন্তব্য' },
    'জনপ্রিয় গন্তব্য': { en: 'FEATURED DESTINATION', bn: 'জনপ্রিয় গন্তব্য' },
    'Sajek Valley — Kingdom of Clouds': { en: 'Sajek Valley — Kingdom of Clouds', bn: 'সাজেক ভ্যালি — মেঘের রাজ্য' },
    'সাজেক ভ্যালি — মেঘের রাজ্য': { en: 'Sajek Valley — Kingdom of Clouds', bn: 'সাজেক ভ্যালি — মেঘের রাজ্য' },

    // Trust Stats
    'Successful Tour Packages': { en: 'Successful Tour Packages', bn: 'সফল ট্যুর প্যাকেজ' },
    'সফল ট্যুর প্যাকেজ': { en: 'Successful Tour Packages', bn: 'সফল ট্যুর প্যাকেজ' },
    'Satisfied Travelers': { en: 'Satisfied Travelers', bn: 'সন্তুষ্ট ভ্রমণকারী' },
    'সন্তুষ্ট ভ্রমণকারী': { en: 'Satisfied Travelers', bn: 'সন্তুষ্ট ভ্রমণকারী' },
    'Average Review Rating': { en: 'Average Review Rating', bn: 'গড় রেটিং রিভিউ' },
    'গড় রেটিং রিভিউ': { en: 'Average Review Rating', bn: 'গড় রেটিং রিভিউ' },
    'Thrilling Destinations': { en: 'Thrilling Destinations', bn: 'রোমাঞ্চকর গন্তব্য' },
    'রোমাঞ্চকর গন্তব্য': { en: 'Thrilling Destinations', bn: 'রোমাঞ্চকর গন্তব্য' },

    // Section Titles
    'EXPLORE OUR JOURNEYS': { en: 'EXPLORE OUR JOURNEYS', bn: 'আমাদের অসাধারণ ট্যুরসমূহ' },
    'আমাদের অসাধারণ ট্যুরসমূহ': { en: 'EXPLORE OUR JOURNEYS', bn: 'আমাদের অসাধারণ ট্যুরসমূহ' },
    'Our Best Tour Packages': { en: 'Our Best Tour Packages', bn: 'আমাদের সেরা ট্যুর প্যাকেজসমূহ' },
    'আমাদের সেরা ট্যুর প্যাকেজসমূহ': { en: 'Our Best Tour Packages', bn: 'আমাদের সেরা ট্যুর প্যাকেজসমূহ' },
    'View All Tours': { en: 'View All Tours', bn: 'সবগুলো ট্যুর দেখুন' },
    'সবগুলো ট্যুর দেখুন': { en: 'View All Tours', bn: 'সবগুলো ট্যুর দেখুন' },
    'WHERE DO YOU WANT TO GO?': { en: 'WHERE DO YOU WANT TO GO?', bn: 'আপনার পছন্দের গন্তব্য' },
    'আপনার পছন্দের গন্তব্য': { en: 'WHERE DO YOU WANT TO GO?', bn: 'আপনার পছন্দের গন্তব্য' },
    'Popular Attractions & Destinations': { en: 'Popular Attractions & Destinations', bn: 'জনপ্রিয় দর্শনীয় স্থান ও গন্তব্য' },
    'জনপ্রিয় দর্শনীয় স্থান ও গন্তব্য': { en: 'Popular Attractions & Destinations', bn: 'জনপ্রিয় দর্শনীয় স্থান ও গন্তব্য' },
    'UPCOMING JOURNEYS': { en: 'UPCOMING JOURNEYS', bn: 'আসন্ন যাত্রাসমূহ' },
    'আসন্ন যাত্রাসমূহ': { en: 'UPCOMING JOURNEYS', bn: 'আসন্ন যাত্রাসমূহ' },
    'Upcoming Journey Schedule & Seats': { en: 'Upcoming Journey Schedule & Seats', bn: 'আসন্ন যাত্রার সূচি ও আসন সংখ্যা' },
    'আসন্ন যাত্রার সূচি ও আসন সংখ্যা': { en: 'Upcoming Journey Schedule & Seats', bn: 'আসন্ন যাত্রার সূচি ও আসন সংখ্যা' },
    'View All Dates →': { en: 'View All Dates →', bn: 'সব তারিখ দেখুন →' },
    'সব তারিখ দেখুন →': { en: 'View All Dates →', bn: 'সব তারিখ দেখুন →' },
    'AUTHENTIC TRAVEL LOGS': { en: 'AUTHENTIC TRAVEL LOGS', bn: 'ভ্রমণ কাহিনী ও বাস্তব অভিজ্ঞতা' },
    'ভ্রমণ কাহিনী ও বাস্তব অভিজ্ঞতা': { en: 'AUTHENTIC TRAVEL LOGS', bn: 'ভ্রমণ কাহিনী ও বাস্তব অভিজ্ঞতা' },
    'Travel Stories & Genuine Experiences': { en: 'Travel Stories & Genuine Experiences', bn: 'ভ্রমণের গল্প ও বাস্তব অভিজ্ঞতা' },
    'ভ্রমণের গল্প ও বাস্তব অভিজ্ঞতা': { en: 'Travel Stories & Genuine Experiences', bn: 'ভ্রমণের গল্প ও বাস্তব অভিজ্ঞতা' },
    'Read All Stories →': { en: 'Read All Stories →', bn: 'সব গল্প পড়ুন →' },
    'সব গল্প পড়ুন →': { en: 'Read All Stories →', bn: 'সব গল্প পড়ুন →' },
    'PHOTO & VIDEO GALLERY': { en: 'PHOTO & VIDEO GALLERY', bn: 'ছবি ও ভিডিও গ্যালারি' },
    'ছবি ও ভিডিও গ্যালারি': { en: 'PHOTO & VIDEO GALLERY', bn: 'ছবি ও ভিডিও গ্যালারি' },
    'Memories of Beautiful Bangladesh': { en: 'Memories of Beautiful Bangladesh', bn: 'স্মৃতির ফ্রেমে বাঁধা বাংলাদেশের সৌন্দর্য' },
    'স্মৃতির ফ্রেমে বাঁধা বাংলাদেশের সৌন্দর্য': { en: 'Memories of Beautiful Bangladesh', bn: 'স্মৃতির ফ্রেমে বাঁধা বাংলাদেশের সৌন্দর্য' },
    'Explore Full Gallery': { en: 'Explore Full Gallery', bn: 'পুরো গ্যালারি এক্সপ্লোর করুন' },
    'পুরো গ্যালারি এক্সপ্লোর করুন': { en: 'Explore Full Gallery', bn: 'পুরো গ্যালারি এক্সপ্লোর করুন' },
    'TRAVELER TESTIMONIALS': { en: 'TRAVELER TESTIMONIALS', bn: 'ভ্রমণকারীদের মন্তব্য' },
    'ভ্রমণকারীদের মন্তব্য': { en: 'TRAVELER TESTIMONIALS', bn: 'ভ্রমণকারীদের মন্তব্য' },
    'Words of Joy from Travelers': { en: 'Words of Joy from Travelers', bn: 'ভ্রমণকারীদের ভালোলাগার কথা' },
    'ভ্রমণকারীদের ভালোলাগার কথা': { en: 'Words of Joy from Travelers', bn: 'ভ্রমণকারীদের ভালোলাগার কথা' },
    'HAVE QUESTIONS?': { en: 'HAVE QUESTIONS?', bn: 'প্রশ্ন আছে কি?' },
    'প্রশ্ন আছে কি?': { en: 'HAVE QUESTIONS?', bn: 'প্রশ্ন আছে কি?' },
    'Frequently Asked Questions (FAQ)': { en: 'Frequently Asked Questions (FAQ)', bn: 'সচরাচর জিজ্ঞাসিত প্রশ্নসমূহ (FAQ)' },
    'সচরাচর জিজ্ঞাসিত প্রশ্নসমূহ (FAQ)': { en: 'Frequently Asked Questions (FAQ)', bn: 'সচরাচর জিজ্ঞাসিত প্রশ্নসমূহ (FAQ)' },

    // Card Details & Actions
    'Price per person': { en: 'Price per person', bn: 'জনপ্রতি প্যাকেজ মূল্য' },
    'জনপ্রতি প্যাকেজ মূল্য': { en: 'Price per person', bn: 'জনপ্রতি প্যাকেজ মূল্য' },
    'Per person': { en: 'Per person', bn: 'জনপ্রতি' },
    'জনপ্রতি': { en: 'Per person', bn: 'জনপ্রতি' },
    'View Details': { en: 'View Details', bn: 'বিস্তারিত' },
    'বিস্তারিত': { en: 'View Details', bn: 'বিস্তারিত' },
    'Book Now': { en: 'Book Now', bn: 'বুক করুন' },
    'বুক করুন': { en: 'Book Now', bn: 'বুক করুন' },
    'View Tours': { en: 'View Tours', bn: 'ট্যুরগুলো দেখুন' },
    'ট্যুরগুলো দেখুন': { en: 'View Tours', bn: 'ট্যুরগুলো দেখুন' },
    'Read Full Story': { en: 'Read Full Story', bn: 'পুরো গল্প পড়ুন' },
    'পুরো গল্প পড়ুন': { en: 'Read Full Story', bn: 'পুরো গল্প পড়ুন' },
    'Days': { en: 'Days', bn: 'দিন' },
    'দিন': { en: 'Days', bn: 'দিন' },
    'Nights': { en: 'Nights', bn: 'রাত' },
    'রাত': { en: 'Nights', bn: 'রাত' },
    'persons': { en: 'persons', bn: 'জন' },
    'জন': { en: 'persons', bn: 'জন' },
    'seats left': { en: 'seats left', bn: 'টি বাকি' },
    'টি বাকি': { en: 'seats left', bn: 'টি বাকি' },
    'Discount': { en: 'Discount', bn: 'ছাড়' },
    'ছাড়': { en: 'Discount', bn: 'ছাড়' },
    'Sold Out': { en: 'Sold Out', bn: 'আসন পূর্ণ' },
    'আসন পূর্ণ': { en: 'Sold Out', bn: 'আসন পূর্ণ' },

    // Tour Catalog & Filters
    'ALL JOURNEYS & EXPEDITIONS': { en: 'ALL JOURNEYS & EXPEDITIONS', bn: 'সকল যাত্রা ও অভিযান' },
    'Find Your Dream Travel Package': { en: 'Find Your Dream Travel Package', bn: 'আপনার পছন্দের ভ্রমণ প্যাকেজ খুঁজুন' },
    'আপনার পছন্দের ভ্রমণ প্যাকেজ খুঁজুন': { en: 'Find Your Dream Travel Package', bn: 'আপনার পছন্দের ভ্রমণ প্যাকেজ খুঁজুন' },
    'Destination': { en: 'Destination', bn: 'গন্তব্য' },
    'Category': { en: 'Category', bn: 'ক্যাটাগরি' },
    'Duration': { en: 'Duration', bn: 'সময়কাল' },
    'All Destinations': { en: 'All Destinations', bn: 'সকল গন্তব্য' },
    'All Categories': { en: 'All Categories', bn: 'সকল ক্যাটাগরি' },
    'All Durations': { en: 'All Durations', bn: 'সকল সময়কাল' },
    'Featured & Popular': { en: 'Featured & Popular', bn: 'জনপ্রিয় ও নতুন' },
    'Price: Low to High': { en: 'Price: Low to High', bn: 'মূল্য: কম থেকে বেশি' },
    'Price: High to Low': { en: 'Price: High to Low', bn: 'মূল্য: বেশি থেকে কম' },
    'Top Rated': { en: 'Top Rated', bn: 'সর্বোচ্চ রেটিং' },
    'Clear All Filters': { en: 'Clear All Filters', bn: 'সব ফিল্টার ক্লিয়ার করুন' },
    'সব ফিল্টার ক্লিয়ার করুন': { en: 'Clear All Filters', bn: 'সব ফিল্টার ক্লিয়ার করুন' },
    'No Tour Packages Found': { en: 'No Tour Packages Found', bn: 'কোনো ট্যুর প্যাকেজ পাওয়া যায়নি' },
    'কোনো ট্যুর প্যাকেজ পাওয়া যায়নি': { en: 'No Tour Packages Found', bn: 'কোনো ট্যুর প্যাকেজ পাওয়া যায়নি' },

    // Tour Detail Page
    'Tour Overview & Highlights': { en: 'Tour Overview & Highlights', bn: 'ট্যুর পরিচিতি ও হাইলাইটস' },
    'ট্যুর পরিচিতি ও হাইলাইটস': { en: 'Tour Overview & Highlights', bn: 'ট্যুর পরিচিতি ও হাইলাইটস' },
    'Upcoming Departure Dates': { en: 'Upcoming Departure Dates', bn: 'আসন্ন যাত্রার তারিখসমূহ' },
    'আসন্ন যাত্রার তারিখসমূহ': { en: 'Upcoming Departure Dates', bn: 'আসন্ন যাত্রার তারিখসমূহ' },
    'Day-by-Day Itinerary': { en: 'Day-by-Day Itinerary', bn: 'দিনভিত্তিক ভ্রমণ পরিকল্পনা' },
    'দিনভিত্তিক ভ্রমণ পরিকল্পনা': { en: 'Day-by-Day Itinerary', bn: 'দিনভিত্তিক ভ্রমণ পরিকল্পনা' },
    'Included in Package': { en: 'Included in Package', bn: 'প্যাকেজে যা অন্তর্ভুক্ত' },
    'প্যাকেজে যা অন্তর্ভুক্ত': { en: 'Included in Package', bn: 'প্যাকেজে যা অন্তর্ভুক্ত' },
    'Not Included (Excluded)': { en: 'Not Included (Excluded)', bn: 'যা অন্তর্ভুক্ত নয়' },
    'যা অন্তর্ভুক্ত নয়': { en: 'Not Included (Excluded)', bn: 'যা অন্তর্ভুক্ত নয়' },
    'Tour Photo Gallery': { en: 'Tour Photo Gallery', bn: 'ট্যুর ফটো গ্যালারি' },
    'ট্যুর ফটো গ্যালারি': { en: 'Tour Photo Gallery', bn: 'ট্যুর ফটো গ্যালারি' },
    'Special Package Rate per Person': { en: 'Special Package Rate per Person', bn: 'জনপ্রতি স্পেশাল প্যাকেজ রেট' },
    'জনপ্রতি স্পেশাল প্যাকেজ রেট': { en: 'Special Package Rate per Person', bn: 'জনপ্রতি স্পেশাল প্যাকেজ রেট' },
    'Tour Duration:': { en: 'Tour Duration:', bn: 'ট্যুর সময়কাল:' },
    'ট্যুর সময়কাল:': { en: 'Tour Duration:', bn: 'ট্যুর সময়কাল:' },
    'Destination:': { en: 'Destination:', bn: 'গন্তব্য:' },
    'গন্তব্য:': { en: 'Destination:', bn: 'গন্তব্য:' },
    'Confirmed Seat:': { en: 'Confirmed Seat:', bn: 'নিশ্চিত আসন:' },
    'নিশ্চিত আসন:': { en: 'Confirmed Seat:', bn: 'নিশ্চিত আসন:' },
    'Instant Confirmation': { en: 'Instant Confirmation', bn: 'ইনস্ট্যান্ট কনফার্মেশন' },
    'ইনস্ট্যান্ট কনফার্মেশন': { en: 'Instant Confirmation', bn: 'ইনস্ট্যান্ট কনফার্মেশন' },
    'Book Seat': { en: 'Book Seat', bn: 'সিট বুক করুন' },
    'সিট বুক করুন': { en: 'Book Seat', bn: 'সিট বুক করুন' },
    'Meals:': { en: 'Meals:', bn: 'খাবার:' },
    'খাবার:': { en: 'Meals:', bn: 'খাবার:' },
    'Stay:': { en: 'Stay:', bn: 'রাত্রিবাস:' },
    'রাত্রিবাস:': { en: 'Stay:', bn: 'রাত্রিবাস:' },
    'Escort & Safety': { en: 'Escort & Safety', bn: 'এসকর্ট ও নিরাপত্তা' },
    '🔒 100% Safe Payment & Easy Refund Policy': { en: '🔒 100% Safe Payment & Easy Refund Policy', bn: '🔒 ১০০% নিরাপদ পেমেন্ট ও সহজ রিফান্ড পলিসি' },
    '🔒 ১০০% নিরাপদ পেমেন্ট ও সহজ রিফান্ড পলিসি': { en: '🔒 100% Safe Payment & Easy Refund Policy', bn: '🔒 ১০০% নিরাপদ পেমেন্ট ও সহজ রিফান্ড পলিসি' },

    // Booking Process
    'INSTANT RESERVATION': { en: 'INSTANT RESERVATION', bn: 'ইনস্ট্যান্ট রিজার্ভেশন' },
    'Confirm Your Journey': { en: 'Confirm Your Journey', bn: 'আপনার যাত্রা নিশ্চিত করুন' },
    'আপনার যাত্রা নিশ্চিত করুন': { en: 'Confirm Your Journey', bn: 'আপনার যাত্রা নিশ্চিত করুন' },
    'Selected Tour & Date': { en: 'Selected Tour & Date', bn: 'নির্বাচিত ট্যুর ও তারিখ' },
    'নির্বাচিত ট্যুর ও তারিখ': { en: 'Selected Tour & Date', bn: 'নির্বাচিত ট্যুর ও তারিখ' },
    'Number of Travelers': { en: 'Number of Travelers', bn: 'যাত্রীদের সংখ্যা' },
    'যাত্রীদের সংখ্যা': { en: 'Number of Travelers', bn: 'যাত্রীদের সংখ্যা' },
    'Total Travelers': { en: 'Total Travelers', bn: 'মোট ভ্রমণকারী' },
    'মোট ভ্রমণকারী': { en: 'Total Travelers', bn: 'মোট ভ্রমণকারী' },
    'Including adults and children': { en: 'Including adults and children', bn: 'প্রাপ্তবয়স্ক ও শিশুসহ' },
    'প্রাপ্তবয়স্ক ও শিশুসহ': { en: 'Including adults and children', bn: 'প্রাপ্তবয়স্ক ও শিশুসহ' },
    'Customer Details': { en: 'Customer Details', bn: 'গ্রাহকের তথ্য' },
    'গ্রাহকের তথ্য': { en: 'Customer Details', bn: 'গ্রাহকের তথ্য' },
    'Full Name *': { en: 'Full Name *', bn: 'পূর্ণ নাম *' },
    'পূর্ণ নাম *': { en: 'Full Name *', bn: 'পূর্ণ নাম *' },
    'Email Address *': { en: 'Email Address *', bn: 'ইমেইল ঠিকানা *' },
    'ইমেইল ঠিকানা *': { en: 'Email Address *', bn: 'ইমেইল ঠিকানা *' },
    'Phone Number *': { en: 'Phone Number *', bn: 'মোবাইল নম্বর *' },
    'মোবাইল নম্বর *': { en: 'Phone Number *', bn: 'মোবাইল নম্বর *' },
    'Address': { en: 'Address', bn: 'ঠিকানা' },
    'ঠিকানা': { en: 'Address', bn: 'ঠিকানা' },
    'Special Request / Notes': { en: 'Special Request / Notes', bn: 'বিশেষ কোনো অনুরোধ বা নোট' },
    'বিশেষ কোনো অনুরোধ বা নোট': { en: 'Special Request / Notes', bn: 'বিশেষ কোনো অনুরোধ বা নোট' },
    'Total Payable': { en: 'Total Payable', bn: 'মোট প্রদেয় টাকা' },
    'মোট প্রদেয় টাকা': { en: 'Total Payable', bn: 'মোট প্রদেয় টাকা' },
    'Proceed to Payment': { en: 'Proceed to Payment', bn: 'পেমেন্টে এগিয়ে যান' },
    'পেমেন্টে এগিয়ে যান': { en: 'Proceed to Payment', bn: 'পেমেন্টে এগিয়ে যান' },

    // Payment & Verification
    'SECURE MANUAL & GATEWAY CHECKOUT': { en: 'SECURE MANUAL & GATEWAY CHECKOUT', bn: 'নিরাপদ পেমেন্ট চেকআউট' },
    'Complete Payment': { en: 'Complete Payment', bn: 'পেমেন্ট সম্পন্ন করুন' },
    'পেমেন্ট সম্পন্ন করুন': { en: 'Complete Payment', bn: 'পেমেন্ট সম্পন্ন করুন' },
    'Choose Payment Method': { en: 'Choose Payment Method', bn: 'পেমেন্ট মেথড বেছে নিন' },
    'পেমেন্ট মেথড বেছে নিন': { en: 'Choose Payment Method', bn: 'পেমেন্ট মেথড বেছে নিন' },
    'Official bKash Number': { en: 'Official bKash Number', bn: 'অফিশিয়াল বিকাশ নম্বর' },
    'অফিশিয়াল বিকাশ নম্বর': { en: 'Official bKash Number', bn: 'অফিশিয়াল বিকাশ নম্বর' },
    'Official Nagad Number': { en: 'Official Nagad Number', bn: 'অফিশিয়াল নগদ নম্বর' },
    'অফিশিয়াল নগদ নম্বর': { en: 'Official Nagad Number', bn: 'অফিশিয়াল নগদ নম্বর' },
    'Copy Number': { en: 'Copy Number', bn: 'নম্বর কপি' },
    'নম্বর কপি': { en: 'Copy Number', bn: 'নম্বর কপি' },
    'Copied!': { en: 'Copied!', bn: 'কপি হয়েছে!' },
    'কপি হয়েছে!': { en: 'Copied!', bn: 'কপি হয়েছে!' },
    'Open bKash App': { en: 'Open bKash App', bn: 'বিকাশ অ্যাপ ওপেন করুন' },
    'বিকাশ অ্যাপ ওপেন করুন': { en: 'Open bKash App', bn: 'বিকাশ অ্যাপ ওপেন করুন' },
    'Open Nagad App': { en: 'Open Nagad App', bn: 'নগদ অ্যাপ ওপেন করুন' },
    'নগদ অ্যাপ ওপেন করুন': { en: 'Open Nagad App', bn: 'নগদ অ্যাপ ওপেন করুন' },
    'Bank Payment': { en: 'Bank Payment', bn: 'ব্যাংক পেমেন্ট' },
    'ব্যাংক পেমেন্ট': { en: 'Bank Payment', bn: 'ব্যাংক পেমেন্ট' },
    'On Hold': { en: 'On Hold', bn: 'স্থগিত' },
    'স্থগিত': { en: 'On Hold', bn: 'স্থগিত' },
    'Temporarily On Hold': { en: 'Temporarily On Hold', bn: 'সাময়িকভাবে স্থগিত' },
    'সাময়িকভাবে স্থগিত': { en: 'Temporarily On Hold', bn: 'সাময়িকভাবে স্থগিত' },
    'Bank Payment is Temporarily On Hold': { en: 'Bank Payment is Temporarily On Hold', bn: 'ব্যাংক পেমেন্ট অপশনটি আপাতত স্থগিত রয়েছে' },
    'ব্যাংক পেমেন্ট অপশনটি আপাতত স্থগিত রয়েছে': { en: 'Bank Payment is Temporarily On Hold', bn: 'ব্যাংক পেমেন্ট অপশনটি আপাতত স্থগিত রয়েছে' },
    'Submit Payment Verification': { en: 'Submit Payment Verification', bn: 'পেমেন্ট যাচাইয়ের জন্য জমা দিন' },
    'পেমেন্ট যাচাইয়ের জন্য জমা দিন': { en: 'Submit Payment Verification', bn: 'পেমেন্ট যাচাইয়ের জন্য জমা দিন' },
    'Sender bKash / Nagad Number': { en: 'Sender bKash / Nagad Number', bn: 'প্রেরক বিকাশ / নগদ নম্বর' },
    'Transaction ID (TrxID)': { en: 'Transaction ID (TrxID)', bn: 'লেনদেন নম্বর (TrxID)' },
    'Payment Submitted • Under Verification': { en: 'Payment Submitted • Under Verification', bn: 'পেমেন্ট জমা সম্পন্ন • ভেরিফিকেশন চলছে' },
    'পেমেন্ট জমা সম্পন্ন • ভেরিফিকেশন চলছে': { en: 'Payment Submitted • Under Verification', bn: 'পেমেন্ট জমা সম্পন্ন • ভেরিফিকেশন চলছে' },
    'Your Payment is Under Verification': { en: 'Your Payment is Under Verification', bn: 'আপনার পেমেন্ট ভেরিফিকেশনের অধীনে রয়েছে' },
    'আপনার পেমেন্ট ভেরিফিকেশনের অধীনে রয়েছে': { en: 'Your Payment is Under Verification', bn: 'আপনার পেমেন্ট ভেরিফিকেশনের অধীনে রয়েছে' },
    'Booking Reference ID': { en: 'Booking Reference ID', bn: 'বুকিং রেফারেন্স নম্বর' },
    'বুকিং রেফারেন্স নম্বর': { en: 'Booking Reference ID', bn: 'বুকিং রেফারেন্স নম্বর' },
    'Pending Verification': { en: 'Pending Verification', bn: 'ভেরিফিকেশন অপেক্ষমাণ' },
    'ভেরিফিকেশন অপেক্ষমাণ': { en: 'Pending Verification', bn: 'ভেরিফিকেশন অপেক্ষমাণ' },
    'Tour Package:': { en: 'Tour Package:', bn: 'ট্যুর প্যাকেজ:' },
    'ট্যুর প্যাকেজ:': { en: 'Tour Package:', bn: 'ট্যুর প্যাকেজ:' },
    'Travel Date:': { en: 'Travel Date:', bn: 'ভ্রমণের তারিখ:' },
    'ভ্রমণের তারিখ:': { en: 'Travel Date:', bn: 'ভ্রমণের তারিখ:' },
    'Customer Name:': { en: 'Customer Name:', bn: 'গ্রাহকের নাম:' },
    'গ্রাহকের নাম:': { en: 'Customer Name:', bn: 'গ্রাহকের নাম:' },
    'Travelers:': { en: 'Travelers:', bn: 'যাত্রী সংখ্যা:' },
    'যাত্রী সংখ্যা:': { en: 'Travelers:', bn: 'যাত্রী সংখ্যা:' },
    'Payment Method:': { en: 'Payment Method:', bn: 'পেমেন্ট মাধ্যম:' },
    'পেমেন্ট মাধ্যম:': { en: 'Payment Method:', bn: 'পেমেন্ট মাধ্যম:' },
    'Sender Number:': { en: 'Sender Number:', bn: 'প্রেরক নম্বর:' },
    'প্রেরক নম্বর:': { en: 'Sender Number:', bn: 'প্রেরক নম্বর:' },
    'Transaction ID:': { en: 'Transaction ID:', bn: 'লেনদেন নম্বর:' },
    'লেনদেন নম্বর:': { en: 'Transaction ID:', bn: 'লেনদেন নম্বর:' },
    'Paid Amount:': { en: 'Paid Amount:', bn: 'পরিশোধিত টাকা:' },
    'পরিশোধিত টাকা:': { en: 'Paid Amount:', bn: 'পরিশোধিত টাকা:' },
    'What happens next?': { en: 'What happens next?', bn: 'পরবর্তী পদক্ষেপ' },
    'পরবর্তী পদক্ষেপ': { en: 'What happens next?', bn: 'পরবর্তী পদক্ষেপ' },
    'Track Booking Status': { en: 'Track Booking Status', bn: 'বুকিং স্ট্যাটাস ট্র্যাক করুন' },
    'বুকিং স্ট্যাটাস ট্র্যাক করুন': { en: 'Track Booking Status', bn: 'বুকিং স্ট্যাটাস ট্র্যাক করুন' },
    'Return to Home': { en: 'Return to Home', bn: 'হোম পেজে ফিরুন' },
    'হোম পেজে ফিরুন': { en: 'Return to Home', bn: 'হোম পেজে ফিরুন' },
    'Flexible': { en: 'Flexible', bn: 'ফ্লেক্সিবল' },
    'ফ্লেক্সিবল': { en: 'Flexible', bn: 'ফ্লেক্সিবল' },

    // Booking Success / Voucher
    'BOOKING CONFIRMED': { en: 'BOOKING CONFIRMED', bn: 'বুকিং নিশ্চিত হয়েছে' },
    'Congratulations! Your Booking is Confirmed': { en: 'Congratulations! Your Booking is Confirmed', bn: 'অভিনন্দন! আপনার বুকিং নিশ্চিত হয়েছে' },
    'অভিনন্দন! আপনার বুকিং নিশ্চিত হয়েছে': { en: 'Congratulations! Your Booking is Confirmed', bn: 'অভিনন্দন! আপনার বুকিং নিশ্চিত হয়েছে' },
    'Official Voucher': { en: 'Official Voucher', bn: 'ভ্রমণঘুড়ি ভাউচার' },
    'Download Voucher PDF': { en: 'Download Voucher PDF', bn: 'ভাউচার PDF ডাউনলোড' },
    'ভাউচার PDF ডাউনলোড': { en: 'Download Voucher PDF', bn: 'ভাউচার PDF ডাউনলোড' },
    'Print Voucher': { en: 'Print Voucher', bn: 'প্রিন্ট করুন' },
    'প্রিন্ট করুন': { en: 'Print Voucher', bn: 'প্রিন্ট করুন' },

    // Footer
    'Quick Links': { en: 'Quick Links', bn: 'দ্রুত লিঙ্ক' },
    'দ্রুত লিঙ্ক': { en: 'Quick Links', bn: 'দ্রুত লিঙ্ক' },
    'Information & Support': { en: 'Information & Support', bn: 'তথ্য ও সহায়তা' },
    'তথ্য ও সহায়তা': { en: 'Information & Support', bn: 'তথ্য ও সহায়তা' },
    'Frequently Asked Questions': { en: 'Frequently Asked Questions', bn: 'সচরাচর জিজ্ঞাসা' },
    'সচরাচর জিজ্ঞাসা': { en: 'Frequently Asked Questions', bn: 'সচরাচর জিজ্ঞাসা' },
    'View Location on Google Maps': { en: 'View Location on Google Maps', bn: 'গুগল ম্যাপে লোকেশন দেখুন' },
    'গুগল ম্যাপে লোকেশন দেখুন': { en: 'View Location on Google Maps', bn: 'গুগল ম্যাপে লোকেশন দেখুন' },
    'Safe Travel • Modern Experience • Responsible Tourism': { en: 'Safe Travel • Modern Experience • Responsible Tourism', bn: 'নিরাপদ ভ্রমণ • আধুনিক অভিজ্ঞতা • দায়িত্বশীল পর্যটন' },
    'নিরাপদ ভ্রমণ • আধুনিক অভিজ্ঞতা • দায়িত্বশীল পর্যটন': { en: 'Safe Travel • Modern Experience • Responsible Tourism', bn: 'নিরাপদ ভ্রমণ • আধুনিক অভিজ্ঞতা • দায়িত্বশীল পর্যটন' },
    'All rights reserved.': { en: 'All rights reserved.', bn: 'সর্বস্বত্ব সংরক্ষিত।' },
    'সর্বস্বত্ব সংরক্ষিত।': { en: 'All rights reserved.', bn: 'সর্বস্বত্ব সংরক্ষিত।' },

    // Additional Core Pages & Forms
    'Check Your Booking Status': { en: 'Check Your Booking Status', bn: 'আপনার বুকিং স্ট্যাটাস যাচাই করুন' },
    'আপনার বুকিং স্ট্যাটাস যাচাই করুন': { en: 'Check Your Booking Status', bn: 'আপনার বুকিং স্ট্যাটাস যাচাই করুন' },
    'Booking Reference Number': { en: 'Booking Reference Number', bn: 'বুকিং রেফারেন্স নম্বর' },
    'বুকিং রেফারেন্স নম্বর': { en: 'Booking Reference Number', bn: 'বুকিং রেফারেন্স নম্বর' },
    'Search Booking': { en: 'Search Booking', bn: 'অনুসন্ধান করুন' },
    'Current Status': { en: 'Current Status', bn: 'বর্তমান স্ট্যাটাস' },
    'বর্তমান স্ট্যাটাস': { en: 'Current Status', bn: 'বর্তমান স্ট্যাটাস' },
    'Traveler:': { en: 'Traveler:', bn: 'যাত্রী:' },
    'যাত্রী:': { en: 'Traveler:', bn: 'যাত্রী:' },
    'Total Amount:': { en: 'Total Amount:', bn: 'মোট টাকা:' },
    'মোট টাকা:': { en: 'Total Amount:', bn: 'মোট টাকা:' },
    'Voucher PDF': { en: 'Voucher PDF', bn: 'ভাউচার PDF' },
    'ভাউচার PDF': { en: 'Voucher PDF', bn: 'ভাউচার PDF' },
    'Online Voucher →': { en: 'Online Voucher →', bn: 'অনলাইন ভাউচার →' },
    'অনলাইন ভাউচার →': { en: 'Online Voucher →', bn: 'অনলাইন ভাউচার →' },
    'View Verification Status →': { en: 'View Verification Status →', bn: 'ভেরিফিকেশন স্ট্যাটাস দেখুন →' },
    'ভেরিফিকেশন স্ট্যাটাস দেখুন →': { en: 'View Verification Status →', bn: 'ভেরিফিকেশন স্ট্যাটাস দেখুন →' },
    'Complete Payment →': { en: 'Complete Payment →', bn: 'পেমেন্ট সম্পন্ন করুন →' },
    'পেমেন্ট সম্পন্ন করুন →': { en: 'Complete Payment →', bn: 'পেমেন্ট সম্পন্ন করুন →' },
    'Selected Tour & Date': { en: 'Selected Tour & Date', bn: 'নির্বাচিত ট্যুর ও তারিখ' },
    'নির্বাচিত ট্যুর ও তারিখ': { en: 'Selected Tour & Date', bn: 'নির্বাচিত ট্যুর ও তারিখ' },
    'Total Price:': { en: 'Total Price:', bn: 'সর্বমোট মূল্য:' },
    'সর্বমোট মূল্য:': { en: 'Total Price:', bn: 'সর্বমোট মূল্য:' },
    'Download Official Voucher PDF': { en: 'Download Official Voucher PDF', bn: 'অফিশিয়াল ভাউচার PDF ডাউনলোড' },
    'অফিশিয়াল ভাউচার PDF ডাউনলোড': { en: 'Download Official Voucher PDF', bn: 'অফিশিয়াল ভাউচার PDF ডাউনলোড' },
    'Booking Order Details': { en: 'Booking Order Details', bn: 'বুকিং অর্ডার বিবরণ' },
    'বুকিং অর্ডার বিবরণ': { en: 'Booking Order Details', bn: 'বুকিং অর্ডার বিবরণ' },
    'Submit for Verification →': { en: 'Submit for Verification →', bn: 'পেমেন্ট তথ্য সাবমিট করুন' },
    'Our Journey & Philosophy': { en: 'Our Journey & Philosophy', bn: 'ভ্রমণঘুড়ির পথচলা ও দর্শন' },
    'ভ্রমণঘুড়ির পথচলা ও দর্শন': { en: 'Our Journey & Philosophy', bn: 'ভ্রমণঘুড়ির পথচলা ও দর্শন' },
    'Safety First': { en: 'Safety First', bn: 'নিরাপত্তা প্রথম' },
    'নিরাপত্তা প্রথম': { en: 'Safety First', bn: 'নিরাপত্তা প্রথম' },
    'Responsible Tourism': { en: 'Responsible Tourism', bn: 'দায়িত্বশীল পর্যটন' },
    'দায়িত্বশীল পর্যটন': { en: 'Responsible Tourism', bn: 'দায়িত্বশীল পর্যটন' },
    'Trusted Quality': { en: 'Trusted Quality', bn: 'বিশ্বস্ত সেবা' },
    'বিশ্বস্ত সেবা': { en: 'Trusted Quality', bn: 'বিশ্বস্ত সেবা' },
    'Contact Our Travel Experts': { en: 'Contact Our Travel Experts', bn: 'আমাদের সাথে যোগাযোগ' },
    'BhromonGhuri Head Office': { en: 'BhromonGhuri Head Office', bn: 'ভ্রমণঘুড়ি হেড অফিস' },
    'Send Message': { en: 'Send Message', bn: 'বার্তা পাঠান' },
    'বার্তা পাঠান': { en: 'Send Message', bn: 'বার্তা পাঠান' },
    'Return to Homepage': { en: 'Return to Homepage', bn: 'হোম পেজে ফিরে যান' },
    'হোম পেজে ফিরে যান': { en: 'Return to Homepage', bn: 'হোম পেজে ফিরে যান' },
    'This Trail Could Not Be Found!': { en: 'This Trail Could Not Be Found!', bn: 'এই পথটি খুঁজে পাওয়া যায়নি!' },
    'Temporary Server Error': { en: 'Temporary Server Error', bn: 'সাময়িক সার্ভার ত্রুটি' }
  };

  const originalTextNodes = new Map();

  function getStoredLanguage() {
    // Default to English as specified in Problem 3
    return localStorage.getItem(STORAGE_KEY) || 'en';
  }

  function applyPureBilingualTranslation(targetLang) {
    // 1. Primary: Explicit data-en & data-bn elements
    document.querySelectorAll('[data-en][data-bn]').forEach((el) => {
      const targetText = targetLang === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-bn');
      if (targetText && el.textContent.trim() !== targetText.trim()) {
        el.textContent = targetText;
      }
    });

    // 2. Input & Textarea Placeholders with data-en-placeholder & data-bn-placeholder
    document.querySelectorAll('[data-en-placeholder][data-bn-placeholder]').forEach((el) => {
      const targetPlaceholder = targetLang === 'en' ? el.getAttribute('data-en-placeholder') : el.getAttribute('data-bn-placeholder');
      if (targetPlaceholder) {
        el.setAttribute('placeholder', targetPlaceholder);
      }
    });

    // 3. Fallback dictionary tree-walk across text nodes
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
          // Never translate or alter the brand logo
          if (parent.closest('a[aria-label="ভ্রমণঘুড়ি"]') || parent.classList.contains('brand-logo-text')) {
            return NodeFilter.FILTER_REJECT;
          }
          const text = node.nodeValue.trim();
          if (text === 'ভ্রমণঘুড়ি' || text === 'ভ্রমণঘুরি') {
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

      // Exact dictionary match
      if (translations[trimmed] && translations[trimmed][targetLang]) {
        node.nodeValue = rawText.replace(trimmed, translations[trimmed][targetLang]);
        return;
      }

      // Reverse dictionary match
      for (const mapping of Object.values(translations)) {
        if (mapping.en === trimmed || mapping.bn === trimmed) {
          const replacement = mapping[targetLang];
          if (replacement) {
            node.nodeValue = rawText.replace(trimmed, replacement);
            return;
          }
        }
      }

      // Substring replace for multi-item phrases
      let updatedText = rawText;
      let modified = false;
      for (const mapping of Object.values(translations)) {
        if (mapping.en && mapping.bn) {
          if (targetLang === 'en' && mapping.bn.length > 3 && updatedText.includes(mapping.bn)) {
            updatedText = updatedText.replaceAll(mapping.bn, mapping.en);
            modified = true;
          } else if (targetLang === 'bn' && mapping.en.length > 3 && updatedText.includes(mapping.en)) {
            updatedText = updatedText.replaceAll(mapping.en, mapping.bn);
            modified = true;
          }
        }
      }
      if (modified) {
        node.nodeValue = updatedText;
      }
    });

    // 4. Update input placeholders matching dictionary
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

  function clearGoogleTranslateArtifacts() {
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + window.location.hostname + ';';
  }

  window.setSiteLanguage = function (targetLang) {
    if (targetLang !== 'en' && targetLang !== 'bn') return;

    localStorage.setItem(STORAGE_KEY, targetLang);
    updateNavbarUI(targetLang);
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
