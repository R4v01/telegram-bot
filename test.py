import random
import time
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8675289775:AAH-CtOLEt2AVt0Vzw3eMH3ezKHcIWOOO98"

cooldowns = {}
COOLDOWN = 5

# 🟢 circle avatar
def make_circle(img_path, size=(260, 260)):
    img = Image.open(img_path).resize(size).convert("RGBA")

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    img.putalpha(mask)
    return img

# 🖼️ create image
def create_image(img1, img2, name1, name2, percent):
    bg = Image.open("template.jpg").convert("RGBA")

    p1 = make_circle(img1)
    p2 = make_circle(img2)

    bg.paste(p1, (100, 160), p1)
    bg.paste(p2, (540, 160), p2)

    draw = ImageDraw.Draw(bg)

    font_big = ImageFont.truetype("font.ttf", 40)
    font_small = ImageFont.truetype("font.ttf", 30)

    draw.line((300, 300, 540, 300), fill="white", width=6)
    draw.text((400, 260), f"❤️ {percent}%", fill="white", font=font_small)

    draw.text((120, 440), name1, fill="white", font=font_big)
    draw.text((560, 440), name2, fill="white", font=font_big)

    draw.text((320, 550), f"{percent}% LOVE", fill="yellow", font=font_big)

    output = "result.png"
    bg.save(output)
    return output

# 🎯 handler
async def love_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text not in ["kapl", "قل"]:
        return

    user_id = update.message.from_user.id

    # ⏱ cooldown
    if user_id in cooldowns:
        if time.time() - cooldowns[user_id] < COOLDOWN:
            await update.message.reply_text("⏳ تکایە چاوەڕێ بکە...")
            return

    cooldowns[user_id] = time.time()

    chat = update.effective_chat

    members = []
    async for m in context.bot.get_chat_administrators(chat.id):
        members.append(m.user)

    if len(members) < 2:
        await update.message.reply_text("❌ ئەندام نیە")
        return

    u1, u2 = random.sample(members, 2)

    name1 = u1.first_name
    name2 = u2.first_name

    percent = random.randint(50, 100)

    # 📸 download photos
    p1 = await context.bot.get_user_profile_photos(u1.id, limit=1)
    p2 = await context.bot.get_user_profile_photos(u2.id, limit=1)

    if not p1.photos or not p2.photos:
        await update.message.reply_text("❌ وێنە نەدۆزرایەوە")
        return

    file1 = await context.bot.get_file(p1.photos[0][-1].file_id)
    file2 = await context.bot.get_file(p2.photos[0][-1].file_id)

    await file1.download_to_drive("u1.jpg")
    await file2.download_to_drive("u2.jpg")

    result = create_image("u1.jpg", "u2.jpg", name1, name2, percent)

    msg = f"""
کەپڵەکان دیاری کران 💍🌚 :
━━━━━━━━━━━━━━━━━━
<a href="tg://user?id={u1.id}">{name1}</a> + 🖤 + <a href="tg://user?id={u2.id}">{name2}</a> = ❣️
━━━━━━━━━━━━━━━━━━
💘 {percent}% خۆشەویستی
پیرۆزە 😂🎉
"""

    await update.message.reply_photo(
        photo=InputFile(result),
        caption=msg,
        parse_mode="HTML"
    )

# ▶️ run
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, love_handler))

print("🔥 BotFather Kurdish Love Bot running...")
app.run_polling()