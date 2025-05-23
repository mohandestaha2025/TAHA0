import sqlite3
import re
import os
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)


# اتصال به پایگاه داده SQLite
conn = sqlite3.connect("bot_users.db", check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول کاربران و ادمین‌ها
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT
)
""")
conn.commit()

# متغیرهای عمومی
TOKEN = "7829435444:AAEVwMH-549ew0ZPzSLwOJwISG7EzhZxX3c"
SUPER_ADMIN_USERNAME = "@MKSHNT"
group_id = None
players = {}
choices = ["سنگ 🪨", "کاغذ 📜", "قیچی ✂️"]

# ==============================================
# توابع کمکی و عمومی
# ==============================================

def validate_national_code(national_code):
    """تابع بررسی صحت کد ملی"""
    if len(national_code) != 10 or not national_code.isdigit():
        return False
    checksum = int(national_code[-1])
    sums = sum(int(national_code[i]) * (10 - i) for i in range(9)) % 11
    return (sums < 2 and checksum == sums) or (sums >= 2 and checksum == 11 - sums)

def calculate_level(xp):
    """تابع محاسبه سطح بر اساس XP"""
    return xp // 1000 + 1

# ==============================================
# توابع مربوط به فایل‌های رسانه‌ای
# ==============================================

async def send_voice(update: Update, context) -> None:
    """تابع ارسال فایل صوتی 505"""
    chat_id = update.effective_chat.id
    try:
        file_path = "/storage/emulated/0/BOTFORMOHANDESTAHA/back505.ogg"
        caption_text = "🎤🎵i going back to 505..."
        if os.path.exists(file_path):
            with open(file_path, 'rb') as voice_file:
                await context.bot.send_voice(chat_id=chat_id, voice=voice_file, caption=caption_text)
        else:
            await update.message.reply_text("فایل 505.ogg پیدا نشد. لطفاً بررسی کنید که فایل در مسیر درست باشد.")
    except Exception as e:
        await update.message.reply_text(f"Ok!")

async def send_voice_meow(update: Update, context) -> None:
    """تابع ارسال صدای میو"""
    chat_id = update.effective_chat.id
    try:
        await context.bot.send_voice(chat_id=chat_id, voice=open('ogg.ogg', 'rb'))
    except Exception as e:
        await update.message.reply_text("مشکلی در ارسال صدا پیش آمد!")

async def send_begarafte_gif(update: Update, context) -> None:
    """تابع ارسال گیف بگا رفتم"""
    try:
        gif_path = "/storage/emulated/0/BOTFORMOHANDESTAHA/begarafte.gif"
        if os.path.exists(gif_path):
            with open(gif_path, "rb") as gif_file:
                await update.message.reply_animation(animation=gif_file, caption="منم همینطور 💔")
        else:
            await update.message.reply_text("فایل begarafte.gif پیدا نشد.")
    except Exception as e:
        await update.message.reply_text(f"Ok!")

# ==============================================
# دستورات عمومی و پاسخ به پیام‌ها
# ==============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع ربات (/start)"""
    # ایجاد دکمه شیشه‌ای
    keyboard = [[InlineKeyboardButton("Help", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ارسال پیام خوش‌آمدگویی با دکمه شیشه‌ای
    await update.message.reply_text(
        "سلام! من میکاسا هستم. چطور میتونم کمکتون کنم؟",
        reply_markup=reply_markup
    )
    
    # ثبت کاربر در دیتابیس
    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"کاربر {user_id}"
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما (/help)"""
    help_text = """📋 **لیست دستورات ربات:**

- `/start` - شروع ربات
- `/hello` - خوش‌آمدگویی
- `/info <id>` - نمایش اطلاعات کاربر
- `/leaderboard` - نمایش لیست کاربران برتر
- `/admin <id>` - اضافه کردن ادمین (فقط سوپر ادمین)
- `/addlevel <id> <amount>` - اضافه کردن سطح به کاربر (فقط سوپر ادمین)
- `/game1` - ثبت گروه برای بازی
- `/join` - ورود به بازی
- `/play` - شروع بازی سنگ، کاغذ، قیچی
- `/gamecancel` - لغو بازی و حذف بازیکنان

"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(help_text)
    else:
        await update.message.reply_text(help_text)

async def respond_to_message(update: Update, context):
    """پاسخ به پیام‌های خاص"""
    text = update.message.text
    
    if "کدملی" in text:
        match = re.search(r'\b\d{10}\b', text)
        if match:
            national_code = match.group()
            if validate_national_code(national_code):
                await update.message.reply_text("کد ملی معتبر است.")
            else:
                await update.message.reply_text("کد ملی معتبر نیست.")
        else:
            await update.message.reply_text("لطفاً یک کد ملی ۱۰ رقمی ارسال کنید.")
    
    elif text.lower() == "میکاسا میو کن":
        await send_voice_meow(update, context)
    
    elif text.lower() == "میکاسا آھنگ 505 رو پلی کن":
        await send_voice(update, context)
    
    elif "بگا رفتم" in text:
        await send_begarafte_gif(update, context)
    
    elif text == "سلام":
        await update.message.reply_text("سلام!")
    
    elif text == "حالم خراب":
        await update.message.reply_sticker("CAACAgIAAyEFAASgcRmLAAMxZ-UM2yQ1C8mE5NrxxXBNa1VxbNoAAjMPAALkaQABSAXbXIXGtqG6NgQ")
    
    elif text in ["عشق طاھا کیه", "عشق طاھا کیہ"]:
        await update.message.reply_sticker("CAACAgIAAxkBAAOBZ-UOEdpf2a6nsXUNkkG35P_I5BUAAlZSAAIucTBIZkUJSVF0-tM2BA")
    
    elif text in ["عشق امین کیه", "عشق امین کیہ"]:
        await update.message.reply_sticker("CAACAgQAAxkBAAOEZ-UOJWX2yO3cEojCxgLB5Pd7pwYAAn0XAALkxbFQVRNBR4Ovx3A2BA")
    
    elif text in ["تو میگفتی پی وی بلاک", "لبو رد کن"]:
        await update.message.reply_sticker("CAACAgQAAyEFAASgSsswAAN6Z-U0MRNWs7XWspiyOE4G8OacQlMAAsUTAAITSKFRKoy2IYmgtz82BA")
    
    elif "میو" in text:
        await update.message.reply_text("سلام!")
    
    elif "خوبی" in text:
        await update.message.reply_text("خوبم!")
    
    elif text == "میکاسا ساعتو بگو":
        current_time = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"اکنون {current_time} است.")
    
    elif text == "میکاسا تاریخو بگو":
        current_date = datetime.now().strftime("%Y-%m-%d")
        await update.message.reply_text(f"تاریخ امروز: {current_date}")

# ==============================================
# دستورات کاربری و مدیریتی
# ==============================================

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور خوش‌آمدگویی (/hello)"""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"کاربر {user_id}"
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        await update.message.reply_text(f"سلام {username}! شما به ربات اضافه شدید.")
    else:
        await update.message.reply_text(f"سلام دوباره {username}! خوش آمدید.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور نمایش اطلاعات کاربر (/info)"""
    if len(context.args) < 1:
        await update.message.reply_text("لطفاً آیدی یا نام کاربری را وارد کنید. مثال: /info @username")
        return

    identifier = context.args[0]

    if identifier.startswith("@"):
        username = identifier[1:]
        cursor.execute("SELECT id, xp, level FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            await update.message.reply_text("کاربر موردنظر یافت نشد.")
            return
        user_id, xp, level = user[0], user[1], user[2]
    else:
        try:
            user_id = int(identifier)
            cursor.execute("SELECT username, xp, level FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("کاربر موردنظر یافت نشد.")
                return
            username, xp, level = user[0], user[1], user[2]
        except ValueError:
            await update.message.reply_text("لطفاً آیدی معتبر وارد کنید.")
            return

    user_info = f"👤 **مشخصات کاربر**:\n- نام کاربری: @{username}\n- آیدی: {user_id}\n- XP: {xp}\n- Level: {level}"

    try:
        profile_photos = await context.bot.get_user_profile_photos(user_id)
        photo = profile_photos.photos[0][0] if profile_photos.photos else None
        if photo:
            await update.message.reply_photo(photo.file_id, caption=user_info)
        else:
            await update.message.reply_text(user_info)
    except Exception as e:
        await update.message.reply_text(user_info)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور نمایش لیست برترین‌ها (/leaderboard)"""
    cursor.execute("SELECT username, level FROM users ORDER BY level DESC, xp DESC")
    users = cursor.fetchall()

    if not users:
        await update.message.reply_text("هیچ کاربری در ربات ثبت نشده است.")
        return

    leaderboard_text = "🏆 **لیست کاربران بر اساس سطح** 🏆\n"
    for i, (username, level) in enumerate(users, start=1):
        leaderboard_text += f"{i}. {username} - Level: {level}\n"

    await update.message.reply_text(leaderboard_text)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور مدیریت ادمین‌ها (/admin)"""
    requester_username = f"@{update.message.from_user.username}"
    if requester_username != SUPER_ADMIN_USERNAME:
        await update.message.reply_text("فقط سوپر ادمین می‌تواند ادمین‌ها را تعیین کند.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("لطفاً آیدی یا نام کاربری فرد را وارد کنید. مثال: /admin @username")
        return

    identifier = context.args[0]
    if identifier.startswith("@"):
        username = identifier[1:]
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    else:
        try:
            user_id = int(identifier)
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            username = user[0] if user else None
        except ValueError:
            await update.message.reply_text("لطفاً آیدی معتبر وارد کنید.")
            return

    if not user:
        await update.message.reply_text("کاربر موردنظر یافت نشد.")
        return

    user_id = user[0]
    cursor.execute("SELECT * FROM admins WHERE id = ?", (user_id,))
    admin = cursor.fetchone()

    if not admin:
        cursor.execute("INSERT INTO admins (id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        await update.message.reply_text(f"{username} اکنون ادمین است!")
    else:
        await update.message.reply_text(f"{username} قبلاً ادمین بوده است.")

async def addlevel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور افزودن سطح (/addlevel)"""
    requester_username = f"@{update.message.from_user.username}"
    if requester_username != SUPER_ADMIN_USERNAME:
        await update.message.reply_text("فقط سوپر ادمین می‌تواند سطح کاربران را تغییر دهد.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("لطفاً آیدی یا نام کاربری و مقدار Level را وارد کنید. مثال: /addlevel @username 2")
        return

    identifier = context.args[0]
    try:
        level_to_add = int(context.args[1])
    except ValueError:
        await update.message.reply_text("مقدار Level باید یک عدد صحیح باشد.")
        return

    if identifier.startswith("@"):
        username = identifier[1:]
        cursor.execute("SELECT id, level FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            await update.message.reply_text("کاربر موردنظر یافت نشد.")
            return
        user_id, current_level = user
    else:
        try:
            user_id = int(identifier)
            cursor.execute("SELECT level FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                await update.message.reply_text("کاربر موردنظر یافت نشد.")
                return
            current_level = user[0]
        except ValueError:
            await update.message.reply_text("لطفاً آیدی معتبر وارد کنید.")
            return

    new_level = max(1, current_level + level_to_add)
    cursor.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
    conn.commit()

    await update.message.reply_text(f"سطح جدید کاربر {identifier} تنظیم شد! سطح کنونی: {new_level}")

# ==============================================
# دستورات بازی سنگ، کاغذ، قیچی
# ==============================================

async def game1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ثبت گروه برای بازی (/game1)"""
    global group_id

    if update.message.chat.type in ["group", "supergroup"]:
        group_id = update.message.chat.id
        await update.message.reply_text("این گروه برای بازی ثبت شد! بازیکنان می‌توانند با دستور /join وارد شوند.")
    else:
        await update.message.reply_text("این دستور فقط در گروه‌ها قابل استفاده است!")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ورود به بازی (/join)"""
    global group_id

    if not group_id:
        await update.message.reply_text("ابتدا باید گروه با دستور /game1 ثبت شود!")
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"کاربر {user_id}"

    if len(players) >= 2:
        await update.message.reply_text("بازی قبلاً شروع شده است. فقط دو بازیکن می‌توانند شرکت کنند!")
        return

    if user_id not in players:
        players[user_id] = {"choice": None, "username": username}
        await update.message.reply_text(f"{username} وارد بازی شد! منتظر دستور شروع بازی باشید.")
    else:
        await update.message.reply_text("شما قبلاً وارد بازی شده‌اید!")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع بازی (/play)"""
    global group_id

    if not group_id:
        await update.message.reply_text("گروه ثبت نشده است! ابتدا دستور /game1 را اجرا کنید.")
        return

    if len(players) < 2:
        await update.message.reply_text("برای شروع بازی حداقل دو بازیکن لازم است! دستور /join را اجرا کنید.")
        return

    for user_id, player in players.items():
        keyboard = [
            [InlineKeyboardButton(choice, callback_data=f"choose:{user_id}:{choice}") for choice in choices]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=group_id,
            text=f"{player['username']}, لطفاً انتخاب خود را انجام دهید (سنگ، کاغذ، یا قیچی):",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های بازی"""
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    user_id = int(data[1])
    choice = data[2]

    if query.from_user.id != user_id:
        await query.answer(text="این دکمه برای شما نیست!", show_alert=True)
        return

    if players[user_id]["choice"] is None:
        players[user_id]["choice"] = choice
        await query.edit_message_text("انتخاب شما ثبت شد! منتظر نتایج بازی باشید.")
    else:
        await query.answer(text="شما قبلاً انتخاب خود را انجام داده‌اید!", show_alert=True)

    if all(player["choice"] is not None for player in players.values()):
        result = determine_winner()
        await context.bot.send_message(chat_id=group_id, text=result)

        for player in players.values():
            player["choice"] = None

def determine_winner():
    """تعیین برنده بازی"""
    user_ids = list(players.keys())
    player1 = players[user_ids[0]]
    player2 = players[user_ids[1]]

    choice1 = player1["choice"]
    choice2 = player2["choice"]

    if choice1 == choice2:
        return f"بازی مساوی شد! 🙌\nانتخاب هر دو: {choice1}"
    elif (choice1 == "سنگ 🪨" and choice2 == "قیچی ✂️") or \
         (choice1 == "قیچی ✂️" and choice2 == "کاغذ 📜") or \
         (choice1 == "کاغذ 📜" and choice2 == "سنگ 🪨"):
        winner_id = user_ids[0]
        random_xp = random.randint(1, 100)

        cursor.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (random_xp, winner_id))
        conn.commit()

        cursor.execute("SELECT xp FROM users WHERE id = ?", (winner_id,))
        xp = cursor.fetchone()[0]
        new_level = calculate_level(xp)

        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, winner_id))
        conn.commit()

        return f"بازیکن {player1['username']} برنده شد! 🎉\nامتیاز کسب شده: {random_xp}\nسطح جدید: {new_level}"
    else:
        winner_id = user_ids[1]
        random_xp = random.randint(1, 100)

        cursor.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (random_xp, winner_id))
        conn.commit()

        cursor.execute("SELECT xp FROM users WHERE id = ?", (winner_id,))
        xp = cursor.fetchone()[0]
        new_level = calculate_level(xp)

        cursor.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, winner_id))
        conn.commit()

        return f"بازیکن {player2['username']} برنده شد! 🎉\nامتیاز کسب شده: {random_xp}\nسطح جدید: {new_level}"

async def gamecancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو بازی (/gamecancel)"""
    global players, group_id

    if not group_id or len(players) == 0:
        await update.message.reply_text("هیچ بازی فعالی برای لغو وجود ندارد!")
        return

    players.clear()
    group_id = None
    await update.message.reply_text("بازی لغو شد و تمامی بازیکنان خارج شدند.")

# ==============================================
# راه‌اندازی اصلی ربات
# ==============================================

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # دستورات عمومی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^help$"))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    
    # دستورات مدیریتی
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addlevel", addlevel))
    
    # دستورات بازی
    app.add_handler(CommandHandler("game1", game1))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("gamecancel", gamecancel))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # پاسخ به پیام‌های متنی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_message))

    print("✅ ربات میکاسا با موفقیت راه‌اندازی شد!")
    app.run_polling()

if __name__ == "__main__":
    main()