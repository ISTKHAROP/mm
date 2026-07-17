# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic

import asyncio
from pyrogram import filters
from pyrogram.types import Message
from AloneX import app, logger

DELETE_DELAY = 7

class VCLogger:
    def __init__(self):
        self.join_count: dict[tuple, int] = {}
        self.user_cache: dict[int, tuple] = {}
        # List of chats where it has been manually turned OFF (Temporary RAM storage)
        self.disabled_chats: set[int] = set() 

    # Check whether logging is enabled in the chat or not
    def is_enabled(self, chat_id: int) -> bool:
        return chat_id not in self.disabled_chats

    async def _get_user_info(self, chat_id: int, user_id: int) -> tuple:
        if user_id in self.user_cache:
            return self.user_cache[user_id]

        name = "User"
        username = "None"
        try:
            member = await app.get_chat_member(chat_id, user_id)
            if member and member.user:
                user = member.user
                name = user.first_name or "User"
                if user.last_name:
                    name += f" {user.last_name}"
                username = f"@{user.username}" if user.username else "None"
        except Exception:
            pass

        self.user_cache[user_id] = (name, username)
        return name, username

    async def _delete_later(self, chat_id: int, message_id: int) -> None:
        try:
            await asyncio.sleep(DELETE_DELAY)
            await app.delete_messages(chat_id, message_id)
        except Exception:
            pass

    async def notify_join(self, chat_id: int, user_id: int) -> None:
        if not self.is_enabled(chat_id):
            return

        key = (chat_id, user_id)
        self.join_count[key] = self.join_count.get(key, 0) + 1
        count = self.join_count[key]

        name, username = await self._get_user_info(chat_id, user_id)
        mention = f'<a href="tg://user?id={user_id}">{name}</a>'

        text = (
            "<b>#JoinVideoChat</b>\n\n"
            f"<b>• Name:</b> {mention}\n"
            f"<b>• ID:</b> <code>{user_id}</code>\n"
            f"<b>• Username:</b> {username}"
        )
        if count > 1:
            text += f"\n\n<b>🔁 Join count:</b> <code>{count}</code>"

        try:
            msg = await app.send_message(chat_id, text)
            asyncio.create_task(self._delete_later(chat_id, msg.id))
        except Exception as e:
            logger.error(f"[VCLogger] Failed to send join notice for {chat_id}: {e}")

    async def notify_leave(self, chat_id: int, user_id: int) -> None:
        if not self.is_enabled(chat_id):
            return

        name, username = await self._get_user_info(chat_id, user_id)
        mention = f'<a href="tg://user?id={user_id}">{name}</a>'

        text = (
            "<b>#LeftVideoChat</b>\n\n"
            f"<b>• Name:</b> {mention}\n"
            f"<b>• ID:</b> <code>{user_id}</code>\n"
            f"<b>• Username:</b> {username}"
        )

        try:
            msg = await app.send_message(chat_id, text)
            asyncio.create_task(self._delete_later(chat_id, msg.id))
        except Exception as e:
            logger.error(f"[VCLogger] Failed to send leave notice for {chat_id}: {e}")

    def clear_chat(self, chat_id: int) -> None:
        for key in [k for k in self.join_count if k[0] == chat_id]:
            del self.join_count[key]

# --- VC Logger Instance ---
vc_log = VCLogger()

# --- Command Handler for ON/OFF ---
@app.on_message(filters.command(["vclog"]) & filters.group)
async def toggle_vclog(client, message: Message):
    if len(message.command) < 2:
        state = "ENABLED" if vc_log.is_enabled(message.chat.id) else "DISABLED"
        return await message.reply_text(
            f"Video Chat Logging is currently **{state}** in this chat.\n\n"
            "To change the settings, use:\n"
            "`/vclog off` - To turn off\n"
            "`/vclog on` - To turn on"
        )

    cmd_arg = message.command[1].lower()
    chat_id = message.chat.id

    if cmd_arg == "off":
        vc_log.disabled_chats.add(chat_id)
        await message.reply_text("✅ Video Chat logging has been **DISABLED (OFF)** for this group.")
    elif cmd_arg == "on":
        if chat_id in vc_log.disabled_chats:
            vc_log.disabled_chats.remove(chat_id)
        await message.reply_text("✅ Video Chat logging has been **ENABLED (ON)** for this group.")
    else:
        await message.reply_text("❌ Invalid command. Please use only `/vclog on` or `/vclog off`.")
        
