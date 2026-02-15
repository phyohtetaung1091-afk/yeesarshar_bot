import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# Logging ကို သတ်မှတ်ခြင်း
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# State အဆင့်ဆင့်သတ်မှတ်ချက်များ
GENDER, AGE, CITY, PHOTO, DISCOVERY = range(5)

# အချက်အလက်သိမ်းဆည်းရန် (လောလောဆယ် Temporary Database အဖြစ်သုံးထားသည်)
users_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['ယောင်္ကျားလေး 👦', 'မိန်းကလေး 👧']]
    await update.message.reply_text(
        "🇲🇲 YeeSarShar (YSS) မှ ကြိုဆိုပါတယ်!\n\n"
        "စတင်ဖို့အတွက် သင်က ဘယ်သူလဲဆိုတာ အရင်ရွေးပေးပါဦး။",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("သင့်အသက်ကို ဂဏန်းနဲ့ ရိုက်ထည့်ပေးပါ (ဥပမာ- ၂၀)။", reply_markup=ReplyKeyboardRemove())
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("သင်ဘယ်မြို့မှာ နေပါသလဲ? (ဥပမာ- ရန်ကုန်)။")
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("နောက်ဆုံးအဆင့်အနေနဲ့ သင့်ရဲ့ ဓာတ်ပုံတစ်ပုံ ပို့ပေးပါ။ 📸")
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id
    
    # User အချက်အလက်သိမ်းခြင်း
    users_db[user.id] = {
        'name': user.first_name,
        'gender': context.user_data['gender'],
        'age': context.user_data['age'],
        'city': context.user_data['city'],
        'photo': photo_file_id
    }
    
    await update.message.reply_text("✅ မှတ်ပုံတင်ပြီးပါပြီ! အခု တခြားသူတွေကို စတင်ရှာဖွေလို့ရပါပြီ။")
    return await show_someone(update, context)

async def show_someone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_user_id = update.effective_user.id
    target_user = None
    
    # မိမိမဟုတ်သော တခြားသူတစ်ယောက်ကို ရှာခြင်း
    for uid, data in users_db.items():
        if uid != current_user_id:
            target_user = data
            break
            
    if target_user:
        caption = f"👤 နာမည်: {target_user['name']}\n🎂 အသက်: {target_user['age']}\n📍 မြို့: {target_user['city']}"
        reply_keyboard = [['❤️ Like', '👎 Next']]
        await update.message.reply_photo(
            photo=target_user['photo'],
            caption=caption,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        )
        return DISCOVERY
    else:
        await update.message.reply_text("လောလောဆယ် လူအသစ်မရှိသေးပါဘူး။ ခဏနေမှ ပြန်လာခဲ့ပါ! /start ကို ပြန်နှိပ်နိုင်ပါတယ်။")
        return ConversationHandler.END

async def handle_discovery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == '❤️ Like':
        await update.message.reply_text("သဘောကျကြောင်း အကြောင်းကြားလိုက်ပါပြီ! 🥰")
    
    return await show_someone(update, context)

if __name__ == '__main__':
    TOKEN = "8529724118:AAH5DOSQ0Hc8OkB-a5WJVf6XPEVSvIVI-Lo"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            DISCOVERY: [MessageHandler(filters.Regex('^(❤️ Like|👎 Next)$'), handle_discovery)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    print("Bot starting...")
    app.run_polling()
