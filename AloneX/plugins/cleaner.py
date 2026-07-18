import os
from pyrogram import filters
from pyrogram.types import Message
from AloneX import app, config

DOWNLOAD_DIR = "downloads"

@app.on_message(filters.command(["clean"]))
async def clean_cmd(client, message: Message):
    # ✅ Direct sudo check without any external modules
    if message.from_user.id not in app.sudoers:
        return
        
    if len(message.command) < 2:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ !\n» ᴜsᴇ : `/clean 10` ᴏʀ `/clean all`")
    
    arg = message.command[1].lower()
    
    if not os.path.exists(DOWNLOAD_DIR):
        return await message.reply_text("📁 ᴅᴏᴡɴʟᴏᴀᴅs ғᴏʟᴅᴇʀ ɪs ᴇᴍᴘᴛʏ ᴄᴜʀʀᴇɴᴛʟʏ.")

    files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        return await message.reply_text("📁 ɴᴏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴏɴɢs ғᴏᴜɴᴅ.")

    # Sort files by oldest first
    files.sort(key=os.path.getctime)
    
    deleted_count = 0
    
    if arg == "all":
        for f in files:
            try:
                os.remove(f)
                deleted_count += 1
            except:
                pass
        msg = f"🗑 **ᴄʟᴇᴀɴᴇᴅ ᴀʟʟ !**\n» sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ `{deleted_count}` ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴏɴɢs."
        
    elif arg.isdigit():
        count = int(arg)
        for f in files[:count]:
            try:
                os.remove(f)
                deleted_count += 1
            except:
                pass
        msg = f"🗑 **ᴄʟᴇᴀɴᴇᴅ ᴏʟᴅᴇsᴛ sᴏɴɢs !**\n» sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ᴛʜᴇ ᴏʟᴅᴇsᴛ `{deleted_count}` ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴏɴɢs."
        
    else:
        return await message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴏɴʟʏ ɴᴜᴍʙᴇʀs ᴏʀ 'all'.\n» ᴇxᴀᴍᴘʟᴇ : `/clean 5`")

    await message.reply_text(msg)
    
    # Send report to Logger Group
    try:
        log_report = f"👤 {message.from_user.mention} ʀᴀɴ ᴀ ᴍᴀɴᴜᴀʟ ᴄʟᴇᴀɴᴜᴘ.\n\n{msg}"
        if hasattr(config, "LOGGER_ID") and config.LOGGER_ID:
            await app.send_message(config.LOGGER_ID, log_report)
    except Exception:
        pass


@app.on_message(filters.command(["istu"]))
async def list_downloads(client, message: Message):
    # ✅ Sudo check
    if message.from_user.id not in app.sudoers:
        return

    if not os.path.exists(DOWNLOAD_DIR):
        return await message.reply_text("📁 ᴅᴏᴡɴʟᴏᴀᴅs ғᴏʟᴅᴇʀ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ.")
        
    files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        return await message.reply_text("📁 ɴᴏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴏɴɢs ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴛʜᴇ sᴇʀᴠᴇʀ.")
        
    text = f"📁 **ᴛᴏᴛᴀʟ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ sᴏɴɢs : {len(files)}**\n\n"
    
    # Show only up to 30 files so the message doesn't get too long
    for i, f in enumerate(files[:30], 1):
        text += f"**{i}.** `{os.path.basename(f)}`\n"
        
    if len(files) > 30:
        text += f"\n*» ... ᴀɴᴅ {len(files) - 30} ᴍᴏʀᴇ.*"
        
    await message.reply_text(text)
  
