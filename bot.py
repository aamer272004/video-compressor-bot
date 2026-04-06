import os, subprocess, asyncio, nest_asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
nest_asyncio.apply()
API_ID = 35816853
API_HASH = "a9bfcd6d0b9a13c1dd4397b8509ba5db"
BOT_TOKEN = "8762180978:AAExPp9UESEiRAclfYQ762HrzyEWrRSUnrs"

app = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاموس لحفظ الفيديوهات لكل مستخدم
user_videos = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("✅ البوت المطور جاهز! أرسل الفيديو الآن وسأقوم بضغطه بدون أخطاء.")

@app.on_message(filters.video | filters.document)
async def handle_video(client, message):
    media = message.video or message.document
    if hasattr(media, 'mime_type') and not media.mime_type.startswith("video/"): return
    
    # حفظ معرف الملف الخاص بالمستخدم
    user_videos[message.from_user.id] = media.file_id
    
    buttons = [[
        InlineKeyboardButton("📉 ضغط قوي", callback_data="low"),
        InlineKeyboardButton("⚖️ متوازن", callback_data="mid"),
        InlineKeyboardButton("🎥 جودة عالية", callback_data="high")
    ]]
    await message.reply_text("📥 تم استلام الفيديو. اختر الجودة المطلوبة للبدء:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def process_video(client, callback_query):
    quality = callback_query.data
    user_id = callback_query.from_user.id
    file_id = user_videos.get(user_id)
    
    if not file_id:
        await callback_query.message.edit_text("❌ لم يتم العثور على الفيديو، يرجى إرساله مرة أخرى.")
        return

    msg = await callback_query.message.edit_text("⏳ جاري التحميل والضغط... يرجى عدم إرسال شيء آخر.")
    
    # تحديد مسارات ثابتة وواضحة
    base_path = os.path.expanduser("~/video_compressor_bot")
    input_p = os.path.join(base_path, f"in_{user_id}.mp4")
    output_p = os.path.join(base_path, f"out_{user_id}.mp4")

    try:
        # تحميل الملف والانتظار حتى ينتهي
        downloaded_file = await client.download_media(file_id, file_name=input_p)
        
        if not os.path.exists(input_p):
            raise Exception("فشل تحميل الملف إلى الذاكرة.")

        # إعدادات الضغط
        crf = {"low": "32", "mid": "28", "high": "24"}[quality]
        # أمر ffmpeg مع استخدام المسارات الكاملة
        cmd = f"ffmpeg -i '{input_p}' -vcodec libx264 -crf {crf} -preset veryfast '{output_p}' -y"
        
        process = await asyncio.create_subprocess_shell(cmd)
        await process.communicate()

        if os.path.exists(output_p):
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=output_p,
                caption="✨ تم الضغط بنجاح بواسطة النسخة المطورة!"
            )
            await msg.delete()
        else:
            await callback_query.message.edit_text("❌ فشل عملية الضغط، يرجى تجربة جودة أخرى.")

    except Exception as e:
        await callback_query.message.edit_text(f"❌ حدث خطأ تقني: {str(e)}")
    finally:
        # تنظيف الملفات بعد الانتهاء
        for f in [input_p, output_p]:
            if os.path.exists(f): os.remove(f)
async def start_bot():
    await app.start()
    print("--- البوت بدأ العمل الآن بنجاح ---")
    await asyncio.Event().wait()
if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass




