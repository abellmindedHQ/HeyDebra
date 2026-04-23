#!/usr/bin/env python3
"""Compose a 300x250 LEGO Desk Organizers display ad."""

from PIL import Image, ImageDraw, ImageFont
import os

# --- Config ---
WIDTH, HEIGHT = 300, 250
LEGO_RED = "#D11013"
LEGO_YELLOW = "#F6EC35"
WHITE = "#FFFFFF"
BLACK = "#000000"
DARK_GRAY = "#333333"

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
HERO_IMAGE = "/Users/debra/.openclaw/media/tool-image-generation/image-1---89d1f27a-8e91-47c6-9d91-ffcbf8d8e988.jpg"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "lego-desk-organizer-ad-300x250.png")

# --- Fonts ---
def load_font(style="Bold", size=20):
    paths = [
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        try:
            # Avenir Next Bold is index 7, Heavy is index 11, Demi Bold is index 3, Regular is index 0
            if "Avenir" in p:
                if style == "Heavy":
                    return ImageFont.truetype(p, size, index=10)
                elif style == "Bold":
                    return ImageFont.truetype(p, size, index=6)
                elif style == "DemiBold":
                    return ImageFont.truetype(p, size, index=2)
                elif style == "Medium":
                    return ImageFont.truetype(p, size, index=4)
                else:
                    return ImageFont.truetype(p, size, index=0)
            else:
                return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

# --- Create canvas ---
canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
draw = ImageDraw.Draw(canvas)

# --- Layout Plan ---
# Top bar: LEGO yellow strip (thin, 4px)
# Headline area: top ~55px (white bg, dark text)
# Hero image: middle ~140px
# CTA bar: bottom ~45px (LEGO red bg, white text)
# LEGO logo text: small, bottom-right corner on the red bar

TOP_BAR_H = 6
HEADLINE_H = 50
IMAGE_H = 148
CTA_H = 46

# --- Top yellow accent bar ---
draw.rectangle([0, 0, WIDTH, TOP_BAR_H], fill=LEGO_YELLOW)

# --- Headline ---
headline_font = load_font("Heavy", 17)
subline_font = load_font("Medium", 10)

headline_text = "Your Desk. Your Build."
subline_text = "New LEGO® Desk Organizers"

# Center headline
headline_bbox = draw.textbbox((0, 0), headline_text, font=headline_font)
headline_w = headline_bbox[2] - headline_bbox[0]
headline_x = (WIDTH - headline_w) // 2
headline_y = TOP_BAR_H + 10

draw.text((headline_x, headline_y), headline_text, fill=DARK_GRAY, font=headline_font)

# Subline
subline_bbox = draw.textbbox((0, 0), subline_text, font=subline_font)
subline_w = subline_bbox[2] - subline_bbox[0]
subline_x = (WIDTH - subline_w) // 2
subline_y = headline_y + (headline_bbox[3] - headline_bbox[1]) + 4

draw.text((subline_x, subline_y), subline_text, fill="#666666", font=subline_font)

# --- Hero Image ---
img_y_start = TOP_BAR_H + HEADLINE_H
img_y_end = img_y_start + IMAGE_H

hero = Image.open(HERO_IMAGE)
# Crop to landscape ratio for the 300xIMAGE_H area
hero_w, hero_h = hero.size
target_ratio = WIDTH / IMAGE_H
hero_ratio = hero_w / hero_h

if hero_ratio > target_ratio:
    # Wider than needed, crop sides
    new_w = int(hero_h * target_ratio)
    left = (hero_w - new_w) // 2
    hero = hero.crop((left, 0, left + new_w, hero_h))
else:
    # Taller than needed, crop top/bottom
    new_h = int(hero_w / target_ratio)
    top = (hero_h - new_h) // 2
    hero = hero.crop((0, top, hero_w, top + new_h))

hero = hero.resize((WIDTH, IMAGE_H), Image.LANCZOS)
canvas.paste(hero, (0, img_y_start))

# --- CTA Bar ---
cta_y = img_y_end
draw.rectangle([0, cta_y, WIDTH, HEIGHT], fill=LEGO_RED)

# CTA button text
cta_font = load_font("Bold", 14)
cta_text = "Start Building"

cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
cta_text_w = cta_bbox[2] - cta_bbox[0]
cta_text_h = cta_bbox[3] - cta_bbox[1]

# Draw a white rounded-rect button
btn_padding_x = 16
btn_padding_y = 6
btn_w = cta_text_w + btn_padding_x * 2
btn_h = cta_text_h + btn_padding_y * 2
btn_x = (WIDTH // 2) - btn_w // 2 - 30  # Offset left to make room for logo
btn_y = cta_y + (CTA_H - btn_h) // 2

# Rounded rect button
draw.rounded_rectangle(
    [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
    radius=4,
    fill=WHITE
)
draw.text(
    (btn_x + btn_padding_x, btn_y + btn_padding_y - 1),
    cta_text,
    fill=LEGO_RED,
    font=cta_font
)

# LEGO wordmark (small, bottom-right)
logo_font = load_font("Heavy", 16)
logo_text = "LEGO"
logo_bbox = draw.textbbox((0, 0), logo_text, font=logo_font)
logo_w = logo_bbox[2] - logo_bbox[0]
logo_x = WIDTH - logo_w - 12
logo_y = cta_y + (CTA_H - (logo_bbox[3] - logo_bbox[1])) // 2

# Draw a small yellow-outlined box behind LEGO text
lego_box_pad = 4
lego_box = [
    logo_x - lego_box_pad - 2,
    logo_y - lego_box_pad,
    logo_x + logo_w + lego_box_pad + 2,
    logo_y + (logo_bbox[3] - logo_bbox[1]) + lego_box_pad
]
draw.rounded_rectangle(lego_box, radius=3, fill=LEGO_YELLOW, outline=BLACK, width=1)
draw.text((logo_x, logo_y), logo_text, fill=LEGO_RED, font=logo_font)

# --- Thin black border around the entire ad (standard for display ads) ---
draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline="#CCCCCC", width=1)

# --- Save ---
canvas.save(OUTPUT_PATH, "PNG")
print(f"Ad saved to: {OUTPUT_PATH}")
print(f"Size: {canvas.size}")
