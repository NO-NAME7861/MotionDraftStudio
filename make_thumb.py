"""make_thumb.py - dramatic custom thumbnail generator (CTR-optimized).

Draws: blood-moon gradient, mountain silhouette, a sword figure, huge ENGLISH text.
Run: python make_thumb.py OUT.png
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720

font_paths = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf",
              r"C:\Windows\Fonts\DejaVuSans-Bold.ttf"]
def font(size):
    for p in font_paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

# vertical gradient: wine-red at top -> near-black at bottom
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    t = y / H
    r = int(80 * (1 - t) ** 1.5 + 10 * t)
    g = int(8 * (1 - t) + 4 * t)
    b = int(16 * (1 - t) + 8 * t)
    for x in range(W):
        px[x, y] = (r, g, b)

d = ImageDraw.Draw(img, "RGBA")

# blood moon, top-right
moon_c = (W - 300, 150, 210)
for rad, alpha in [(150, 40), (120, 60), (95, 110), (78, 255)]:
    d.ellipse([moon_c[0] - rad, moon_c[1] - rad, moon_c[0] + rad, moon_c[1] + rad],
              fill=(255, 80, 60, alpha if alpha < 255 else 255))
# moon crater dots
d.ellipse([moon_c[0] - 30, moon_c[1] + 10, moon_c[0] + 20, moon_c[1] + 55], fill=(210, 60, 45))
d.ellipse([moon_c[0] + 15, moon_c[1] - 40, moon_c[0] + 45, moon_c[1] - 15], fill=(210, 60, 45))

# distant mountain silhouette
mts = [(0, 470), (130, 430), (240, 500), (360, 380), (470, 480), (610, 350),
       (740, 500), (860, 415), (980, 520), (1120, 445), (1280, 510), (1280, 720), (0, 720)]
d.polygon(mts, fill=(18, 12, 22))
mts2 = [(0, 560), (200, 500), (390, 590), (600, 505), (800, 600), (1000, 520), (1280, 590), (1280, 720), (0, 720)]
d.polygon(mts2, fill=(8, 5, 12))

# sword figure: vertical jian blade, center-right
sx = 880
# glow behind blade
d.polygon([(sx - 90, 620), (sx, 130), (sx + 90, 620)], fill=(255, 60, 40, 30))
d.polygon([(sx, 615), (sx - 26, 250), (sx, 60), (sx + 26, 250), (sx, 615)], fill=(24, 26, 40))
d.polygon([(sx, 615), (sx - 12, 250), (sx, 60), (sx + 12, 250), (sx, 615)], fill=(52, 58, 90))
# guard + grip
d.rectangle([sx - 55, 615, sx + 55, 632], fill=(28, 20, 14))
d.rectangle([sx - 14, 632, sx + 14, 730], fill=(40, 28, 20))

# text block (left)
tx = 70
d.text((tx, 80), "BETRAYED", font=font(165), fill=(255, 255, 255))
d.text((tx, 245), "BY EVERYONE.", font=font(120), fill=(255, 74, 54))
d.rectangle([tx, 395, tx + 470, 406], fill=(255, 200, 80))
d.text((tx, 425), "REBORN. RUTHLESS.", font=font(64), fill=(255, 210, 105))
d.text((tx, 512), "HINDI RECAP  |  2+ HOURS", font=font(40), fill=(235, 235, 235))

img = img.filter(ImageFilter.GaussianBlur(0.4))
out = sys.argv[1]
img.save(out, quality=95)
print("saved", out, img.size)
