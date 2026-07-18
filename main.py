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

# ============ BOLD UNICODE FONT HELPER ============

def bold(text):
    """Convert text to bold Unicode characters"""
    bold_map = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
        'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
        'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
        'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠',
        'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧',
        'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮',
        'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
        '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗',
        ' ': ' ', '.': '．', ',': '，', ':': '：', ';': '；', '/': '／', '\\': '＼',
        '!': '❗', '?': '❓', '-': '➖', '+': '➕', '*': '✱', '=': '＝', '<': '＜', '>': '＞',
        '(': '（', ')': '）', '[': '［', ']': '］', '{': '｛', '}': '｝', '_': '＿', '~': '～',
        '|': '｜', '"': '＂', "'": '＇', '`': '｀', '@': '＠', '#': '＃', '$': '＄', '%': '％',
        '&': '＆', '^': '＾', '★': '★'
    }
    return ''.join(bold_map.get(char, char) for char in text)

# ============ REPLY KEYBOARDS ============

def user_menu(user_id):
    is_admin_user = is_admin(user_id)

    keyboard = [
        [
            KeyboardButton("🎬 " + bold("RANDOM")),
            KeyboardButton("📌 " + bold("LATEST"))
        ],
        [
            KeyboardButton("ℹ️ " + bold("ABOUT"))
        ]
    ]

    if is_admin_user:
        keyboard.append([
            KeyboardButton("🔑 " + bold("ADMIN"))
        ])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu():
    keyboard = [
        [
            KeyboardButton("📊 " + bold("DATABASE")),
            KeyboardButton("🔄 " + bold("REFRESH"))
        ],
        [
            KeyboardButton("📹 " + bold("COUNT")),
            KeyboardButton("📁 " + bold("EXPORT"))
        ],
        [
            KeyboardButton("👤 " + bold("USER MODE")),
            KeyboardButton("🔙 " + bold("BACK"))
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def after_video_menu():
    keyboard = [
        [
            KeyboardButton("🎲 " + bold("ANOTHER")),
            KeyboardButton("📌 " + bold("LATEST"))
        ],
        [
            KeyboardButton("🏠 " + bold("MENU"))
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============ BOT INIT ============

app = None
user_mode = {}

# ============ WELCOME MESSAGE ============

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    user_mode[user_id] = False

    user_photos = await context.bot.get_user_profile_photos(user_id, limit=1)

    welcome_text = (
        f"🎬 {bold('WELCOME TO P4ON BOT')}\n\n"
        f"👋 {bold('HELLO')} {bold(user.first_name)}!\n"
        f"🆔 {bold('USER ID')}: {bold(str(user_id))}\n"
        f"📁 {bold(str(len(video_ids)))} {bold('VIDEOS AVAILABLE')}\n\n"
        f"👇 {bold('CLICK A BUTTON TO START')}"
    )

    if user_photos.total_count > 0:
        photo = user_photos.photos[0][-1]
        await update.message.reply_photo(
            photo.file_id,
            caption=welcome_text,
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )

async def admin_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    user_mode[user_id] = True

    user_photos = await context.bot.get_user_profile_photos(user_id, limit=1)

    welcome_text = (
        f"🎬 {bold('WELCOME TO P4ON BOT')}\n\n"
        f"🔑 {bold('ADMIN MODE')}\n"
        f"👋 {bold('HELLO')} {bold(user.first_name)}!\n"
        f"🆔 {bold('ADMIN ID')}: {bold(str(user_id))}\n"
        f"📁 {bold(str(len(video_ids)))} {bold('VIDEOS')}\n"
        f"📺 {bold('CHANNEL')}: @P49NBOOBS\n\n"
        f"📊 {bold('SELECT AN OPTION')}"
    )

    if user_photos.total_count > 0:
        photo = user_photos.photos[0][-1]
        await update.message.reply_photo(
            photo.file_id,
            caption=welcome_text,
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            welcome_text,
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
    if text == "🔑 " + bold("ADMIN"):
        if is_admin(user_id):
            await admin_welcome(update, context)
        else:
            await update.message.reply_text("⛔ " + bold("ACCESS DENIED"))
        return

    # ===== SWITCH TO USER =====
    if text == "👤 " + bold("USER MODE"):
        if is_admin(user_id):
            user_mode[user_id] = False
            await send_welcome(update, context)
        else:
            await update.message.reply_text("⛔ " + bold("ACCESS DENIED"))
        return

    # ===== BACK =====
    if text == "🔙 " + bold("BACK"):
        if is_admin(user_id) and user_mode.get(user_id, False):
            await admin_welcome(update, context)
        else:
            await send_welcome(update, context)
        return

    # ===== MAIN MENU =====
    if text == "🏠 " + bold("MENU"):
        await start(update, context)
        return

    # ===== RANDOM VIDEO =====
    if text in ["🎬 " + bold("RANDOM"), "🎲 " + bold("ANOTHER")]:
        if not video_ids:
            await update.message.reply_text(
                "📭 " + bold("NO VIDEOS AVAILABLE") + "\n\n⚠️ " + bold("PLEASE CONTACT ADMIN"),
                reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
            )
            return

        video_id = random.choice(video_ids)
        caption = f"🎥 {bold('RANDOM VIDEO')}\n\n📊 {bold('VIDEO')} {bold(str(video_ids.index(video_id) + 1))} {bold('OF')} {bold(str(len(video_ids)))}"

        await update.message.reply_video(
            video_id,
            caption=caption,
            reply_markup=after_video_menu()
        )
        return

    # ===== LATEST VIDEO =====
    if text == "📌 " + bold("LATEST"):
        if not video_ids:
            await update.message.reply_text(
                "📭 " + bold("NO VIDEOS AVAILABLE") + "\n\n⚠️ " + bold("PLEASE CONTACT ADMIN"),
                reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
            )
            return

        video_id = video_ids[-1]
        caption = f"📌 {bold('LATEST VIDEO')}\n\n📊 {bold('VIDEO')} #{bold(str(len(video_ids)))}"

        await update.message.reply_video(
            video_id,
            caption=caption,
            reply_markup=after_video_menu()
        )
        return

    # ===== ABOUT =====
    if text == "ℹ️ " + bold("ABOUT"):
        about_text = (
            f"ℹ️ {bold('ABOUT')}\n\n"
            f"🤖 {bold('BOT')}: P4ON BOT\n"
            f"📌 {bold('TYPE')}: VIDEO DISTRIBUTOR\n"
            f"📹 {bold('VIDEOS')}: {bold(str(len(video_ids)))}\n\n"
            f"💡 {bold('CLICK BUTTONS TO GET VIDEOS')}"
        )
        await update.message.reply_text(
            about_text,
            reply_markup=user_menu(user_id) if not is_admin(user_id) else admin_menu()
        )
        return

    # ===== ADMIN CHECK =====
    if text in ["📊 " + bold("DATABASE"), "🔄 " + bold("REFRESH"), "📹 " + bold("COUNT"), "📁 " + bold("EXPORT")]:
        if not is_admin(user_id):
            await update.message.reply_text("⛔ " + bold("ACCESS DENIED"))
            return

    # ===== ADMIN STATS =====
    if text == "📊 " + bold("DATABASE"):
        stats = (
            f"📊 {bold('DATABASE INFO')}\n\n"
            f"📺 {bold('CHANNEL')}: @P49NBOOBS\n"
            f"🆔 {bold('CHANNEL ID')}: {bold(str(CHANNEL_ID))}\n"
            f"📹 {bold('TOTAL VIDEOS')}: {bold(str(len(video_ids)))}\n"
            f"📁 {bold('DB FILE')}: {JSON_FILE}\n"
            f"✅ {bold('STATUS')}: ACTIVE"
        )
        await update.message.reply_text(stats, reply_markup=admin_menu())
        return

    # ===== ADMIN REFRESH =====
    if text == "🔄 " + bold("REFRESH"):
        await update.message.reply_text("🔄 " + bold("REFRESHING DATABASE..."))
        await scan_channel()
        text_msg = (
            f"✅ {bold('DATABASE REFRESHED')}\n\n"
            f"📹 {bold('TOTAL VIDEOS')}: {bold(str(len(video_ids)))}"
        )
        await update.message.reply_text(text_msg, reply_markup=admin_menu())
        return

    # ===== ADMIN COUNT =====
    if text == "📹 " + bold("COUNT"):
        count = (
            f"📹 {bold('VIDEO COUNT')}\n\n"
            f"📊 {bold('TOTAL')}: {bold(str(len(video_ids)))}\n"
            f"🔹 {bold('FIRST')}: {video_ids[0][:15] if video_ids else 'NONE'}...\n"
            f"🔸 {bold('LAST')}: {video_ids[-1][:15] if video_ids else 'NONE'}..."
        )
        await update.message.reply_text(count, reply_markup=admin_menu())
        return

    # ===== ADMIN EXPORT =====
    if text == "📁 " + bold("EXPORT"):
        save_video_ids(video_ids)
        export = (
            f"📁 {bold('JSON EXPORT')}\n\n"
            f"✅ {bold('FILE SAVED')}\n"
            f"📄 {bold('FILENAME')}: {JSON_FILE}\n"
            f"📹 {bold('TOTAL')}: {bold(str(len(video_ids)))}"
        )
        await update.message.reply_text(export, reply_markup=admin_menu())
        return

# ============ FIXED CHANNEL POST HANDLER ============

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new posts in the channel - FIXED for channel video detection"""
    global video_ids

    # Handle channel_post (new posts in channel)
    if update.channel_post:
        chat_id = update.channel_post.chat.id

        # Only process posts from our target channel
        if chat_id == CHANNEL_ID:
            # Check if it's a video
            if update.channel_post.video:
                video_id = update.channel_post.video.file_id
                if video_id not in video_ids:
                    video_ids.append(video_id)
                    save_video_ids(video_ids)
                    print(f"📹 New video detected via channel_post! Total: {len(video_ids)}")
                    print(f"   File ID: {video_id[:30]}...")

            # Check if it's a document that is a video
            elif update.channel_post.document:
                mime = update.channel_post.document.mime_type
                if mime and ('video' in mime or mime == 'application/octet-stream'):
                    video_id = update.channel_post.document.file_id
                    if video_id not in video_ids:
                        video_ids.append(video_id)
                        save_video_ids(video_ids)
                        print(f"📹 New video (as document) detected! Total: {len(video_ids)}")

# ============ ADD VIDEO COMMAND (Admin) ============

async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add a video by replying to it"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ " + bold("ACCESS DENIED"))
        return

    # Check if admin replied to a video
    if update.message.reply_to_message and update.message.reply_to_message.video:
        video_id = update.message.reply_to_message.video.file_id
        if video_id not in video_ids:
            video_ids.append(video_id)
            save_video_ids(video_ids)
            await update.message.reply_text(
                f"✅ {bold('VIDEO ADDED')}\n\n"
                f"📹 {bold('TOTAL')}: {bold(str(len(video_ids)))}"
            )
        else:
            await update.message.reply_text("⚠️ " + bold("VIDEO ALREADY EXISTS"))

    elif update.message.reply_to_message and update.message.reply_to_message.document:
        mime = update.message.reply_to_message.document.mime_type
        if mime and 'video' in mime:
            video_id = update.message.reply_to_message.document.file_id
            if video_id not in video_ids:
                video_ids.append(video_id)
                save_video_ids(video_ids)
                await update.message.reply_text(
                    f"✅ {bold('VIDEO ADDED')}\n\n"
                    f"📹 {bold('TOTAL')}: {bold(str(len(video_ids)))}"
                )
            else:
                await update.message.reply_text("⚠️ " + bold("VIDEO ALREADY EXISTS"))
        else:
            await update.message.reply_text("⚠️ " + bold("NOT A VIDEO FILE"))
    else:
        await update.message.reply_text(
            "⚠️ " + bold("REPLY TO A VIDEO") + "\n\n"
            "💡 " + bold("Forward a video from channel and reply /add to it")
        )

# ============ SCAN CHANNEL ============

async def scan_channel():
    """Scan channel for videos - Fixed approach"""
    global video_ids
    print(f"🔍 Checking channel: {CHANNEL_ID}")

    try:
        # Check bot membership in channel
        try:
            member = await app.bot.get_chat_member(CHANNEL_ID, app.bot.id)
            print(f"👤 Bot status in channel: {member.status}")
            if member.status not in ['administrator', 'creator']:
                print("⚠️ WARNING: Bot is not admin in channel!")
                print("   → Add bot as ADMIN with these permissions:")
                print("      • Post Messages")
                print("      • Edit Messages") 
                print("      • Delete Messages")
        except Exception as e:
            print(f"⚠️ Cannot check membership: {e}")

        # Load existing videos from JSON
        video_ids = load_video_ids()
        print(f"📊 Loaded {len(video_ids)} videos from {JSON_FILE}")

        if len(video_ids) == 0:
            print("💡 No videos found. To add videos:")
            print("   1. Forward videos from channel to bot, then reply /add")
            print("   2. Post new videos in channel (auto-detected)")
            print("   3. Manually add file_ids to video_ids.json")

        save_video_ids(video_ids)

    except Exception as e:
        print(f"❌ Error: {e}")

# ============ HELP COMMAND ============

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        f"🤖 {bold('P4ON BOT HELP')}\n\n"
        f"🎬 {bold('RANDOM')} - Get a random video\n"
        f"📌 {bold('LATEST')} - Get the latest video\n"
        f"ℹ️ {bold('ABOUT')} - Bot information\n\n"
        f"🔑 {bold('ADMIN COMMANDS')}\n"
        f"/add - Reply to a video to add it\n"
        f"📊 {bold('DATABASE')} - View database info\n"
        f"🔄 {bold('REFRESH')} - Refresh database\n"
        f"📹 {bold('COUNT')} - Video count\n"
        f"📁 {bold('EXPORT')} - Save to JSON"
    )
    await update.message.reply_text(help_text)

# ============ MAIN ============

async def main():
    global app

    app = Application.builder().token(BOT_TOKEN).build()

    # ===== REGISTER HANDLERS (ORDER MATTERS!) =====

    # 1. Channel post handler FIRST (highest priority, group 0)
    # This catches new videos posted in the channel
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post), group=0)

    # 2. Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add_video))

    # 3. Text message handler (group 1, lower priority)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages), group=1)

    await post_init()

    print("=" * 50)
    print("🤖 P4ON BOT STARTED!")
    print("=" * 50)
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"📺 Channel: {CHANNEL_ID}")
    print(f"📁 Database: {JSON_FILE}")
    print("=" * 50)
    print("⚡ IMPORTANT: Bot must be ADMIN in the channel!")
    print("⚡ Use /add command to manually add existing videos")
    print("⚡ New videos posted in channel auto-detected")
    print("=" * 50)

    # CRITICAL FIX: Use allowed_updates to receive channel_posts
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("✅ Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
