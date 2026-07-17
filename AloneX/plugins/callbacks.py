# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import re
import asyncio
from pyrogram import enums, filters, types
from AloneX import anon, app, db, lang, queue, tg, yt
from AloneX.helpers import admin_check, buttons, can_manage_vc

@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)

@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action, chat_id = args[1], int(args[2])
    qaction = len(args) == 4
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        return await query.answer(query.lang["not_playing"], show_alert=True)

    if action == "status":
        status = await db.get_playing(chat_id)
        if status:
            keyboard = buttons.controls(chat_id, timer=f"{status.played} {status.duration}", _lang=query.lang, autoplay_on=await db.get_autoplay(chat_id))
            try: await query.edit_message_reply_markup(reply_markup=keyboard)
            except: pass
        return await query.answer()

    if action == "autoplay_toggle":
        new_state = not await db.get_autoplay(chat_id)
        await db.set_autoplay(chat_id, new_state)
        await query.answer(query.lang.get("autoplay_on", "Enabled") if new_state else query.lang.get("autoplay_off", "Disabled"))
        
        # 🛠 FIX: ▶️ aur ** dono hata diye gaye hain, ab text ekdam normal aayega
        status_msg = "🟢 ᴇɴᴀʙʟᴇᴅ" if new_state else "🔴 ᴅɪsᴀʙʟᴇᴅ"
        try: await app.send_message(chat_id=chat_id, text=f"ᴀᴜᴛᴏ-ᴘʟᴀʏ ʜᴀs ʙᴇᴇɴ {status_msg} ʙʏ {query.from_user.mention}")
        except: pass
            
        try:
            return await query.edit_message_reply_markup(reply_markup=buttons.controls(chat_id, _lang=query.lang, autoplay_on=new_state))
        except:
            return

    await query.answer(query.lang["processing"], show_alert=True)

    # Action Handlers
    if action == "pause": await anon.pause(chat_id); reply = query.lang["play_paused"].format(user)
    elif action == "resume": await anon.resume(chat_id); reply = query.lang["play_resumed"].format(user)
    elif action == "skip": await anon.play_next(chat_id); reply = query.lang["play_skipped"].format(user)
    elif action == "stop": await anon.stop(chat_id); reply = query.lang["play_stopped"].format(user)
    elif action == "replay": await anon.replay(chat_id); reply = query.lang["play_replayed"].format(user)

    try:
        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply, quote=False)
            await query.message.delete()
        else:
            original_text = query.message.caption.html if query.message.caption else query.message.text.html
            mtext = re.sub(r"\n\n<blockquote>.*?</blockquote>", "", original_text, flags=re.DOTALL)
            
            status = await db.get_playing(chat_id)
            keyboard = buttons.controls(
                chat_id,
                timer=f"{status.played} {status.duration}" if status else None,
                _lang=query.lang,
                autoplay_on=await db.get_autoplay(chat_id),
            )
            
            final_text = f"{mtext}\n\n<blockquote>{reply}</blockquote>"
            if query.message.photo or query.message.video or query.message.animation:
                await query.edit_message_caption(caption=final_text, reply_markup=keyboard)
            else:
                await query.edit_message_text(text=final_text, reply_markup=keyboard)
    except:
        pass


@app.on_callback_query(filters.regex("help") & ~app.bl_users)
@lang.language()
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    is_private = query.message.chat.type == enums.ChatType.PRIVATE
    has_media = bool(query.message.photo or query.message.video or query.message.animation)

    async def edit_ui(new_text, new_markup):
        try:
            if has_media:
                await query.edit_message_caption(caption=new_text, reply_markup=new_markup)
            else:
                await query.edit_message_text(text=new_text, reply_markup=new_markup)
        except Exception:
            pass

    if len(data) == 1:
        if not is_private:
            return await query.answer(url=f"https://t.me/{app.username}?start=help")
        return await edit_ui(query.lang["help_menu"], buttons.help_markup(query.lang))

    if data[1] == "back":
        return await edit_ui(query.lang["help_menu"], buttons.help_markup(query.lang))
        
    elif data[1] == "home":
        if not is_private:
            return await query.answer(url=f"https://t.me/{app.username}?start=home")
        
        _text = query.lang["start_pm"].format(query.from_user.first_name, app.name)
        key = buttons.start_key(query.lang, True)
        return await edit_ui(_text, key)
        
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except:
            return

    await edit_ui(query.lang[f"help_{data[1]}"], buttons.help_markup(query.lang, True))


@app.on_callback_query(filters.regex("settings") & ~app.bl_users)
@lang.language()
@admin_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)

    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, _admin)
        _admin = not _admin
    
    markup = buttons.settings_markup(query.lang, _admin, _delete, _language, chat_id)
    if query.message.photo or query.message.video or query.message.animation:
        await query.edit_message_reply_markup(reply_markup=markup)
    else:
        await query.edit_message_reply_markup(reply_markup=markup)


async def _delete_later(message: types.Message) -> None:
    try:
        await asyncio.sleep(7)
        await message.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex("^autoplay_panel") & ~app.bl_users)
@lang.language()
async def _autoplay_panel(_, query: types.CallbackQuery):
    data = query.data.split()
    action = data[1] if len(data) > 1 else None
    chat_id = query.message.chat.id
    has_media = bool(query.message.photo or query.message.video or query.message.animation)

    if action == "info":
        await query.answer()
        text = query.lang.get(
            "autoplay_info_title",
            "ℹ️ <b>How Autoplay works?</b>\n\n"
            "• Automatically continues music playback.\n"
            "• Follows current audio or video mode.\n"
            "• Designed for seamless listening.\n\n"
            "🎶 Sit back & enjoy the music.",
        )
        markup = buttons.autoplay_info_markup(query.lang)
        if has_media: return await query.edit_message_caption(caption=text, reply_markup=markup)
        else: return await query.edit_message_text(text=text, reply_markup=markup)

    elif action == "back":
        await query.answer()
        text = query.lang.get(
            "autoplay_panel_title",
            "🎶 <b>Autoplay:</b>\n\n"
            "• Keeps music playing automatically.\n"
            "• Ensures smooth and uninterrupted listening.\n"
            "• Designed for a seamless music experience.",
        )
        markup = buttons.autoplay_markup(query.lang)
        if has_media: return await query.edit_message_caption(caption=text, reply_markup=markup)
        else: return await query.edit_message_text(text=text, reply_markup=markup)

    elif action == "close":
        await query.answer()
        try: await query.message.delete()
        except: pass
        return

    elif action == "enable":
        await db.set_autoplay(chat_id, True)
        await query.answer(query.lang.get("autoplay_on", "Enabled"))
        try: await query.message.delete()
        except: pass

        msg = await app.send_message(
            chat_id=chat_id,
            text=query.lang.get("autoplay_enabled_short", "✅ Autoplay Enabled"),
        )
        asyncio.create_task(_delete_later(msg))
        return
    
