import shutil
import os
from pathlib import Path

BASE = Path(r"K:\BhromonGhuri")
BRAIN = Path(r"C:\Users\shams\.gemini\antigravity-ide\brain\f4dfbb9d-6da1-4be5-afb2-33b2791fb617")

os.makedirs(BASE / "static" / "images", exist_ok=True)
os.makedirs(BASE / "media" / "tours", exist_ok=True)

img_hero = BRAIN / "hero_sajek_travel_1789973099886.jpg"
img_bandarban = BRAIN / "tour_bandarban_nilgiri_1789973121938.jpg"
img_stmartin = BRAIN / "tour_saint_martin_1789973148410.jpg"
img_sreemangal = BRAIN / "tour_sreemangal_tea_1789973184510.jpg"

if img_hero.exists():
    shutil.copy(img_hero, BASE / "static" / "images" / "hero-sajek.jpg")
    shutil.copy(img_hero, BASE / "media" / "tours" / "sajek-valley.jpg")
    print("Copied Sajek hero")

if img_bandarban.exists():
    shutil.copy(img_bandarban, BASE / "media" / "tours" / "bandarban-nilgiri.jpg")
    print("Copied Bandarban")

if img_stmartin.exists():
    shutil.copy(img_stmartin, BASE / "media" / "tours" / "saint-martin.jpg")
    print("Copied Saint Martin")

if img_sreemangal.exists():
    shutil.copy(img_sreemangal, BASE / "media" / "tours" / "sreemangal-tea.jpg")
    print("Copied Sreemangal")

# Assign them to existing tours in database
import sys
sys.path.insert(0, str(BASE))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.tours.models import Tour

t_sajek = Tour.objects.filter(slug__contains="sajek").first()
if t_sajek:
    t_sajek.cover_image = "tours/sajek-valley.jpg"
    t_sajek.save(update_fields=['cover_image'])
    print("Updated Sajek cover_image")

t_bandarban = Tour.objects.filter(slug__contains="bandarban").first()
if t_bandarban:
    t_bandarban.cover_image = "tours/bandarban-nilgiri.jpg"
    t_bandarban.save(update_fields=['cover_image'])
    print("Updated Bandarban cover_image")

t_sreemangal = Tour.objects.filter(slug__contains="sreemangal").first() or Tour.objects.filter(slug__contains="srimangal").first()
if t_sreemangal:
    t_sreemangal.cover_image = "tours/sreemangal-tea.jpg"
    t_sreemangal.save(update_fields=['cover_image'])
    print("Updated Sreemangal cover_image")

t_martin = Tour.objects.filter(slug__contains="saint").first() or Tour.objects.filter(slug__contains="martin").first()
if t_martin:
    t_martin.cover_image = "tours/saint-martin.jpg"
    t_martin.save(update_fields=['cover_image'])
    print("Updated Saint Martin cover_image")

# Also assign covers for all other tours to prevent placeholder boxes
for tour in Tour.objects.filter(cover_image=""):
    tour.cover_image = "tours/sajek-valley.jpg"
    tour.save(update_fields=['cover_image'])
    print(f"Set fallback cover for {tour.title}")

print("All tour cover images successfully assigned!")
