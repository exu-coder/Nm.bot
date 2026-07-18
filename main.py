import os
import json
import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ YOUR CONFIGURATION ============
BOT_TOKEN = "8848345002:AAGXAe8hUUSqgGWULHBsfsqGX69ix8Um67E"
CHANNEL_ID = -1004380729703
ADMIN_ID = 8379062893

# ============ JSON DATABASE ============
JSON_FILE = "video_ids.json"

def load_video_ids():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_video_ids(video_ids):
    with open(JSON_FILE, 'w') as f:
        json.dump(video_ids, f, indent=4)

video_ids = load_video_ids()

def is_admin(user_id):
    return user_id == ADMIN_ID

# ============ REPLY KEYBOARDS ============

def user_menu(user_id):
    is_admin_user = is_admin(user_id)
    
    keyboard = [
        [
            KeyboardButton("🎬 𝐑𝐀𝐍𝐃𝐎𝐌"),
            KeyboardButton("📌 𝐋𝐀𝐓𝐄𝐒𝐓")
        ],
        [
            KeyboardButton("ℹ️ 𝐀𝐁𝐎𝐔𝐓")
        ]
    ]
    
    if is_admin_user:
        keyboard.append([
            KeyboardButton("🔑 𝐀𝐃𝐌𝐈𝐍")
        ])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu():
    keyboard = [
        [
            KeyboardButton("📊 𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄"),
            KeyboardButton("🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇")
        ],
        [
            KeyboardButton("📹 𝐂𝐎𝐔𝐍𝐓"),
            KeyboardButton("📁 𝐄𝐗𝐏𝐎𝐑𝐓")
        ],
        [
            KeyboardButton("👤 𝐔𝐒𝐄𝐑 𝐌𝐎𝐃𝐄"),
            KeyboardButton("🔙 𝐁𝐀𝐂𝐊")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def after_video_menu():
    keyboard = [
        [
            KeyboardButton("🎲 𝐀𝐍𝐎𝐓𝐇𝐄𝐑"),
            KeyboardButton("📌 𝐋𝐀𝐓𝐄𝐒𝐓")
        ],
        [
            KeyboardButton("🏠 𝐌𝐄𝐍𝐔")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============ BOT INIT ============

app = None
user_mode = {}

# ============ WELCOME MESSAGE WITH PROFILE PICTURE ============

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with user's profile picture"""
    user_id = update.effective_user.id
    user = update.effective_user
    user_mode[user_id] = False
    
    # Get user's profile picture
    user_photos = await context.bot.get_user_profile_photos(user_id, limit=1)
    
    welcome_text = (
        f"🎬 **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐏𝟒𝐎𝐍 𝐁𝐎𝐓**\n\n"
        f"👋 **𝐇𝐄𝐋𝐋𝐎** {user.first_name}!\n"
        f"🆔 **𝐔𝐒𝐄𝐑 𝐈𝐃**: {user_id}\n"
        f"📁 **{len(video_ids)} 𝐕𝐈𝐃𝐄𝐎𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄**\n\n"
        f"👇 **𝐂𝐋𝐈𝐂𝐊 𝐀 𝐁𝐔𝐓𝐓𝐎𝐍 𝐓𝐎 𝐒𝐓𝐀𝐑𝐓**"
    )
    
    # If user has profile picture, send it with the message
    if user_photos.total_count > 0:
        photo = user_photos.photos[0][-1]  # Get the largest photo
        await update.message.reply_photo(
            photo.file_id,
            caption=welcome_text,
            parse_mode="Markdown",
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )
    else:
        # If no profile picture, send text message
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )

# ============ ADMIN WELCOME ============

async def admin_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send admin welcome message"""
    user_id = update.effective_user.id
    user = update.effective_user
    user_mode[user_id] = True
    
    # Get user's profile picture
    user_photos = await context.bot.get_user_profile_photos(user_id, limit=1)
    
    welcome_text = (
        f"🎬 **𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐏𝟒𝐎𝐍 𝐁𝐎𝐓**\n\n"
        f"🔑 **𝐀𝐃𝐌𝐈𝐍 𝐌𝐎𝐃𝐄**\n"
        f"👋 **𝐇𝐄𝐋𝐋𝐎** {user.first_name}!\n"
        f"🆔 **𝐀𝐃𝐌𝐈𝐍 𝐈𝐃**: {user_id}\n"
        f"📁 **{len(video_ids)} 𝐕𝐈𝐃𝐄𝐎𝐒**\n"
        f"📺 **𝐂𝐇𝐀𝐍𝐍𝐄𝐋**: @𝐏𝟒𝟗𝐍𝐁𝐎𝐎𝐁𝐒\n\n"
        f"📊 **𝐒𝐄𝐋𝐄𝐂𝐓 𝐀𝐍 𝐎𝐏𝐓𝐈𝐎𝐍**"
    )
    
    if user_photos.total_count > 0:
        photo = user_photos.photos[0][-1]
        await update.message.reply_photo(
            photo.file_id,
            caption=welcome_text,
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

# ============ START COMMAND ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id):
        await admin_welcome(update, context)
    else:
        await send_welcome(update, context)

# ============ MESSAGE HANDLER ============

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # ===== SWITCH TO ADMIN =====
    if text == "🔑 𝐀𝐃𝐌𝐈𝐍":
        if is_admin(user_id):
            await admin_welcome(update, context)
        else:
            await update.message.reply_text("⛔ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**", parse_mode="Markdown")
        return
    
    # ===== SWITCH TO USER =====
    if text == "👤 𝐔𝐒𝐄𝐑 𝐌𝐎𝐃𝐄":
        if is_admin(user_id):
            user_mode[user_id] = False
            await send_welcome(update, context)
        else:
            await update.message.reply_text("⛔ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**", parse_mode="Markdown")
        return
    
    # ===== BACK =====
    if text == "🔙 𝐁𝐀𝐂𝐊":
        if is_admin(user_id) and user_mode.get(user_id, False):
            await admin_welcome(update, context)
        else:
            await send_welcome(update, context)
        return
    
    # ===== MAIN MENU =====
    if text == "🏠 𝐌𝐄𝐍𝐔":
        await start(update, context)
        return
    
    # ===== RANDOM VIDEO =====
    if text in ["🎬 𝐑𝐀𝐍𝐃𝐎𝐌", "🎲 𝐀𝐍𝐎𝐓𝐇𝐄𝐑"]:
        if not video_ids:
            await update.message.reply_text(
                "📭 **𝐍𝐎 𝐕𝐈𝐃𝐄𝐎𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄**\n\n"
                "⚠️ **𝐏𝐋𝐄𝐀𝐒𝐄 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍**",
                parse_mode="Markdown",
                reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
            )
            return
        
        video_id = random.choice(video_ids)
        caption = f"🎥 **𝐑𝐀𝐍𝐃𝐎𝐌 𝐕𝐈𝐃𝐄𝐎**\n\n📊 **𝐕𝐈𝐃𝐄𝐎 {video_ids.index(video_id) + 1} 𝐎𝐅 {len(video_ids)}**"
        
        await update.message.reply_video(
            video_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=after_video_menu()
        )
        return
    
    # ===== LATEST VIDEO =====
    if text in ["📌 𝐋𝐀𝐓𝐄𝐒𝐓"]:
        if not video_ids:
            await update.message.reply_text(
                "📭 **𝐍𝐎 𝐕𝐈𝐃𝐄𝐎𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄**\n\n"
                "⚠️ **𝐏𝐋𝐄𝐀𝐒𝐄 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍**",
                parse_mode="Markdown",
                reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
            )
            return
        
        video_id = video_ids[-1]
        caption = f"📌 **𝐋𝐀𝐓𝐄𝐒𝐓 𝐕𝐈𝐃𝐄𝐎**\n\n📊 **𝐕𝐈𝐃𝐄𝐎 #{len(video_ids)}**"
        
        await update.message.reply_video(
            video_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=after_video_menu()
        )
        return
    
    # ===== ABOUT =====
    if text == "ℹ️ 𝐀𝐁𝐎𝐔𝐓":
        about_text = (
            f"ℹ️ **𝐀𝐁𝐎𝐔𝐓**\n\n"
            f"🤖 **𝐁𝐎𝐓**: 𝐏𝟒𝐎𝐍 𝐁𝐎𝐓\n"
            f"📌 **𝐓𝐘𝐏𝐄**: 𝐕𝐈𝐃𝐄𝐎 𝐃𝐈𝐒𝐓𝐑𝐈𝐁𝐔𝐓𝐎𝐑\n"
            f"📹 **𝐕𝐈𝐃𝐄𝐎𝐒**: {len(video_ids)}\n\n"
            f"💡 **𝐂𝐋𝐈𝐂𝐊 𝐁𝐔𝐓𝐓𝐎𝐍𝐒 𝐓𝐎 𝐆𝐄𝐓 𝐕𝐈𝐃𝐄𝐎𝐒**"
        )
        await update.message.reply_text(
            about_text,
            parse_mode="Markdown",
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )
        return
    
    # ===== ADMIN CHECK =====
    if text in ["📊 𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄", "🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇", "📹 𝐂𝐎𝐔𝐍𝐓", "📁 𝐄𝐗𝐏𝐎𝐑𝐓"]:
        if not is_admin(user_id):
            await update.message.reply_text("⛔ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃**", parse_mode="Markdown")
            return
    
    # ===== ADMIN STATS =====
    if text == "📊 𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄":
        stats = (
            f"📊 **𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄 𝐈𝐍𝐅𝐎**\n\n"
            f"📺 **𝐂𝐇𝐀𝐍𝐍𝐄𝐋**: @𝐏𝟒𝟗𝐍𝐁𝐎𝐎𝐁𝐒\n"
            f"🆔 **𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐈𝐃**: {CHANNEL_ID}\n"
            f"📹 **𝐓𝐎𝐓𝐀𝐋 𝐕𝐈𝐃𝐄𝐎𝐒**: {len(video_ids)}\n"
            f"📁 **𝐃𝐁 𝐅𝐈𝐋𝐄**: {JSON_FILE}\n"
            f"✅ **𝐒𝐓𝐀𝐓𝐔𝐒**: 𝐀𝐂𝐓𝐈𝐕𝐄"
        )
        await update.message.reply_text(stats, parse_mode="Markdown", reply_markup=admin_menu())
        return
    
    # ===== ADMIN REFRESH =====
    if text == "🔄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇":
        await update.message.reply_text("🔄 **𝐑𝐄𝐅𝐑𝐄𝐒𝐇𝐈𝐍𝐆...**", parse_mode="Markdown")
        await scan_channel()
        text_msg = (
            f"✅ **𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄 𝐑𝐄𝐅𝐑𝐄𝐒𝐇𝐄𝐃**\n\n"
            f"📹 **𝐓𝐎𝐓𝐀𝐋 𝐕𝐈𝐃𝐄𝐎𝐒**: {len(video_ids)}"
        )
        await update.message.reply_text(text_msg, parse_mode="Markdown", reply_markup=admin_menu())
        return
    
    # ===== ADMIN COUNT =====
    if text == "📹 𝐂𝐎𝐔𝐍𝐓":
        count = (
            f"📹 **𝐕𝐈𝐃𝐄𝐎 𝐂𝐎𝐔𝐍𝐓**\n\n"
            f"📊 **𝐓𝐎𝐓𝐀𝐋**: {len(video_ids)}\n"
            f"🔹 **𝐅𝐈𝐑𝐒𝐓**: {video_ids[0][:15] if video_ids else '𝐍𝐎𝐍𝐄'}...\n"
            f"🔸 **𝐋𝐀𝐒𝐓**: {video_ids[-1][:15] if video_ids else '𝐍𝐎𝐍𝐄'}..."
        )
        await update.message.reply_text(count, parse_mode="Markdown", reply_markup=admin_menu())
        return
    
    # ===== ADMIN EXPORT =====
    if text == "📁 𝐄𝐗𝐏𝐎𝐑𝐓":
        save_video_ids(video_ids)
        export = (
            f"📁 **𝐉𝐒𝐎𝐍 𝐄𝐗𝐏𝐎𝐑𝐓**\n\n"
            f"✅ **𝐅𝐈𝐋𝐄 𝐒𝐀𝐕𝐄𝐃**\n"
            f"📄 **𝐅𝐈𝐋𝐄𝐍𝐀𝐌𝐄**: {JSON_FILE}\n"
            f"📹 **𝐓𝐎𝐓𝐀𝐋**: {len(video_ids)}"
        )
        await update.message.reply_text(export, parse_mode="Markdown", reply_markup=admin_menu())
        return

# ============ VIDEO INDEXING ============

async def scan_channel():
    global video_ids
    video_ids = []
    print(f"🔍 Scanning: {CHANNEL_ID}")
    
    try:
        chat = await app.bot.get_chat(CHANNEL_ID)
        print(f"✅ Found channel: {chat.title}")
        
        # Try to get messages
        try:
            async for msg in app.bot.get_chat_history(chat_id=CHANNEL_ID, limit=500):
                if msg.video:
                    video_ids.append(msg.video.file_id)
                    print(f"📹 Found: {msg.video.file_id[:20]}...")
        except Exception as e:
            print(f"⚠️ get_chat_history failed: {e}")
            # Try alternative method
            try:
                updates = await app.bot.get_updates(limit=200)
                for update in updates:
                    if update.channel_post and update.channel_post.chat.id == CHANNEL_ID:
                        if update.channel_post.video:
                            video_ids.append(update.channel_post.video.file_id)
                            print(f"📹 Found via updates: {update.channel_post.video.file_id[:20]}...")
            except Exception as e2:
                print(f"⚠️ get_updates failed: {e2}")
        
        save_video_ids(video_ids)
        print(f"✅ Loaded {len(video_ids)} videos")
        
        if len(video_ids) == 0:
            print("⚠️ No videos found! Make sure:")
            print("   1. Bot is admin in the channel")
            print("   2. There are videos in the channel")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def handle_new_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.video:
        video_ids.append(update.channel_post.video.file_id)
        save_video_ids(video_ids)
        print(f"📹 New video! Total: {len(video_ids)}")

async def post_init():
    await scan_channel()

# ============ HELP COMMAND ============

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ============ MAIN ============

async def main():
    global app
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.add_handler(MessageHandler(filters.VIDEO & filters.Chat(CHANNEL_ID), handle_new_video))
    
    await post_init()
    
    print("🤖 Bot Running!")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"📺 Channel: {CHANNEL_ID}")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
