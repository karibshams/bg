from PIL import Image

im = Image.open('static/images/logo.png')
width, height = im.size

# Kite: from y=14 to y=232, x=480 to 625
# Let's check bbox of this crop
kite_crop = im.crop((480, 14, 625, 230))
# Clear any stray pixels below the yellow bow
k_w, k_h = kite_crop.size
k_pixels = kite_crop.load()

# Wordmark: y=250 to 520, x=17 to 647
wordmark_crop = im.crop((17, 252, 647, 520))

# We want a high-resolution horizontal logo:
# Let height = 140
# Wordmark height = 110
wm_ratio = 110.0 / wordmark_crop.height
wm_w = int(wordmark_crop.width * wm_ratio)
wordmark_scaled = wordmark_crop.resize((wm_w, 110), Image.Resampling.LANCZOS)

# Kite height = 115
kite_ratio = 115.0 / kite_crop.height
kite_w = int(kite_crop.width * kite_ratio)
kite_scaled = kite_crop.resize((kite_w, 115), Image.Resampling.LANCZOS)

# Combined horizontal logo
gap = 18
canvas_w = kite_w + gap + wm_w + 10
canvas_h = 130

horiz_img = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
horiz_img.paste(kite_scaled, (4, int((canvas_h - 115) / 2)), kite_scaled)
horiz_img.paste(wordmark_scaled, (kite_w + gap, int((canvas_h - 110) / 2)), wordmark_scaled)

# Save to static/images/logo-horizontal.png and static/images/logo-navbar.png
horiz_img.save('static/images/logo-horizontal.png')
horiz_img.save('static/images/logo-navbar.png')
horiz_img.save('C:/Users/shams/.gemini/antigravity-ide/brain/f4dfbb9d-6da1-4be5-afb2-33b2791fb617/logo-navbar.png')
print("Successfully generated logo-navbar.png:", horiz_img.size)
