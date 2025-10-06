import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import os
from dotenv import load_dotenv

# Environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Excel fayl nomi
EXCEL_FILE = "talabalar.xlsx"

# Talabalar ma'lumotlarini Excel fayldan yuklash
def load_student_data():
    try:
        # Excel faylni o'qish
        df = pd.read_excel(EXCEL_FILE)
        
        # Majburiy ustunlarni tekshirish
        required_columns = ['passport_id', 'full_name', 'faculty', 'group_name', 'group_link']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Excel faylda '{col}' ustuni topilmadi")
        
        # Passport ID larni string ga o'tkazish va katta harflarga
        df['passport_id'] = df['passport_id'].astype(str).str.upper().str.strip()
        
        return df
    
    except FileNotFoundError:
        logging.error(f"Excel fayl topilmadi: {EXCEL_FILE}")
        
        # Namuna Excel fayl yaratish
        create_sample_excel()
        return load_student_data()
    
    except Exception as e:
        logging.error(f"Excel faylni o'qishda xato: {e}")
        return None

# Namuna Excel fayl yaratish
def create_sample_excel():
    sample_data = {
        'passport_id': ['AB1234567', 'CD9876543', 'EF5555555', 'GH1111111', 'IJ2222222'],
        'full_name': [
            'Ali Valiyev',
            'Gulnora Xasanova', 
            'Shoxrux Qodirov',
            'Dilnoza Karimova',
            'Javohir Tursunov'
        ],
        'faculty': [
            'Dasturiy injiniring fakulteti',
            'Axborot texnologiyalari fakulteti', 
            'Telekommunikatsiya fakulteti',
            'Iqtisodiyot fakulteti',
            'Tibbiyot fakulteti'
        ],
        'group_name': [
            'DI-21-01',
            'AT-20-02', 
            'TK-22-01',
            'IQ-19-03',
            'TB-21-02'
        ],
        'group_link': [
            'https://t.me/di2101_group',
            'https://t.me/at2002_group',
            'https://t.me/tk2201_group', 
            'https://t.me/iq1903_group',
            'https://t.me/tb2102_group'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    logging.info("Namuna Excel fayl yaratildi")

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum! 🤖\n"
        "Talaba ma'lumotlari botiga xush kelibsiz!\n\n"
        "📝 **Passport ID raqamingizni yuboring**, men sizga:\n"
        "• 👤 To'liq ism-familiyangiz\n" 
        "• 🏛️ Fakultetingiz\n"
        "• 📚 Guruh nomingiz\n"
        "• 🔗 Guruh linkingiz\n\n"
        "📍 **Namuna:** AB1234567\n\n"
        "⚠️ Iltimos, passport ID ni to'g'ri kiriting!"
    )

# Help komandasi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ **Yordam:**\n\n"
        "1. /start - Botni ishga tushirish\n"
        "2. Passport ID raqamingizni yuboring\n"
        "3. Bot sizga to'liq ma'lumotlaringizni yuboradi\n\n"
        "📍 **Namuna:** AB1234567\n\n"
        "📞 Muammo bo'lsa, administrator bilan bog'laning"
    )

# Passport ID ni qayta ishlash
async def handle_passport_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    passport_id = update.message.text.upper().strip()
    
    # Ma'lumotlarni yuklash
    df = load_student_data()
    
    if df is None:
        await update.message.reply_text(
            "❌ Ma'lumotlar bazasida muammo yuzaga keldi. "
            "Iltimos, keyinroq urinib ko'ring yoki administrator bilan bog'laning."
        )
        return
    
    # Passport ID ni qidirish
    student_data = df[df['passport_id'] == passport_id]
    
    if not student_data.empty:
        student = student_data.iloc[0]
        full_name = student['full_name']
        faculty = student['faculty']
        group_name = student['group_name']
        group_link = student['group_link']
        
        # Asosiy javob
        response_text = (
            f"✅ **Ma'lumot topildi!**\n\n"
            f"👤 **To'liq ism:** {full_name}\n"
            f"📋 **Passport ID:** {passport_id}\n"
            f"🏛️ **Fakultet:** {faculty}\n"
            f"📚 **Guruh:** {group_name}\n"
            f"🔗 **Guruh linki:** {group_link}"
        )
        
        await update.message.reply_text(response_text)
        
        # Guruh linkini alohida yuborish (qulaylik uchun)
        await update.message.reply_text(
            f"📲 **Guruhga o'tish uchun quyidagi linkni bosing:**\n{group_link}"
        )
        
    else:
        await update.message.reply_text(
            f"❌ Kechirasiz, **{passport_id}** raqamli talaba topilmadi.\n\n"
            f"🔍 **Tekshirish uchun:**\n"
            f"• Passport ID ni to'g'ri kiritganingizni tekshiring\n"
            f"• Katta-kichik harflar farqi yo'q\n"
            f"• Ortiqcha bo'sh joy qoldirmang\n\n"
            f"📞 Agar muammo davom etsa, administrator bilan bog'laning."
        )

