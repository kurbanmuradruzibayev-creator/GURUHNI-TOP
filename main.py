import logging
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# .env faylidan tokenni o'qish
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Excel faylini o'qish
try:
    df = pd.read_excel("talabalar.xlsx")
except FileNotFoundError:
    logger.error("talabalar.xlsx fayli topilmadi!")
    raise FileNotFoundError("talabalar.xlsx fayli loyiha papkasida bo'lishi kerak!")

# Excel'dan ma'lumotlarni lug'atga aylantirish
# Ustunlar: passport_num (str), group_name (str), group_link (str)
STUDENT_GROUPS = {
    row["passport_num"]: (row["group_name"], row["group_link"])
    for _, row in df.iterrows()
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /start buyrug'i uchun handler """
    await update.message.reply_text(
        "Assalomu alaykum! Talaba guruhi botiga xush kelibsiz. 👋\n\n"
        "Sizning passport raqamingizni yuboring (masalan: AA1234567).\n"
        "Men sizning guruhingizni topib, Telegram linkini yuboraman.\n\n"
        "Eslatma: Bu demo bot. Haqiqiy ma'lumotlar uchun admin bilan bog'laning."
    )

async def handle_passport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Passport raqamini qayta ishlash """
    passport_num = update.message.text.strip().upper()  # Katta harflarga o'tkazish
    
    if passport_num in STUDENT_GROUPS:
        group_name, group_link = STUDENT_GROUPS[passport_num]
        message = f"✅ Topildi!\n\nGuruhingiz: {group_name}\n\nGuruhga qo'shilish: {group_link}"
    else:
        message = "❌ Kechirasiz, bunday passport raqami topilmadi. Iltimos, to'g'ri raqamni yuboring yoki admin @admin_username bilan bog'laning."
    
    await update.message.reply_text(message)

def main() -> None:
    """ Botni ishga tushirish """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN .env faylida topilmadi!")
        raise ValueError("Iltimos, .env faylida BOT_TOKEN ni sozlang.")
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_passport))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
