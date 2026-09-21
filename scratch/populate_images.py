import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tours.models import Destination, Tour

brain_dir = r'C:\Users\shams\.gemini\antigravity-ide\brain\f4dfbb9d-6da1-4be5-afb2-33b2791fb617'
dest_media = os.path.join('media', 'destinations')
tour_media = os.path.join('media', 'tours')
os.makedirs(dest_media, exist_ok=True)
os.makedirs(tour_media, exist_ok=True)

img_map = {
    'sajek': 'hero_sajek_travel_1789973099886.jpg',
    'bandarban': 'tour_bandarban_nilgiri_1789973121938.jpg',
    'saint-martin': 'tour_saint_martin_1789973148410.jpg',
    'sreemangal': 'tour_sreemangal_tea_1789973184510.jpg',
    'tanguar': 'tanguar_haor_boat_1789978310944.jpg',
    'sundarbans': 'sundarbans_mangrove_1789978467783.jpg'
}

for key, fname in img_map.items():
    src = os.path.join(brain_dir, fname)
    if os.path.exists(src):
        dst_dest = os.path.join(dest_media, f'{key}.jpg')
        dst_tour = os.path.join(tour_media, f'{key}.jpg')
        shutil.copy2(src, dst_dest)
        shutil.copy2(src, dst_tour)
        print(f'Copied {key} -> {dst_dest}')

mapping_dest = {
    'sajek': 'destinations/sajek.jpg',
    'bandarban': 'destinations/bandarban.jpg',
    'saint-martin': 'destinations/saint-martin.jpg',
    'sreemangal': 'destinations/sreemangal.jpg',
    'tanguar': 'destinations/tanguar.jpg',
    'sundarban': 'destinations/sundarbans.jpg',
}

for d in Destination.objects.all():
    slug_lower = d.slug.lower()
    for key, path in mapping_dest.items():
        if key in slug_lower:
            d.cover_image = path
            d.save()
            print(f'Updated Destination {d.name} -> {path}')

mapping_tour = {
    'sajek': 'tours/sajek.jpg',
    'bandarban': 'tours/bandarban.jpg',
    'saint-martin': 'tours/saint-martin.jpg',
    'sreemangal': 'tours/sreemangal.jpg',
    'tanguar': 'tours/tanguar.jpg',
    'sundarban': 'tours/sundarbans.jpg',
}

for t in Tour.objects.all():
    slug_lower = t.slug.lower()
    for key, path in mapping_tour.items():
        if key in slug_lower:
            t.cover_image = path
            t.save()
            print(f'Updated Tour {t.title} -> {path}')

print("Done! Verifying images:")
for d in Destination.objects.all():
    print("Destination:", d.name, "Cover:", d.cover_image)
for t in Tour.objects.all():
    print("Tour:", t.title, "Cover:", t.cover_image)