# Fakultet bo'yicha qidirish
async def faculty_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🏛️ **Fakultet bo'yicha qidirish:**\n"
            "Namuna: /faculty Dasturiy injiniring\n"
            "Yoki: /faculty Iqtisodiyot"
        )
        return
    
    faculty_query = ' '.join(context.args).lower()
    df = load_student_data()
    
    if df is not None:
        # Fakultet nomi bo'yicha qidirish
        results = df[df['faculty'].str.lower().str.contains(faculty_query, na=False)]
        
        if not results.empty:
            response = f"🏛️ **Fakultet qidiruvi:** '{faculty_query}'\n"
            response += f"📊 Topilgan talabalar: {len(results)} ta\n\n"
            
            for _, student in results.iterrows():
                response += (
                    f"👤 {student['full_name']}\n"
                    f"📋 {student['passport_id']}\n"
                    f"📚 {student['group_name']}\n"
                    f"🔗 {student['group_link']}\n"
                    f"────────────────────\n"
                )
            
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(f"❌ '{faculty_query}' fakulteti bo'yicha talaba topilmadi")
    else:
        await update.message.reply_text("❌ Ma'lumotlar bazasida muammo")

# Guruh bo'yicha qidirish
async def group_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📚 **Guruh bo'yicha qidirish:**\n"
            "Namuna: /group DI-21-01\n"
            "Yoki: /group AT-20-02"
        )
        return
    
    group_query = ' '.join(context.args).upper()
    df = load_student_data()
    
    if df is not None:
        # Guruh nomi bo'yicha qidirish
        results = df[df['group_name'].str.upper().str.contains(group_query, na=False)]
        
        if not results.empty:
            response = f"📚 **Guruh qidiruvi:** '{group_query}'\n"
            response += f"📊 Topilgan talabalar: {len(results)} ta\n\n"
            
            for _, student in results.iterrows():
                response += (
                    f"👤 {student['full_name']}\n"
                    f"📋 {student['passport_id']}\n"
                    f"🏛️ {student['faculty']}\n"
                    f"🔗 {student['group_link']}\n"
                    f"────────────────────\n"
                )
            
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(f"❌ '{group_query}' guruhi bo'yicha talaba topilmadi")
    else:
        await update.message.reply_text("❌ Ma'lumotlar bazasida muammo")

# Barcha talabalarni ko'rish
async def all_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_student_data()
    
    if df is not None:
        total_students = len(df)
        
        response = f"📊 **Barcha talabalar ro'yxati:**\n"
        response += f"👥 Jami: {total_students} ta talaba\n\n"
        
        # Faqat birinchi 15 ta talabani ko'rsatish
        for i, (_, student) in enumerate(df.head(15).iterrows()):
            response += (
                f"{i+1}. {student['full_name']}\n"
                f"   📋 {student['passport_id']}\n"
                f"   🏛️ {student['faculty']}\n"
                f"   📚 {student['group_name']}\n"
                f"   ──────────────────\n"
            )
        
        if total_students > 15:
            response += f"\n... va yana {total_students - 15} ta talaba"
        
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Ma'lumotlar bazasida muammo")

# Guruh linklari ro'yxati
async def group_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_student_data()
    
    if df is not None:
        # Har bir guruhdan faqat bitta namuna olish
        unique_groups = df.drop_duplicates(subset=['group_name'])
        
        response = "🔗 **Barcha guruh linklari:**\n\n"
        
        for _, group in unique_groups.iterrows():
            response += (
                f"📚 {group['group_name']}\n"
                f"🏛️ {group['faculty']}\n"
                f"🔗 {group['group_link']}\n"
                f"────────────────────\n"
            )
        
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Ma'lumotlar bazasida muammo")

# Admin komandasi - statistikalar
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_student_data()
    
    if df is not None:
        total_students = len(df)
        faculties = df['faculty'].nunique()
        groups = df['group_name'].nunique()
        
        await update.message.reply_text(
            f"📊 **Bot statistikasi:**\n\n"
            f"👥 Jami talabalar: {total_students}\n"
            f"🏛️ Fakultetlar soni: {faculties}\n"
            f"📚 Guruhlar soni: {groups}\n"
            f"📁 Ma'lumotlar manbai: Excel fayl"
        )
    else:
        await update.message.reply_text("❌ Statistikani yuklab bo'lmadi")

# Xato xabarlarni qayta ishlash
async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Iltimos, faqat passport ID raqamingizni yuboring.\n"
        "📍 **Namuna:** AB1234567\n\n"
        "ℹ️ Yordam olish uchun /help buyrug'ini yuboring"
    )

def main():
    # Bot ilovasini yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("faculty", faculty_search))
    application.add_handler(CommandHandler("group", group_search))
    application.add_handler(CommandHandler("all", all_students))
    application.add_handler(CommandHandler("links", group_links))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_passport_id))
    application.add_handler(MessageHandler(filters.ALL, handle_unknown))
    
    # Botni ishga tushirish
    print("🤖 Bot ishga tushdi...")
    print(f"📊 Excel fayl: {EXCEL_FILE}")
    print("📋 Mavjud ustunlar: passport_id, full_name, faculty, group_name, group_link")
    application.run_polling()

if __name__ == '__main__':
    main()
