import os
import math
import colorsys
import aiohttp

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageEnhance,
    ImageFont,
    ImageOps,
)

from AloneX import config
from AloneX.helpers import Track


class Thumbnail:

    def __init__(self):

        # Canvas
        self.width = 1280
        self.height = 720

        # Album Size
        self.album_size = 520
        self.radius = 42

        # Blur Strength
        self.blur = 70

        # Fonts
        self.font_title = ImageFont.truetype(
            "AloneX/helpers/Raleway-Bold.ttf",
            38,
        )

        self.font_artist = ImageFont.truetype(
            "AloneX/helpers/Inter-Light.ttf",
            27,
        )

        self.font_small = ImageFont.truetype(
            "AloneX/helpers/Inter-Light.ttf",
            22,
        )

        self.font_time = ImageFont.truetype(
            "AloneX/helpers/Inter-Light.ttf",
            20,
        )

        # UI Colors
        self.white = (255,255,255,255)
        self.gray = (190,190,190,255)
        self.light = (230,230,230,255)

        self.glass = (255,255,255,55)
        self.shadow = (0,0,0,170)

        self.progress = self.white

        self.control_size = 62

        self.cache = "cache"

        os.makedirs(self.cache, exist_ok=True)
        # ---------------- DOWNLOAD ----------------

    async def save_thumb(
        self,
        output_path: str,
        url: str,
    ) -> str:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:

                if resp.status != 200:
                    return config.DEFAULT_THUMB

                with open(output_path, "wb") as f:
                    f.write(await resp.read())

        return output_path


    # ---------------- TEXT ----------------

    def trim_text(
        self,
        text,
        font,
        width,
    ):

        if font.getlength(text) <= width:
            return text

        dots = "..."

        while font.getlength(text + dots) > width:

            text = text[:-1]

            if not text:
                break

        return text + dots


    # ---------------- DOMINANT COLOR ----------------

    def get_dominant_color(
        self,
        image,
    ):

        img = image.copy()

        img.thumbnail((80,80))

        colors = img.convert("RGB").getcolors(80*80)

        if not colors:
            return (80,80,80)

        colors.sort(reverse=True)

        r,g,b = colors[0][1]

        h,l,s = colorsys.rgb_to_hls(
            r/255,
            g/255,
            b/255,
        )

        l = max(0.35, l)

        r,g,b = colorsys.hls_to_rgb(
            h,
            l,
            s,
        )

        return (
            int(r*255),
            int(g*255),
            int(b*255),
        )


    # ---------------- ROUND IMAGE ----------------

    def round_image(
        self,
        img,
        radius,
    ):

        mask = Image.new(
            "L",
            img.size,
            0,
        )

        d = ImageDraw.Draw(mask)

        d.rounded_rectangle(
            (0,0,*img.size),
            radius=radius,
            fill=255,
        )

        out = Image.new(
            "RGBA",
            img.size,
        )

        out.paste(
            img,
            (0,0),
            mask,
        )

        return out


    # ---------------- SHADOW ----------------

    def create_shadow(
        self,
        size,
        radius=40,
        blur=30,
    ):

        w,h = size

        shadow = Image.new(
            "RGBA",
            (
                w+blur*2,
                h+blur*2,
            ),
            (0,0,0,0),
        )

        d = ImageDraw.Draw(shadow)

        d.rounded_rectangle(
            (
                blur,
                blur,
                blur+w,
                blur+h,
            ),
            radius=radius,
            fill=(0,0,0,190),
        )

        shadow = shadow.filter(
            ImageFilter.GaussianBlur(blur)
        )

        return shadow
        # ---------------- GLASS PANEL ----------------

    def glass_panel(
        self,
        size,
        radius=36,
        color=(255,255,255,35),
        border=(255,255,255,70),
    ):

        w, h = size

        panel = Image.new(
            "RGBA",
            (w, h),
            (0,0,0,0),
        )

        d = ImageDraw.Draw(panel)

        d.rounded_rectangle(
            (0,0,w,h),
            radius=radius,
            fill=color,
            outline=border,
            width=2,
        )

        return panel


    # ---------------- VIGNETTE ----------------

    def create_vignette(self):

        layer = Image.new(
            "L",
            (self.width, self.height),
            0,
        )

        draw = ImageDraw.Draw(layer)

        for i in range(350):

            alpha = int(i * 0.45)

            draw.rounded_rectangle(
                (
                    -i,
                    -i,
                    self.width+i,
                    self.height+i,
                ),
                radius=120,
                outline=alpha,
                width=2,
            )

        return layer


    # ---------------- BACKGROUND ----------------

    def create_background(
        self,
        image,
    ):

        bg = image.resize(
            (self.width, self.height),
            Image.Resampling.LANCZOS,
        )

        bg = bg.filter(
            ImageFilter.GaussianBlur(
                self.blur
            )
        )

        bg = ImageEnhance.Brightness(
            bg
        ).enhance(
            0.35
        )

        bg = ImageEnhance.Contrast(
            bg
        ).enhance(
            1.18
        )

        return bg.convert("RGBA")


    # ---------------- GLOW ----------------

    def glow(
        self,
        size,
        color,
        blur=120,
    ):

        w, h = size

        layer = Image.new(
            "RGBA",
            (w,h),
            (0,0,0,0),
        )

        d = ImageDraw.Draw(layer)

        d.ellipse(
            (
                0,
                0,
                w,
                h,
            ),
            fill=color,
        )

        return layer.filter(
            ImageFilter.GaussianBlur(
                blur
            )
        )
        # ---------- PREMIUM BACKGROUND ----------

