# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# shona the queen


from pyrogram import enums, types

from AloneX import app, logger


class VCLogger:
    def __init__(self):
        self.user_cache: dict[tuple, tuple] = {}
        self.join_count: dict[tuple, int] = {}
        # 🚀 NAYA: Jo groups log off karenge unki ID yahan save hogi
        self.disabled_chats: set = set() 

    async def _get_user_info(self, chat_id: int, user_id: int) -> tuple:
        key = (chat_id, user_id)
        if key in self.user_cache:
            return self.user_cache[key]

        name = "ᴜsᴇʀ"
        username = "ɪɢɴᴏʀᴇᴅ"
        role = "ᴍᴇᴍʙᴇʀ"

        try:
            member = await app.get_chat_member(chat_id, user_id)
            if member:
                if member.user:
                    user = member.user
                    name = user.first_name or "ᴜsᴇʀ"
                    if user.last_name:
                        name += f" {user.last_name}"
                    username = f"@{user.username}" if user.username else "ɪɢɴᴏʀᴇᴅ"

                if member.status in (
                    enums.ChatMemberStatus.OWNER,
                    enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    role = "ᴀᴅᴍɪɴ"
        except Exception:
            pass

        self.user_cache[key] = (name, username, role)
        return name, username, role

    async def _get_vc_link(self, chat_id: int) -> str | None:
        try:
            chat = await app.get_chat(chat_id)
            if chat.username:
                return f"https://t.me/{chat.username}?videochat"
            if chat.invite_link:
                return chat.invite_link
            invite = await app.export_chat_invite_link(chat_id)
            return invite
        except Exception:
            return None

    async def _send(self, chat_id: int, user_id: int, joined: bool) -> None:
        # 🚀 NAYA: Agar group ka admin isko OFF kar chuka hai, toh return kar do (log mat bhejo)
        if chat_id in self.disabled_chats:
            return

        name, username, role = await self._get_user_info(chat_id, user_id)
        mention = f'<a href="tg://user?id={user_id}">{name}</a>'
        
        tag = "🟢 **#ᴊᴏɪɴ_ᴠɪᴅᴇᴏ_ᴄʜᴀᴛ**" if joined else "🔴 **#ʟᴇᴀᴠᴇ_ᴠɪᴅᴇᴏ_ᴄʜᴀᴛ**"
        action = f"ᴊᴏɪɴᴇᴅ  [ {role} ]" if joined else f"ʟᴇғᴛ  [ {role} ]"

        details = (
            f"**» ɴᴀᴍᴇ :** {mention}\n"
            f"**» ɪᴅ :** <code>{user_id}</code>\n"
            f"**» ᴜsᴇʀɴᴀᴍᴇ :** {username}\n"
            f"**» ᴀᴄᴛɪᴏɴ :** {action}"
        )

        reply_markup = None
        if joined:
            key = (chat_id, user_id)
            self.join_count[key] = self.join_count.get(key, 0) + 1
            details += f"\n**» ᴊᴏɪɴ ᴄᴏᴜɴᴛ :** {self.join_count[key]}"

            vc_link = await self._get_vc_link(chat_id)
            if vc_link:
                reply_markup = types.InlineKeyboardMarkup(
                    [[types.InlineKeyboardButton(text="ᴊᴏɪɴ ʟɪᴠᴇ ᴠᴄ 📶", url=vc_link)]]
                )

        text = f"{tag}\n\n<blockquote>{details}</blockquote>"

        try:
            await app.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"[VCLogger] Failed to send notice for {chat_id}: {e}")

    async def notify_join(self, chat_id: int, user_id: int) -> None:
        await self._send(chat_id, user_id, joined=True)

    async def notify_leave(self, chat_id: int, user_id: int) -> None:
        await self._send(chat_id, user_id, joined=False)

    def clear_chat(self, chat_id: int) -> None:
        for key in [k for k in self.user_cache if k[0] == chat_id]:
            del self.user_cache[key]
        for key in [k for k in self.join_count if k[0] == chat_id]:
            del self.join_count[key]

# Hame iska ek instance banakar rakhna hoga jo command mein import ho sake
vc_log_instance = VCLogger()
        
