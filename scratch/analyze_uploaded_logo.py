from PIL import Image

im = Image.open(r'C:\Users\shams\.gemini\antigravity-ide\brain\f4dfbb9d-6da1-4be5-afb2-33b2791fb617\.user_uploaded\media_1789980279068.jpg')
print("Size:", im.size)

# Find bounding box of non-black pixels (black threshold < 30)
pixels = im.load()
w, h = im.size
min_x, max_x, min_y, max_y = w, 0, h, 0

for y in range(h):
    for x in range(w):
        r, g, b = pixels[x, y][:3]
        if r > 25 or g > 25 or b > 25:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

print(f"Content bbox in uploaded image: x=({min_x}, {max_x}), y=({min_y}, {max_y}), w={max_x - min_x}, h={max_y - min_y}")