bg = self.create_background(img)

accent = self.get_dominant_color(img)

# Glow Behind Album
glow = self.glow(
    (700,700),
    (
        accent[0],
        accent[1],
        accent[2],
        110,
    ),
)

bg.alpha_composite(
    glow,
    (-30,15),
)

# Glass Card
panel = self.glass_panel(
    (1120,620),
    radius=42,
)

bg.alpha_composite(
    panel,
    (80,50),
)

# Album Shadow
shadow = self.create_shadow(
    (
        self.album_size,
        self.album_size,
    ),
    radius=42,
    blur=40,
)

album_x = 120
album_y = 100

bg.alpha_composite(
    shadow,
    (
        album_x-40,
        album_y-40,
    ),
)

# Album Cover
album = img.resize(
    (
        self.album_size,
        self.album_size,
    ),
    Image.Resampling.LANCZOS,
)

album = self.round_image(
    album,
    self.radius,
)

bg.alpha_composite(
    album,
    (
        album_x,
        album_y,
    ),
)

overlay = Image.new(
    "RGBA",
    bg.size,
    (0,0,0,0),
)

draw = ImageDraw.Draw(overlay)
# ---------------- TEXT ----------------

text_x = 720
top_y = 125
right_edge = 1160

title = self.trim_text(
    song.title,
    self.font_title,
    360,
)

artist = self.trim_text(
    song.channel_name,
    self.font_artist,
    360,
)

draw.text(
    (text_x, top_y),
    title,
    font=self.font_title,
    fill=self.white,
)

draw.text(
    (text_x, top_y + 52),
    artist,
    font=self.font_artist,
    fill=(210,210,210,255),
)

# ---------------- STAR ----------------

star_x = 1070
star_y = 145

draw.ellipse(
    (
        star_x-26,
        star_y-26,
        star_x+26,
        star_y+26,
    ),
    fill=(255,255,255,40),
)

self.draw_star(
    draw,
    (star_x, star_y),
    12,
)

# ---------------- MENU ----------------

menu_x = 1142
menu_y = 145

draw.ellipse(
    (
        menu_x-26,
        menu_y-26,
        menu_x+26,
        menu_y+26,
    ),
    fill=(255,255,255,55),
)

self.draw_dots_menu(
    draw,
    (menu_x,menu_y),
    26,
)

# ---------------- PROGRESS ----------------

bar_x = text_x
bar_y = 232
bar_w = 440

draw.rounded_rectangle(
    (
        bar_x,
        bar_y-4,
        bar_x+bar_w,
        bar_y+4,
    ),
    radius=4,
    fill=(255,255,255,90),
)

progress = 0.03

fill_w = int(bar_w * progress)

draw.rounded_rectangle(
    (
        bar_x,
        bar_y-4,
        bar_x+fill_w,
        bar_y+4,
    ),
    radius=4,
    fill=accent,
)

draw.ellipse(
    (
        bar_x+fill_w-8,
        bar_y-8,
        bar_x+fill_w+8,
        bar_y+8,
    ),
    fill=self.white,
)

draw.text(
    (bar_x,255),
    "0:03",
    font=self.font_time,
    fill=(220,220,220,255),
)

duration = f"-{song.duration}"

draw.text(
    (
        bar_x + bar_w - self.font_time.getlength(duration),
        255,
    ),
    duration,
    font=self.font_time,
    fill=(220,220,220,255),
)
# ---------------- PLAYER CONTROLS ----------------

controls_y = 385
center_x = 940

prev = (center_x - 160, controls_y)
play = (center_x, controls_y)
next_ = (center_x + 160, controls_y)

# Previous
self.draw_skip_icon(
    draw,
    prev,
    60,
    forward=False,
)

# Play Circle
draw.ellipse(
    (
        play[0]-34,
        play[1]-34,
        play[0]+34,
        play[1]+34,
    ),
    fill=self.white,
)

# Pause
self.draw_pause_bars(
    draw,
    play,
    32,
)

# Next
self.draw_skip_icon(
    draw,
    next_,
    60,
    forward=True,
)

# ---------------- VOLUME ----------------

vol_y = 500

self.draw_speaker(
    draw,
    (720, vol_y),
    28,
    loud=False,
)

draw.rounded_rectangle(
    (
        775,
        vol_y-5,
        1105,
        vol_y+5,
    ),
    radius=5,
    fill=(255,255,255,120),
)

draw.rounded_rectangle(
    (
        775,
        vol_y-5,
        1015,
        vol_y+5,
    ),
    radius=5,
    fill=accent,
)

draw.ellipse(
    (
        1008,
        vol_y-9,
        1026,
        vol_y+9,
    ),
    fill=self.white,
)

self.draw_speaker(
    draw,
    (1125, vol_y),
    28,
    loud=True,
)

# ---------------- BOTTOM ICONS ----------------

icons_y = 585

self.draw_quote_bubble(
    draw,
    (835, icons_y),
    36,
)

self.draw_list_icon(
    draw,
    (1045, icons_y),
    36,
)

# ---------------- FINAL RENDER ----------------

bg = Image.alpha_composite(bg, overlay)

vignette = self.create_vignette()
bg.putalpha(vignette)

bg = bg.convert("RGB")

bg.save(
    output,
    quality=100,
    optimize=True,
)

try:
    os.remove(temp)
except:
    pass

return output
