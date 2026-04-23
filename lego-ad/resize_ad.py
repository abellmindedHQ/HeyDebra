#!/usr/bin/env python3
"""Resize AI-generated ad to exact 300x250."""
from PIL import Image

src = "/Users/debra/.openclaw/media/tool-image-generation/image-1---251a0100-131e-443e-b02a-9742ab3b7b5c.jpg"
dst = "/Users/debra/.openclaw/media/lego-desk-organizer-ad-300x250-v2.png"

img = Image.open(src)
w, h = img.size

# Target: 300x250 (6:5 ratio)
target_ratio = 300 / 250
img_ratio = w / h

if img_ratio > target_ratio:
    new_w = int(h * target_ratio)
    left = (w - new_w) // 2
    img = img.crop((left, 0, left + new_w, h))
else:
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    img = img.crop((0, top, w, top + new_h))

img = img.resize((300, 250), Image.LANCZOS)
img.save(dst, "PNG")
print(f"Saved: {dst} ({img.size})")
