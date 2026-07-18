# Copyright (c) 2026 THE SHIV
# Licensed under the MIT License.
# This file is part of MahiMusic
# DEVELOPER - THE SHIV

import os
import asyncio

from pyrogram import filters, types, enums
from pyrogram.errors import FloodWait

from AloneX import app, db, lang, queue

# Safe import for userbot to count assistant groups
try:
    from AloneX import userbot
except ImportError:
    userbot = None


# ==========================================
# 🟢 OLD ACTIVE VC COMMAND (UNTOUCHED)
# ==========================================
@app.on_message(filters.command(["ac", "activevc"]) & app.sudoers)
@lang.language()
async def _activevc(_, m: types.Message):
    if not db.active_calls:
        return await m.reply_text(m.lang["vc_empty"])

    if m.command[0] == "ac":
        return await m.reply_text(m.lang["vc_count"].format(len(db.active_calls)))

    sent = await m.reply_text(m.lang["vc_fetching"])
    text = ""

    for i, chat in enumerate(db.active_calls):
        playing = queue.get_current(chat)
        text += f"\n{i+1}. <code>{chat}</code>\n  ➜ {playing.title[:25]}"

    if len(text) < 4000:
        return await sent.edit_text(m.lang["vc_list"] + text)

    with open("activevc.txt", "w") as f:
        f.write(text)
    await sent.edit_media(
        media=types.InputMediaDocument(
            media="activevc.txt",
            caption=m.lang["vc_list"],
        )
    )
    os.remove("activevc.txt")


# ==========================================
# 🆕 /tvc - TOTAL VC WITH INVITE LINKS
# ==========================================
@app.on_message(filters.command(["tvc"]) & app.sudoers)
async def _tvc(_, m: types.Message):
    if not db.active_calls:
        return await m.reply_text("<blockquote><b>❌ ᴋᴏɪ ʙʜɪ ᴠᴏɪᴄᴇ ʏᴀ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴀᴄᴛɪᴠᴇ ɴᴀʜɪ ʜᴀɪ.</b></blockquote>")
        
    sent = await m.reply_text("<blockquote><b>⏳ ꜰᴇᴛᴄʜɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠᴄ/ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴅᴀᴛᴀ... (ᴍᴀʏ ᴛᴀᴋᴇ ᴛɪᴍᴇ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs)</b></blockquote>")
    
    text = f"<blockquote><b>🎵 ᴛᴏᴛᴀʟ ᴀᴄᴛɪᴠᴇ ᴠᴄ / ᴠɪᴅᴇᴏ ᴄʜᴀᴛs : {len(db.active_calls)}</b>\n\n"
    
    for i, chat_id in enumerate(db.active_calls):
        playing = queue.get_current(chat_id)
        title = playing.title[:25] if playing else "Unknown Track"
        
        # Try to get public link or generate private invite link
        try:
            chat = await app.get_chat(chat_id)
            if chat.username:
                chat_link = f"https://t.me/{chat.username}"
            else:
                # Uses existing invite link if available, otherwise generates a new one
                chat_link = chat.invite_link or await app.export_chat_invite_link(chat_id)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            chat_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}/1"
        except Exception:
            # Fallback if bot is not admin or lacks "Invite Users" permission
            chat_link = f"https://t.me/c/{str(chat_id).replace('-100', '')}/1"
            
        text += f"<b>{i+1}. ᴄʜᴀᴛ ɪᴅ :</b> <code>{chat_id}</code>\n"
        text += f"<b>🔗 ᴄʜᴀᴛ ʟɪɴᴋ :</b> <a href='{chat_link}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ</a>\n"
        text += f"<b>🎧 ᴘʟᴀʏɪɴɢ :</b> {title}\n\n"
        
    text += "</blockquote>"

    if len(text) < 4000:
        return await sent.edit_text(text, disable_web_page_preview=True)
        
    # File fallback if list is too huge
    with open("tvc_data.txt", "w", encoding="utf-8") as f:
        clean_text = text.replace("<blockquote>", "").replace("</blockquote>", "").replace("<b>", "").replace("</b>", "").replace("<a href='", "").replace("'>ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ</a>", "")
        f.write("TOTAL ACTIVE VOICE CHATS DATA\n\n" + clean_text)
        
    await sent.edit_media(
        media=types.InputMediaDocument(
            media="tvc_data.txt",
            caption="<blockquote><b>🎵 ᴛᴏᴛᴀʟ ᴀᴄᴛɪᴠᴇ ᴠᴄ ʟɪsᴛ</b></blockquote>"
        )
    )
    os.remove("tvc_data.txt")


