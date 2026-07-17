# Copyright (c) 2025 TheHamkerAlone 
# Licensed under the MIT License.
# This file is part of AloneX

import os
import asyncio
import numpy as np
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from collections import Counter

from AloneX import config
from AloneX.helpers import Track

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(text):
        return text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_TITLE_PATH = os.path.join(BASE_DIR, "font.ttf")
FONT_INFO_PATH = os.path.join(BASE_DIR, "font2.ttf")
TEMPLATE_PATH = os.path.join(BASE_DIR, "..", "assets", "template.png")

def safe_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

class Thumbnail:
    def __init__(self):
        self.size = (1280, 720)
        # 🛠 FIX: Fonts ko bada kiya hai premium look ke liye
        self.font_title = safe_font(FONT_TITLE_PATH, 42)
        self.font_info = safe_font(FONT_INFO_PATH, 30)
        self.font_time = safe_font(FONT_INFO_PATH, 22)

    async def start(self):
        os.makedirs("cache", exist_ok=True)
        return True

    async def save_thumb(self, output_path: str, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        for attempt in range(3):
            try:
                if url.startswith("http"):
                    async with aiohttp.ClientSession(headers=headers) as session:
                        async with session.get(url, timeout=15) as resp:
                            if resp.status == 200:
                                content = await resp.read()
                                with open(output_path, "wb") as f:
                                    f.write(content)
                                return output_path
            except Exception as e:
                await asyncio.sleep(1)
        return output_path

    async def generate(self, song: Track) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            temp = f"cache/temp_{song.id}.jpg"
            final_path = f"cache/{song.id}.png"
            if os.path.exists(final_path):
                return final_path

            await self.save_thumb(temp, song.thumbnail)
            
            try:
                src = Image.open(temp).convert("RGBA")
            except Exception:
                src = Image.new("RGBA", (1280, 720), (30, 30, 30, 255))

            W, H = self.size

            # 1. BLURRED BACKGROUND 
            bg_ratio = W / H
            src_ratio = src.width / src.height
            if src_ratio > bg_ratio:
                new_w = int(src.height * bg_ratio)
                offset = (src.width - new_w) // 2
                bg = src.crop((offset, 0, offset + new_w, src.height))
            else:
                new_h = int(src.width / bg_ratio)
                offset = (src.height - new_h) // 2
                bg = src.crop((0, offset, src.width, offset + new_h))

            bg = bg.resize((W, H), Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(30))
            bg_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160)) # Darker for UI visibility
            bg = Image.alpha_composite(bg, bg_overlay)

            # 2. PASTE COVER ART
            cover_x, cover_y = 80, 80
            cover_w, cover_h = 560, 560
            cover_radius = 45

            # Shadow
            shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.rounded_rectangle(
                (cover_x + 10, cover_y + 15, cover_x + cover_w + 10, cover_y + cover_h + 15),
                radius=cover_radius,
                fill=(0, 0, 0, 150),
            )
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(25))
            bg = Image.alpha_composite(bg, shadow_layer)

            # Cover Image
            cover_resized = src.resize((cover_w, cover_h), Image.Resampling.LANCZOS)
            cover_mask = Image.new("L", (cover_w, cover_h), 0)
            ImageDraw.Draw(cover_mask).rounded_rectangle(
                (0, 0, cover_w, cover_h), radius=cover_radius, fill=255
            )
            bg.paste(cover_resized, (cover_x, cover_y), cover_mask)

            # 3. DRAW PLAYER UI (Text, Progress Bar, Buttons)
            draw = ImageDraw.Draw(bg)
            
            # --- TEXT ---
            text_x = 710
            text_max_w = 500

            def ellipsize(s, font, max_w):
                if draw.textbbox((0, 0), s, font=font)[2] <= max_w:
                    return s
                lo, hi = 1, len(s)
                best = "…"
                while lo <= hi:
                    mid = (lo + hi) // 2
                    cand = s[:mid].rstrip() + "…"
                    if draw.textbbox((0, 0), cand, font=font)[2] <= max_w:
                        best = cand
                        lo = mid + 1
                    else:
                        hi = mid - 1
                return best

            title_str = ellipsize(unidecode(str(song.title)), self.font_title, text_max_w)
            draw.text((text_x, 150), title_str, fill="white", font=self.font_title)

            artist_str = ellipsize(unidecode(str(song.channel_name)), self.font_info, text_max_w)
            draw.text((text_x, 210), artist_str, fill=(180, 180, 180, 255), font=self.font_info)

            # --- PROGRESS BAR ---
            bar_x = 710
            bar_y = 350
            bar_w = 480
            bar_h = 8
            
            # Dark Base Line
            draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=4, fill=(100, 100, 100, 255))
            
            # White Progress Line (Fixed 25% for aesthetic)
            fill_w = int(bar_w * 0.25)
            draw.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + bar_h), radius=4, fill="white")
            
            # Knob Circle
            circle_r = 12
            cx, cy = bar_x + fill_w, bar_y + (bar_h // 2)
            draw.ellipse((cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r), fill="white")

            # --- TIMER TEXT ---
            draw.text((bar_x, bar_y + 25), "0:00", fill=(200, 200, 200, 255), font=self.font_time)
            duration_str = str(getattr(song, "duration", "0:00"))
            dur_w = draw.textbbox((0, 0), duration_str, font=self.font_time)[2]
            draw.text((bar_x + bar_w - dur_w, bar_y + 25), f"-{duration_str}", fill=(200, 200, 200, 255), font=self.font_time)

            # --- CONTROL BUTTONS ---
            btn_y = 480
            center_x = bar_x + (bar_w // 2)

            # 1. Pause Button (Center)
            draw.rounded_rectangle((center_x - 16, btn_y, center_x - 6, btn_y + 40), radius=3, fill="white")
            draw.rounded_rectangle((center_x + 6, btn_y, center_x + 16, btn_y + 40), radius=3, fill="white")

            # 2. Previous Button (Left)
            prev_x = center_x - 130
            draw.polygon([(prev_x, btn_y + 20), (prev_x + 25, btn_y + 5), (prev_x + 25, btn_y + 35)], fill="white")
            draw.polygon([(prev_x + 25, btn_y + 20), (prev_x + 50, btn_y + 5), (prev_x + 50, btn_y + 35)], fill="white")

            # 3. Next Button (Right)
            next_x = center_x + 80
            draw.polygon([(next_x + 25, btn_y + 20), (next_x, btn_y + 5), (next_x, btn_y + 35)], fill="white")
            draw.polygon([(next_x + 50, btn_y + 20), (next_x + 25, btn_y + 5), (next_x + 25, btn_y + 35)], fill="white")
            
            out = bg.convert("RGB")
            out.save(final_path, "PNG")

            try:
                if os.path.exists(temp):
                    os.remove(temp)
            except Exception:
                pass

            return final_path

        except Exception as e:
            print(f"Error: {e}")
            return config.DEFAULT_THUMB
            
