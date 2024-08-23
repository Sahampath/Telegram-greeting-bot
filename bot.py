from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Dictionary to store custom greetings and image IDs per group
group_greetings = {}
group_images = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! Use /setgreeting <message> or upload an image to set a custom greeting for this group.")

def setgreeting(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if context.args:
        greeting = ' '.join(context.args)
        group_greetings[chat_id] = greeting
        
        # Show a preview of the greeting message
        preview_message = f"Sample Greeting: {greeting} [User]!"
        
        if chat_id in group_images:
            # Send a sample with image
            image_id = group_images[chat_id]
            context.bot.send_photo(chat_id=update.message.from_user.id, photo=image_id, caption=preview_message)
        else:
            # Send a sample without image
            update.message.reply_text(preview_message)
        
        update.message.reply_text(f"Custom greeting set to: {greeting}")
    else:
        update.message.reply_text("Please provide a message for the greeting.")

def handle_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    file_id = update.message.photo[-1].file_id  # Get the highest quality photo
    group_images[chat_id] = file_id
    update.message.reply_text("Custom greeting image set.")

def greet_new_member(update: Update, context: CallbackContext) -> None:
    # Check if there are new chat members
    new_members = update.message.new_chat_members
    if new_members:
        for member in new_members:
            chat_id = update.message.chat_id
            user = member.first_name
            greeting = group_greetings.get(chat_id, "Welcome to the group!")
            image_id = group_images.get(chat_id, None)
            
            if image_id:
                # Send the image with the greeting
                context.bot.send_photo(chat_id=chat_id, photo=image_id, caption=f"{greeting} {user}!")
            else:
                # Send text only if no image is set
                update.message.reply_text(f"{greeting} {user}!")

def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("setgreeting", setgreeting))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_new_member))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
