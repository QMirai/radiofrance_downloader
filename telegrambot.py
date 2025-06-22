from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import json

with open('token/token.json', 'r', encoding='utf-8') as f:
    my_token = json.load(f)['token']


def run_bot(message_queue):
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(f'Hello {update.effective_user.first_name}')

    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
        message = update.message.text
        if 'http' not in message:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="This is not a link.")
        else:
            message_queue.put(message)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your podcast is downloading.")

    app = ApplicationBuilder().token(my_token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    app.add_handler(start_handler)
    app.add_handler(echo_handler)
    app.run_polling()
