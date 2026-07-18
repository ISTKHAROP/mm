# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import os
import platform
import sys
import random  # 🚀 NAYA: Random photo select karne ke liye

import psutil
from pyrogram import __version__, filters, types
from pytgcalls import __version__ as pytgver

from AloneX import app, config, db, lang, userbot
from AloneX.plugins import all_modules


@app.on_message(filters.command(["stats"]) & filters.group & ~app.bl_users)
@lang.language()
async def _stats(_, m: types.Message):
    # 🚀 FIX: List me se ek random photo uthana
    if hasattr(config, "STATS_IMG_URL") and isinstance(config.STATS_IMG_URL, list):
        stats_photo = random.choice(config.STATS_IMG_URL)
    elif isinstance(config.PING_IMG, list):
        stats_photo = random.choice(config.PING_IMG)
    else:
        stats_photo = config.PING_IMG

    sent = await m.reply_photo(
        photo=stats_photo,  # 🚀 NAYA: Random photo yahan lagayi
        caption=m.lang["stats_fetching"],
    )

    pid = os.getpid()
    _utext = m.lang["stats_user"].format(
        app.name,
        len(userbot.clients),
        config.AUTO_LEAVE,
        len(db.blacklisted),
        len(app.bl_users),
        len(app.sudoers),
        len(await db.get_chats()),
        len(await db.get_users()),
    )
    if m.from_user.id in app.sudoers:
        process = psutil.Process(pid)
        storage = psutil.disk_usage("/")
        _utext += m.lang["stats_sudo"].format(
            len(all_modules),
            platform.system(),
            f"{process.memory_info().rss / 1024**2:.2f}",
            round(psutil.virtual_memory().total / (1024.0**3)),
            process.cpu_percent(interval=1.0),
            psutil.cpu_count(logical=False),
            f"{storage.used / (1024.0**3):.2f}",
            f"{storage.total / (1024.0**3):.2f}",
            sys.version.split()[0],
            __version__,
            pytgver,
        )
    await sent.edit_caption(_utext)
    
