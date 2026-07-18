# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import time
import psutil
import random  # 🚀 NAYA: Random photo select karne ke liye

from pyrogram import filters, types
from AloneX import app, anon, boot, config, lang
from AloneX.helpers import buttons


@app.on_message(filters.command(["alive", "ping"]) & ~app.bl_users)
@lang.language()
async def _ping(_, m: types.Message):
    start = time.time()
    sent = await m.reply_text(m.lang["pinging"])
    
    get_time = lambda s: (lambda r: (f"{r[-1]}, " if r[-1][:-4] != "0" else "") + ":".join(reversed(r[:-1])))([f"{v}{u}" for v, u in zip([s%60, (s//60)%60, (s//3600)%24, s//86400], ["s", "m", "h", "days"])])
    uptime = get_time(int(time.time() - boot))
    latency = round((time.time() - start) * 1000, 2)
    
    # 🚀 FIX: List me se ek random photo uthana
    # Agar config me list di hai toh random chunega, nahi toh single image utha lega
    if isinstance(config.PING_IMG_URL, list):
        ping_photo = random.choice(config.PING_IMG_URL)
    else:
        ping_photo = config.PING_IMG

    await sent.edit_media(
        media=types.InputMediaPhoto(
            media=ping_photo,  # 🚀 NAYA: Random photo yahan lagayi
            caption=m.lang["ping_pong"].format(
                latency,
                uptime,
                psutil.cpu_percent(interval=0),
                psutil.virtual_memory().percent,
                psutil.disk_usage("/").percent,
                await anon.ping(),
            )
        ),
        reply_markup=buttons.ping_markup(m.lang["support"]),
    )
    
