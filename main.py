import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from pymongo import MongoClient

# --- DATABASE CONNECTION ---
MONGO_URL = "mongodb+srv://phyohtetaung1091_db_user:EhJoxfniB6uFq9OA@cluster0.nrja3ig.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['YeeSarSharDB']
users_col = db['users']

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- STATES ---
GENDER, AGE, CITY, PHOTO = range(4)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    existing_user = users_col.find_one({"user_id": user_id})
    
    if existing_user:
        await update.message.reply_text(
            f"မင်္ဂလာပါ {existing_user['name']}! ✨ လူသစ်များရှာဖွေဖို့ အောက်ကခလုတ်ကို နှိပ်ပါ။",
            reply_markup=ReplyKeyboardMarkup([['🔍 ရှာဖွေမည်']], resize_keyboard=True)
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🇲🇲 YeeSarShar မှ ကြိုဆိုပါတယ်!\nအနီးနားက အဖော်မွန်သစ်များကို အခမဲ့ ရှာဖွေနိုင်ပါတယ်။\n\nစတင်ရန် သင်က ဘယ်သူလဲ?",
        reply_markup=ReplyKeyboardMarkup([['ယောင်္ကျားလေး 👦', 'မိန်းကလေး 👧']], one_time_keyboard=True, resize_keyboard=True)
    )
    return GENDER

# --- REGISTRATION FLOW ---
async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("သင့်အသက်ကို ရိုက်ထည့်ပါ (ဥပမာ- ၂၀)။", reply_markup=ReplyKeyboardRemove())
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("သင်ဘယ်မြို့မှာ နေပါသလဲ?")
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("သင့်ရဲ့ ဓာတ်ပုံတစ်ပုံ ပို့ပေးပါ။ (ကိုယ်တိုင်ရိုက်ပုံဖြစ်ရပါမည်) 📸")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_id = update.message.photo[-1].file_id
    
    user_data = {
        "user_id": user.id,
        "name": user.first_name,
        "gender": context.user_data['gender'],
        "age": context.user_data['age'],
        "city": context.user_data['city'],
        "photo": photo_id,
        "seen_users": [] # ကြည့်ပြီးသားလူစာရင်း
    }
    users_col.update_one({"user_id": user.id}, {"$set": user_data}, upsert=True)
    
    await update.message.reply_text(
        "✅ မှတ်ပုံတင်ပြီးပါပြီ! အခုပဲ လူရှာလို့ရပါပြီ။",
        reply_markup=ReplyKeyboardMarkup([['🔍 ရှာဖွေမည်']], resize_keyboard=True)
    )
    return ConversationHandler.END

# --- AUTO MATCHMAKING (လူတစ်ယောက်ပြီးတစ်ယောက်ပြမည့်စနစ်) ---
async def search_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_user = users_col.find_one({"user_id": user_id})
    
    if not current_user:
        await update.message.reply_text("အရင်ဆုံး /start ကိုနှိပ်ပြီး မှတ်ပုံတင်ပေးပါ။")
        return

    seen = current_user.get("seen_users", [])
    # မိမိမဟုတ်သော၊ မကြည့်ရသေးသော လူကို Random တစ်ယောက်ဆွဲထုတ်ခြင်း
    query = {"user_id": {"$ne": user_id, "$nin": seen}}
    target = list(users_col.aggregate([{"$match": query}, {"$sample": {"size": 1}}]))
    
    if target:
        t = target[0]
        # ကြည့်ပြီးသားထဲ ထည့်လိုက်ခြင်း (ထပ်မပြတော့အောင်)
        users_col.update_one({"user_id": user_id}, {"$push": {"seen_users": t['user_id']}})
        
        caption = f"👤 နာမည်: {t['name']}\n🎂 အသက်: {t['age']}\n📍 မြို့: {t['city']}"
        await update.message.reply_photo(
            photo=t['photo'],
            caption=caption,
            reply_markup=ReplyKeyboardMarkup([['❤️ Like', '👎 Next']], resize_keyboard=True)
        )
    else:
        # လူကုန်သွားရင် အစကပြန်ပြဖို့ Seen list ကို ရှင်းပေးခြင်း
        users_col.update_one({"user_id": user_id}, {"$set": {"seen_users": []}})
        await update.message.reply_text("လောလောဆယ် လူကုန်သွားပါပြီ။ အစကနေ ပြန်ပတ်ပြပေးပါ့မယ်။ '🔍 ရှာဖွေမည်' ကို ပြန်နှိပ်ပါ။")

if __name__ == '__main__':
    TOKEN = "8529724118:AAH5DOSQ0Hc8OkB-a5WJVf6XPEVSvIVI-Lo"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex('^(🔍 ရှာဖွေမည်|❤️ Like|👎 Next)$'), search_people))

    print("YeeSarShar User-Edition is running...")
    app.run_polling()
