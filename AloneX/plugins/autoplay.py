# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import asyncio

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AloneX import app, db, lang

DELETE_DELAY = 7

async def _delete_later(message: types.Message) -> None:
    try:
        await asyncio.sleep(DELETE_DELAY)
        await message.delete()
    except Exception:
        pass

@app.on_message(filters.command(["autoplay"]) & filters.group & ~app.bl_users)
@lang.language()
async def _autoplay(_, m: types.Message):
    mode = m.command[1].lower() if len(m.command) > 1 else None

    if mode in ("off", "disable"):
        await db.set_autoplay(m.chat.id, False)
        msg = await m.reply_text(
            m.lang.get(
                "autoplay_disabled",
                "🚫 Autoplay has been disabled.\n\nPlayback will stop once the queue is empty.",
            )
        )
        asyncio.create_task(_delete_later(msg))
        return

    if mode is not None and mode not in ("on", "enable"):
        msg = await m.reply_text(
            m.lang.get("autoplay_usage", "Usage: /autoplay [on|off]")
        )
        asyncio.create_task(_delete_later(msg))
        return

    # 🛠 FIX 1: Callback data me chat_id daal diya taaki backend samajh sake
    autoplay_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="✅ Enable", callback_data=f"set_ap_on_{m.chat.id}"),
                InlineKeyboardButton(text="❌ Disable", callback_data=f"set_ap_off_{m.chat.id}")
            ],
            [
                InlineKeyboardButton(text="🗑 Close", callback_data="close")
            ]
        ]
    )

    await m.reply_text(
        m.lang.get(
            "autoplay_panel_title",
            "🎶 <b>Autoplay:</b>\n\n"
            "• Keeps music playing automatically.\n"
            "• Ensures smooth and uninterrupted listening.\n"
            "• Designed for a seamless music experience.",
        ),
        reply_markup=autoplay_keyboard,
    )


# 🛠 FIX 2: Ye naya handler add kiya hai jo un buttons ka kaam karega
@app.on_callback_query(filters.regex(r"^set_ap_(on|off)_") & ~app.bl_users)
async def handle_autoplay_buttons(_, query: types.CallbackQuery):
    data = query.data.split("_")
    action = data[2] # Ye 'on' ya 'off' check karega
    chat_id = int(data[3])
    
    if action == "on":
        await db.set_autoplay(chat_id, True)
        status_msg = "🟢 ᴇɴᴀʙʟᴇᴅ"
        alert_msg = "Autoplay Enabled!"
    else:
        await db.set_autoplay(chat_id, False)
        status_msg = "🔴 ᴅɪsᴀʙʟᴇᴅ"
        alert_msg = "Autoplay Disabled!"

    await query.answer(alert_msg)
    
    try:
        # Group me wahi tag wala message bhejega
        await app.send_message(
            chat_id=chat_id, 
            text=f"ᴀᴜᴛᴏ-ᴘʟᴀʏ ʜᴀs ʙᴇᴇɴ {status_msg} ʙʏ {query.from_user.mention}"
        )
    except:
        pass
        
    try:
        # Kaam hone ke baad panel delete ho jayega
        await query.message.delete()
    except:
        pass
    
