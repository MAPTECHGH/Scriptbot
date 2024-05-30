import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin user ID (replace with the actual admin user ID)
ADMIN_ID = 123456789

# Dictionary to store user access levels and expiration times
user_access = {}

# Dictionary to store available access levels and their durations
access_levels = {}

# Dictionary to store codes
stored_codes = []

# Command to start the bot
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /grant <code> to get access. Admin commands: /create_level <level> <days>, /delete_level <level>, /store_code <code>. Use /view_codes to see stored codes.')

# Command for the admin to create access levels
def create_level(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    level = context.args[0] if len(context.args) > 0 else None
    days = int(context.args[1]) if len(context.args) > 1 else None

    if level and days:
        access_levels[level] = days
        update.message.reply_text(f"Access level '{level}' created with a duration of {days} days.")
    else:
        update.message.reply_text("Usage: /create_level <level> <days>")

# Command for the admin to delete access levels
def delete_level(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    level = context.args[0] if len(context.args) > 0 else None

    if level and level in access_levels:
        del access_levels[level]
        update.message.reply_text(f"Access level '{level}' deleted.")
    else:
        update.message.reply_text("Usage: /delete_level <level>")

# Command to grant access based on a code
def grant(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    code = context.args[0] if len(context.args) > 0 else None

    if code == "your_secret_code":  # Replace with your logic to validate codes
        # Here we assume the code corresponds to an access level
        access_level = "premium"  # Modify this based on your logic to map code to access level
        if access_level in access_levels:
            duration = access_levels[access_level]
            expiration = datetime.now() + timedelta(days=duration)
            user_access[user.id] = {"level": access_level, "expires": expiration}
            update.message.reply_text(f"Access granted! Level: {access_level}, Expires: {expiration}")
        else:
            update.message.reply_text("Invalid access level.")
    else:
        update.message.reply_text("Invalid code.")

# Command to check access
def check_access(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    access = user_access.get(user.id, {"level": "none", "expires": None})
    
    if access["expires"] and datetime.now() > access["expires"]:
        access = {"level": "none", "expires": None}
        user_access[user.id] = access

    update.message.reply_text(f"Your access level is {access['level']}. Expires: {access['expires']}")

# Command for the admin to store codes
def store_code(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    code = ' '.join(context.args) if len(context.args) > 0 else None

    if code:
        stored_codes.append(code)
        update.message.reply_text(f"Code '{code}' stored.")
    else:
        update.message.reply_text("Usage: /store_code <code>")

# Command for users to view stored codes if they have access
def view_codes(update: Update, _: CallbackContext) -> None:
    user = update.message.from_user
    access = user_access.get(user.id, {"level": "none", "expires": None})

    if access["level"] != "none" and access["expires"] and datetime.now() <= access["expires"]:
        if stored_codes:
            codes_message = "\n".join(stored_codes)
            update.message.reply_text(f"Stored codes:\n{codes_message}")
        else:
            update.message.reply_text("No codes stored.")
    else:
        update.message.reply_text("You do not have access to view the codes.")

# Command to handle unknown messages
def unknown(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Sorry, I didn't understand that command.")

def main() -> None:
    # Create the Updater and pass it your bot's token
    updater = Updater("YOUR_BOT_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("grant", grant))
    dispatcher.add_handler(CommandHandler("check_access", check_access))
    dispatcher.add_handler(CommandHandler("create_level", create_level))
    dispatcher.add_handler(CommandHandler("delete_level", delete_level))
    dispatcher.add_handler(CommandHandler("store_code", store_code))
    dispatcher.add_handler(CommandHandler("view_codes", view_codes))

    # Add a handler for unknown messages
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
