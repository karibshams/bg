from PIL import Image, ImageFilter

im = Image.open(r'C:\Users\shams\.gemini\antigravity-ide\brain\f4dfbb9d-6da1-4be5-afb2-33b2791fb617\.user_uploaded\media_1789980279068.jpg').convert('RGBA')

# Content bbox is roughly (115, 155, 760, 675)
crop = im.crop((115, 155, 760, 675))
w, h = crop.size
pixels = crop.load()

# Create clean transparent version
out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
out_pixels = out.load()

for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        # Calculate luminance / brightness
        brightness = max(r, g, b)
        if brightness < 20:
            out_pixels[x, y] = (0, 0, 0, 0)
        elif brightness < 60:
            # Smooth feather
            alpha = int((brightness - 20) / 40.0 * 255)
            out_pixels[x, y] = (r, g, b, alpha)
        else:
            out_pixels[x, y] = (r, g, b, 255)

out.save('static/images/official-logo-transparent.png')
out.save('static/images/logo.png')
print("Saved high-res transparent official logo:", out.size)

# Also generate a crystal clear horizontal logo for navbar:
# In this logo:
# Kite is top-right (x ~ 450 to 645, y ~ 0 to 220)
# Wordmark 'ভ্রমণঘুড়ি' is bottom (x ~ 0 to 645, y ~ 230 to 520)
kite_crop = out.crop((440, 0, 640, 225))
wordmark_crop = out.crop((0, 230, 640, 520))

# Make horizontal:
wm_h = 130
wm_ratio = wm_h / float(wordmark_crop.height)
wm_w = int(wordmark_crop.width * wm_ratio)
wm_scaled = wordmark_crop.resize((wm_w, wm_h), Image.Resampling.LANCZOS)

k_h = 135
k_ratio = k_h / float(kite_crop.height)
k_w = int(kite_crop.width * k_ratio)
k_scaled = kite_crop.resize((k_w, k_h), Image.Resampling.LANCZOS)

gap = 18
canvas_w = k_w + gap + wm_w + 10
canvas_h = 150

horiz = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
horiz.paste(k_scaled, (4, int((canvas_h - k_h) / 2)), k_scaled)
horiz.paste(wm_scaled, (k_w + gap, int((canvas_h - wm_h) / 2)), wm_scaled)

horiz.save('static/images/logo-navbar.png')
horiz.save('static/images/logo-horizontal.png')
print("Saved high-res horizontal navbar logo:", horiz.size)
