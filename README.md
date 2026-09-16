# 🪁 ভ্রমণঘুড়ি (Bhromonghuri) — Modern Travel Platform

A modern, animated travel and tour booking platform for Bangladesh built with **Django 5 + Django Templates + HTMX + Alpine.js + Tailwind CSS + GSAP & Lenis**.

> **"Django Admin controls the entire website. The frontend only displays the content."**

---

## 🌟 Key Features

* **Django 5 Backend & Custom Admin**: Comprehensive admin dashboard with inline itinerary editors, date slots, gallery managers, testimonials, FAQs, and site settings.
* **HTMX Dynamic Interactions**: Instant, smooth tour filtering by category, duration, destination, and budget without page reloads.
* **Alpine.js UI State**: Dynamic traveler counter with real-time price calculations, responsive mobile menu drawer, and fullscreen gallery lightbox.
* **GSAP + Lenis Animations**: Fluid hero parallax, gentle kite aerodynamic floating motion, magnetic CTA buttons, and 3D card tilts.
* **Bengali & English Identity**: Authentic branding with Hind Siliguri Bengali typography and Plus Jakarta Sans.
* **Booking & Payment Pipeline**: End-to-end customer booking flow with reference generation (`BG-2026-XXXXX`), date selection, traveler count, and simulated bKash/Nagad/Card checkout with webhook verification.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` (pre-configured for instant development):
```bash
cp .env.example .env
```

### 3. Run Migrations & Seed Data
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```
*Creates superuser (`admin` / `admin123`) and seeds Sajek Valley, Bandarban, Sreemangal, Tanguar Haor, Sundarbans, and Saint Martin tours, itineraries, stories, and reviews.*

### 4. Start Development Server
```bash
python manage.py runserver
```
Visit:
- Website: `http://127.0.0.1:8000/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

---

## 📁 Architecture

```text
bhromonghuri/
├── config/             # Django project settings & root URLs
├── apps/
│   ├── core/           # Home, site settings, testimonials, FAQs, seed_data
│   ├── tours/          # Tours, destinations, categories, itineraries, dates
│   ├── bookings/       # Customer bookings, references, traveler counts
│   ├── payments/       # Transaction tracking & simulated gateway service
│   ├── stories/        # Travel blog & Facebook travel history
│   └── gallery/        # Photo & video masonry showcase
├── templates/          # Modern semantic templates & HTMX partials
└── static/             # Tailwind, GSAP, Lenis, custom CSS & JS
```
