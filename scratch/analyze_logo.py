from PIL import Image

im = Image.open('static/images/logo.png')
print('Image size:', im.size)
width, height = im.size
pixels = im.load()

active_y = []
for y in range(height):
    has_pixel = any(pixels[x, y][3] > 10 for x in range(width))
    if has_pixel:
        active_y.append(y)

print('Min Y:', active_y[0], 'Max Y:', active_y[-1])

for y in range(180, 260, 5):
    count = sum(1 for x in range(width) if pixels[x, y][3] > 10)
    print(f'Row {y} active cols: {count}')
