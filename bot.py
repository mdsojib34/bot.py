from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import config

app = Client(
    "probot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

users = set()
timer = 300
link = "https://t.me/yourchannel"

# ================= SAVE USERS =================
@app.on_message(filters.private)
async def save_users(client, message):
    users.add(message.from_user.id)

# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):
    if message.from_user.id != config.ADMIN_ID:
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url=link)],
        [InlineKeyboardButton("⚙️ Panel", callback_data="panel")]
    ])

    await message.reply_text("🔥 ADMIN PANEL", reply_markup=buttons)

# ================= PANEL =================
@app.on_callback_query(filters.regex("panel"))
async def panel(client, callback_query):
    if callback_query.from_user.id != config.ADMIN_ID:
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Users", callback_data="users")],
        [InlineKeyboardButton("📤 Broadcast", callback_data="broadcast")]
    ])

    await callback_query.message.edit_text("⚙️ CONTROL PANEL", reply_markup=buttons)

# ================= USERS =================
@app.on_callback_query(filters.regex("users"))
async def show_users(client, callback_query):
    await callback_query.answer(f"Total Users: {len(users)}", show_alert=True)

# ================= BROADCAST =================
@app.on_message(filters.text & filters.private)
async def broadcast(client, message):
    if message.from_user.id != config.ADMIN_ID:
        return

    for user in users:
        try:
            await client.send_message(user, message.text)
        except:
            pass

# ================= SET TIME =================
@app.on_message(filters.command("settime"))
async def set_time(client, message):
    global timer
    if message.from_user.id != config.ADMIN_ID:
        return

    try:
        timer = int(message.command[1])
        await message.reply(f"⏱ Timer set to {timer} sec")
    except:
        await message.reply("Usage: /settime 60")

# ================= SET LINK =================
@app.on_message(filters.command("setlink"))
async def set_link(client, message):
    global link
    if message.from_user.id != config.ADMIN_ID:
        return

    try:
        link = message.command[1]
        await message.reply("🔗 Link updated")
    except:
        await message.reply("Usage: /setlink https://t.me/link")

# ================= AUTO SENDER =================
async def auto_send():
    global timer, link
    while True:
        await asyncio.sleep(timer)
        for user in users:
            try:
                await app.send_message(user, f"🔥 Join Now:\n{link}")
            except:
                pass

# ================= MAIN RUN =================
async def main():
    await app.start()
    print("✅ Bot Started Successfully")
    asyncio.create_task(auto_send())
    await idle()

app.run(main())
