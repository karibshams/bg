from PIL import Image
import os

p1 = r'C:\Users\shams\.gemini\antigravity-ide\brain\f4dfbb9d-6da1-4be5-afb2-33b2791fb617\.user_uploaded\media_1789980279068.jpg'
p2 = 'static/images/logo.png'
p3 = 'static/images/official-logo.png'
p4 = 'static/images/logo-navbar.png'

for p, name in [(p1, 'Uploaded'), (p2, 'logo.png'), (p3, 'official-logo.png'), (p4, 'logo-navbar.png')]:
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{name}: size={im.size}, mode={im.mode}")
    else:
        print(f"{name}: NOT FOUND")
