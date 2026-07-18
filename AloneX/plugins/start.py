# Copyright (c) 2026 THE SHIV
# Licensed under the MIT License.
# This file is part of MahiMusic
# DEVELOPER - THE SHIV

import asyncio
import random  # 🚀 NAYA: Random image aur sticker ke liye

from pyrogram import enums, filters, types

from AloneX import app, config, db, lang
from AloneX.helpers import buttons, utils

# 🚀 NAYA: Corrected Sticker IDs (Asli CAAC... wali IDs)
STICKERS = [
    "CAACAgQAAxkBAAEsbVNqWkrdZiNbRMTBVOvFWMlcm-1JdgACBBIAAvAG2VFd6aEJ0tmFXD0E",
    "CAACAgUAAxkBAAEsc99qWw7kf2WcJgsQ8t9mug8D3fTCtQACYQ4AAkQx-FeQjuuRGirFkz0E",
    "CAACAgUAAxkBAAEsc-FqWw7oTt2gcE26PzrVTHrZ5zrt1wACuw8AAqcd8Vd2mW2OG9DEjj0E",
    "CAACAgUAAxkBAAEsc-NqWw7vKJL_56XKpJFJTCT6wVGglAAC7g4AAr738VcdpYIvWb9n8z0E",
    "CAACAgUAAxkBAAEsc-VqWw7xTE8LY39iaHGImUI5CM4wZwACjQ4AAiYD8FdtHIaCSmINiT0E",
    "CAACAgUAAxkBAAEsc-dqWw8AAZ0yTxGiv5sRryDfEnIlTBoAApkMAAKLjvFXboDaGOc_Bn89BA",
    "CAACAgUAAxkBAAEsc-tqWw8OIg0beAH07AABoJ6BHww5MwADPhAAApxICFZBwhdixevHXj0E"
]


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    private = message.chat.type == enums.ChatType.PRIVATE

    # --- LOADING ANIMATION SEQUENCE FOR PRIVATE CHAT ---
    if private:
        # 🚀 FIX: Safety shield ke sath random sticker lagaya
        try:
            await message.reply_sticker(random.choice(STICKERS))
        except Exception:
            pass
        
        # API FloodWait se bachne aur animation fast karne ke liye steps optimize kiye hain
        baby = await message.reply_text("ᴅɪηɢ ᴅᴏηɢ.🥀")
        await asyncio.sleep(0.1)
        await baby.edit_text("ᴅɪηɢ ᴅᴏηɢ...🥀")
        await asyncio.sleep(0.1)
        await baby.edit_text("ᴅɪηɢ ᴅᴏηɢ.....🥀")
        await asyncio.sleep(0.1)

        await baby.edit_text("sᴛᴧʀᴛɪηɢ.❤️‍🔥")
        await asyncio.sleep(0.1)
        await baby.edit_text("sᴛᴧʀᴛɪηɢ...❤️‍🔥")
        await asyncio.sleep(0.1)
        await baby.edit_text("sᴛᴧʀᴛɪηɢ.....❤️‍🔥")
        await asyncio.sleep(0.1)

        await baby.edit_text("ʙσᴛ sᴛᴧʀᴛєᴅ..💤")
        await asyncio.sleep(0.1)
        await baby.edit_text("ʙσᴛ sᴛᴧʀᴛєᴅ....💤")
        await asyncio.sleep(0.1)
        
        await baby.delete()

    # --- HANDLE /start help ---
    if len(message.command) > 1 and message.command[1] == "help":
        if private:
            # 🚀 FIX: Yahan bhi safety shield ke sath random sticker lagaya
            try:
                await message.reply_sticker(random.choice(STICKERS))
            except Exception:
                pass
        return await _help(_, message)

    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    key = buttons.start_key(message.lang, private)
    
    # 🚀 FIX: Start command ke liye Random Image wala code
    if hasattr(config, "START_IMG_URL") and isinstance(config.START_IMG_URL, list):
        start_photo = random.choice(config.START_IMG_URL)
    elif isinstance(config.START_IMG, list):
        start_photo = random.choice(config.START_IMG)
    else:
        start_photo = config.START_IMG

    await message.reply_photo(
        photo=start_photo,
        caption=_text,
        reply_markup=key,
        quote=not private
    )

    if private:
        if await db.is_user(message.from_user.id):
            return
        await utils.send_log(message)
        await db.add_user(message.from_user.id)
    else:
        if await db.is_chat(message.chat.id):
            return
        await utils.send_log(message, True)
        await db.add_chat(message.chat.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
            