# ==========================================
# 🆕 /bdata - BOT & ASSISTANT GROUPS COUNT (FIXED)
# ==========================================
@app.on_message(filters.command(["bdata"]) & app.sudoers)
async def _bdata(_, m: types.Message):
    sent = await m.reply_text("<blockquote><b>⏳ ꜰᴇᴛᴄʜɪɴɢ ʙᴏᴛ & ᴀssɪsᴛᴀɴᴛ ᴅᴀᴛᴀ...</b></blockquote>")
    
    # 1. Instant Data Fetching from Database (Avoids Telegram Limit)
    try:
        total_chats_list = await db.get_chats()
        bot_groups = len(total_chats_list)
    except Exception:
        bot_groups = "Error fetching"

    try:
        total_users_list = await db.get_users()
        total_users = len(total_users_list)
    except Exception:
        total_users = "Error fetching"

    # 2. Assistant Data Fetching (Userbot Dialogs)
    ass_groups = 0
    if userbot:
        try:
            client = getattr(userbot, 'one', None)
            if client:
                async for dialog in client.get_dialogs():
                    if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                        ass_groups += 1
        except Exception:
            ass_groups = "Error fetching"
    else:
        ass_groups = "Not imported"

    # 3. Final Text Formatting
    text = (
        "<blockquote><b>📊 ᴍᴀʜɪ ᴍᴜsɪᴄ sᴛᴀᴛɪsᴛɪᴄs</b>\n\n"
        f"<b>🤖 ᴛᴏᴛᴀʟ ʙᴏᴛ ɢʀᴏᴜᴘs :</b> {bot_groups}\n\n"
        f"<b>👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs :</b> {total_users}\n\n"
        f"<b>👤 ᴀssɪsᴛᴀɴᴛ ɪɴ ɢʀᴏᴜᴘs :</b> {ass_groups}</blockquote>"
    )
    
    await sent.edit_text(text)


# ==========================================
# 🆕 /tdata - TODAY'S ADD/REMOVE & USER STATS (FIXED)
# ==========================================
@app.on_message(filters.command(["tdata"]) & app.sudoers)
async def _tdata(_, m: types.Message):
    try:
        added = await db.get_today_added_count()
        removed = await db.get_today_removed_count()
        # FIX: Puraana function call galat tha, db.py me 'new_users' wala function hai
        today_users = await db.get_today_new_users_count()
    except AttributeError:
        # Fallback agar MongoDB wale functions abhi db.py me nahi dale gaye
        added = "DB Setup Required"
        removed = "DB Setup Required"
        today_users = "DB Setup Required"

    text = (
        "<blockquote><b>📈 ᴛᴏᴅᴀʏ's ᴀᴄᴛɪᴠɪᴛʏ sᴛᴀᴛs</b>\n\n"
        f"<b>👤 ᴛᴏᴅᴀʏ ɴᴇᴡ ᴜsᴇʀs :</b> {today_users}\n\n"
        f"<b>✅ ᴀᴅᴅᴇᴅ ɪɴ ɢʀᴏᴜᴘs ᴛᴏᴅᴀʏ :</b> {added}\n"
        f"<b>❌ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ɢʀᴏᴜᴘs ᴛᴏᴅᴀʏ :</b> {removed}</blockquote>"
    )
    
    await m.reply_text(text)
