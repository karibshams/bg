from PIL import Image

im = Image.open('static/images/logo.png')
# Dimensions: 660, 535
# Let's find exact bounding boxes of the kite and the wordmark
width, height = im.size
pixels = im.load()

# The wordmark top horizontal line is around y=320-330
# Let's inspect where the wordmark starts and where kite ends
for y in range(200, 360, 10):
    row_pix = [x for x in range(width) if pixels[x, y][3] > 20]
    if row_pix:
        print(f"y={y}: count={len(row_pix)}, min_x={min(row_pix)}, max_x={max(row_pix)}")
