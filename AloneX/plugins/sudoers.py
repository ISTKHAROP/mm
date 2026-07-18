# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AloneX import app, db, lang
from AloneX.helpers import utils


@app.on_message(filters.command(["addsudo", "delsudo", "rmsudo"]) & filters.user(app.owner))
@lang.language()
async def _sudo(_, m: types.Message):
    user = await utils.extract_user(m)
    if not user:
        return await m.reply_text(m.lang["user_not_found"])

    if m.command[0] == "addsudo":
        if user.id in app.sudoers:
            return await m.reply_text(m.lang["sudo_already"].format(user.mention))

        app.sudoers.add(user.id)
        await db.add_sudo(user.id)
        await m.reply_text(m.lang["sudo_added"].format(user.mention))
    else:
        if user.id not in app.sudoers:
            return await m.reply_text(m.lang["sudo_not"].format(user.mention))

        app.sudoers.discard(user.id)
        await db.del_sudo(user.id)
        await m.reply_text(m.lang["sudo_removed"].format(user.mention))


SUDO_PIC = "https://h.uguu.se/bDCrjmdX.jpg"

@app.on_message(filters.command(["sudo", "sudolist"]))
@lang.language()
async def _listsudo(_, m: types.Message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="sudo_view")]]
    )
    # Special font and no **
    caption = "» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.\n\n» ɴᴏᴛᴇ: ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ."
    await m.reply_photo(photo=SUDO_PIC, caption=caption, reply_markup=keyboard)


@app.on_callback_query(filters.regex("^sudo_view$"))
async def sudo_view_cb(_, query: types.CallbackQuery):
    if query.from_user.id not in app.sudoers and query.from_user.id != app.owner:
        return await query.answer("⚠️ Only Sudo Users can view this list!", show_alert=True)
    
    await query.answer()

    try:
        owner = await app.get_users(app.owner)
        owner_name = owner.first_name if owner.first_name else "Owner"
        owner_id = owner.id
    except:
        owner_name = "Owner"
        owner_id = app.owner

    # Exact screenshot style text
    text = "┌ ʟɪsᴛ ᴏғ ʙᴏᴛ ᴍᴏᴅᴇʀᴀᴛᴏʀs ┘\n\n"
    text += f"● ᴏᴡɴᴇʀ ● ➥ [{owner_name}](tg://user?id={owner_id})\n\n"

    buttons = [[InlineKeyboardButton("● ᴠɪᴇᴡ ᴏᴡɴᴇʀ ●", url=f"tg://openmessage?user_id={owner_id}")]]

    sudoers = await db.get_sudoers()
    count = 1
    for user_id in sudoers:
        if user_id == app.owner:
            continue
        try:
            user = await app.get_users(user_id)
            user_name = user.first_name if user.first_name else "Sudo User"
            text += f"○ sᴜᴅᴏ {count} » [{user_name}](tg://user?id={user_id})\n"
            buttons.append([InlineKeyboardButton(f"๏ ᴠɪᴇᴡ sᴜᴅᴏ {count} ๏", url=f"tg://openmessage?user_id={user_id}")])
            count += 1
        except:
            continue

    buttons.append([InlineKeyboardButton("๏ ʙᴀᴄᴋ ๏", callback_data="sudo_back")])

    await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^sudo_back$"))
async def sudo_back_cb(_, query: types.CallbackQuery):
    if query.from_user.id not in app.sudoers and query.from_user.id != app.owner:
        return await query.answer("⚠️ Only Sudo Users can use this!", show_alert=True)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="sudo_view")]]
    )
    caption = "» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.\n\n» ɴᴏᴛᴇ: ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ."
    await query.edit_message_caption(caption=caption, reply_markup=keyboard)
    
