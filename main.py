import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# Error Log မှတ်တမ်းကြည့်ရန်
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# အဆင့်များကို သတ်မှတ်ခြင်း
GENDER, AGE, PHOTO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🇲🇲 YeeSarShar Bot မှ ကြိုဆိုပါတယ်!\n\n"
        "ဒီ Bot လေးဟာ မြန်မာလူမျိုးတွေအချင်းချင်း စိတ်တူကိုယ်တူ "
        "သူငယ်ချင်းအသစ်တွေ ရှာဖွေဖို့ သီးသန့်ဖြစ်ပါတယ်။\n\n"
        "စတင်ဖို့အတွက် သင်က ဘယ်သူလဲဆိုတာ အရင်ရွေးပေးပါဦး။"
    )
    reply_keyboard = [['ယောင်္ကျားလေး 👦', 'မိန်းကလေး 👧']]
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return GENDER

async def gender_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_gender = update.message.text
    context.user_data['gender'] = user_gender
    
    await update.message.reply_text(
        f"ဟုတ်ကဲ့ {user_gender} လေးခင်ဗျာ။\n\nသင့်ရဲ့ အသက်ကို ဂဏန်းနဲ့ (ဥပမာ- ၂၀) လို့ ရိုက်ထည့်ပေးပါဦး။",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AGE

async def age_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_age = update.message.text
    context.user_data['age'] = user_age
    
    await update.message.reply_text(
        "မှတ်တမ်းတင်လို့ ပြီးပါပြီ! ✅\n\n"
        "အခုဆိုရင် သင့်ကို စိတ်ဝင်စားမယ့်သူတွေဆီ သင့်ပရိုဖိုင်ကို ပို့ပေးတော့မှာဖြစ်ပါတယ်။ "
        "(မှတ်ချက် - နောက်အဆင့်မှာ ဓာတ်ပုံတင်ခြင်းနဲ့ လူရှာခြင်းတွေကို ထည့်သွင်းပေးသွားမှာပါ)"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bye! နောက်မှ ပြန်ဆုံကြမယ်။', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    # သင်ပေးထားတဲ့ Token ကို ဖြည့်စွက်ထားပါတယ်
    TOKEN = "8529724118:AAH5DOSQ0Hc8OkB-a5WJVf6XPEVSvIVI-Lo"
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # စကားပြောခန်း အဆင့်ဆင့် ထိန်းချုပ်ခြင်း
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(filters.Regex('^(ယောင်္ကျားလေး 👦|မိန်းကလေး 👧)$'), gender_choice)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    print("Bot is running...")
    application.run_polling()
