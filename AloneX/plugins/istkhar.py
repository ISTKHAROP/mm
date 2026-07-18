# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

from pyrogram import filters, types
from AloneX import app


@app.on_message(filters.video_chat_members_invited & filters.group & ~app.bl_users)
async def _vc_invited(_, message: types.Message):
    invited = []

    for user in message.video_chat_members_invited.users:
        try:
            invited.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
        except Exception:
            pass

    if not invited:
        return

    # 🚀 NAYA: Screenshot jaisa stylish font aur emoji
    text = f"📢 {message.from_user.mention} IηvιтєD {', '.join(invited)} . Tσ Vc 😌"

    try:
        await message.reply(text)
    except Exception:
        pass
        
