import urllib.request

urls = [
    ('Homepage', 'http://127.0.0.1:8000/'),
    ('Tours List', 'http://127.0.0.1:8000/tours/'),
    ('Tours Search HTMX', 'http://127.0.0.1:8000/tours/?q=sajek'),
    ('Tour Detail', 'http://127.0.0.1:8000/tours/sajek-cloud-kingdom-adventure/'),
    ('Booking Form', 'http://127.0.0.1:8000/bookings/new/?tour=sajek-cloud-kingdom-adventure'),
    ('Booking Lookup', 'http://127.0.0.1:8000/bookings/lookup/'),
    ('Stories List', 'http://127.0.0.1:8000/stories/'),
    ('Story Detail', 'http://127.0.0.1:8000/stories/sajek-valley-first-touch-of-clouds/'),
    ('Gallery Showcase', 'http://127.0.0.1:8000/gallery/'),
    ('About Us', 'http://127.0.0.1:8000/about/'),
    ('Contact', 'http://127.0.0.1:8000/contact/'),
    ('Admin Login', 'http://127.0.0.1:8000/admin/login/'),
]

all_passed = True
for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"[PASS] {res.status} {name}: {url}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        all_passed = False

if all_passed:
    print("\nALL URLS ACCESSIBLE AND RETURNING 200 OK!")
else:
    exit(1)
