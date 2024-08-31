import logging
import subprocess
import re
import requests
import time
import subprocess
import json
import os
from cryptography.fernet import Fernet
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define states
# State definitions for ConversationHandler
PASSWORD, MAIN_MENU_DISPLAY, MAIN_MENU_HANDLER = range(3)
#TIMEOUT = 10

# Constants
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # Get from env variable, default to 0
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
DATA_FILE = 'user_data.json'
KEY_FILE = 'secret.key'
HOST_INFO_DIGEST_FILE = 'host_info_digest.txt'

# Generate a key for encryption
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)

# Load the encryption key
def load_key():
    return open(KEY_FILE, 'rb').read()

# Encrypt a password
def encrypt_password(password: str, key: bytes) -> str:
    fernet = Fernet(key)
    return fernet.encrypt(password.encode()).decode()

# Decrypt a password
def decrypt_password(encrypted_password: str, key: bytes) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

# Save user data to a file
def save_user_data(user_data):
    with open(DATA_FILE, 'w') as file:
        json.dump(user_data, file)

# Load user data from a file
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Command to add a new user
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You do not have permission to add users.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /adduser <username> <password>")
        return

    username, password = context.args
    user_id = 0

    key = load_key()
    encrypted_password = encrypt_password(password, key)

    user_data = load_user_data()

    user_data[username] = {
        'user_id': user_id,
        'password': encrypted_password
    }

    save_user_data(user_data)
    await update.message.reply_text(f"User {username} added successfully.")

# Command to remove a user
async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You do not have permission to remove users.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /removeuser <username>")
        return

    username = context.args[0]

    user_data = load_user_data()

    if username in user_data:
        del user_data[username]
        save_user_data(user_data)
        await update.message.reply_text(f"User {username} removed successfully.")
    else:
        await update.message.reply_text(f"User {username} not found.")
        
def extract_client_id(file_path):
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()

        pattern = r';client-id\s+([A-Za-z0-9]+)'
        match = re.search(pattern, content)
        # If a match is found, return the client-id
        if match:
            return match.group(1)
        else:
            return None

    except FileNotFoundError:
        logger.info(f"Error: The file at {file_path} was not found.")
        return None        

# Function to load the data when bot starts
def load_on_start():
    generate_key()
    return load_user_data()

def find_user_by_id(user_data, target_user_id):
    for username, details in user_data.items():
        if details.get("user_id") == target_user_id:
            return username
    if target_user_id == ADMIN_USER_ID:
            return "admin"
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the password."""
    try:
        # Check if the user is the admin
        logger.info(f"ADMIN_USER_ID = {ADMIN_USER_ID}")
        username = find_user_by_id(load_user_data(), update.effective_user.id)
        if username != None or update.effective_user.id == ADMIN_USER_ID:
            chat_id = update.effective_chat.id
            digest = make_digest()
            await context.bot.send_message(chat_id=chat_id, text=f"Welcome my dear friend: <b>{username}</b>!!!", parse_mode='HTML')
            # Send the digest to the admin
            await context.bot.send_message(chat_id=chat_id, text=f"{digest}", parse_mode='HTML')

            # Proceed to the main menu
            return await display_main_menu(update, context)

        # If the user is not the admin, ask for the password
        await update.message.reply_text("Please enter the password to access the bot:")
        return PASSWORD

    except Exception as e:
        # Log the error and notify the user
        logger.info(f"Error in start function: {e}")
        await update.message.reply_text(f"An error occurred. Please try again later. {e}")
        return ConversationHandler.END  # End the conversation on error

def get_host_info_digest():
    # Get the CPU temperature using the vcgencmd command
    try:
      temp_output = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
      temp = float(temp_output.split('=')[1].split("'")[0])
      return f'CPU Temperature: {temp}\n'
    except Exception as e:
      return ""
      

def make_digest():
    public_ip = fetch_public_ip()
    host_info_digest = get_host_info_digest()
    return (
        f'---------------------------------------------\n'
        f'<b>My public IP address is:</b> {public_ip}\n'
        f'{host_info_digest}'
        f'\n'
        f'------------------admin section--------------\n'
        f'<b>Usage: /adduser &lt;username&gt; &lt;password&gt</b>\n'
        f'<b>Usage: /deluser &lt;username&gt</b>\n'
        f'---------------------------------------------\n'
    )

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Checks if the entered password is correct."""
    key = load_key()    
    user_input = update.message.text
    user_data = load_user_data()

    for username, details in user_data.items():
        decrypted_password = decrypt_password(details['password'], key)
        if user_input == decrypted_password:
            chat_id = update.effective_chat.id
            if user_data[username]['user_id'] != 0 and user_data[username]['user_id'] != chat_id:
                await update.message.reply_text("You have been binded to another telegram id. Stop cheating")
                return PASSWORD
            # If the password matches, save the user ID
                        
            user_data[username]['user_id'] = chat_id
            save_user_data(user_data)

            # Proceed with the original logic
            digest = make_digest()
            #context.job_queue.run_once(timeout, TIMEOUT, chat_id=chat_id)
            await context.bot.send_message(chat_id=chat_id, text=f"{digest}", parse_mode='HTML')
            return await display_main_menu(update, context)

    # If no password matches
    await update.message.reply_text("Incorrect password. Please try again.")
    return PASSWORD
        
async def display_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Get openvpn file','Get digest', 'Quit']]
    await update.message.reply_text(
        '<b>Please choose an option:</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return MAIN_MENU_HANDLER

#async def timeout(context: ContextTypes.DEFAULT_TYPE):
#    """Handles the timeout when the conversation is inactive."""
#    job = context.job
#    chat_id = job.chat_id

#    await context.bot.send_message(chat_id=chat_id, text="Time's up! The conversation is now canceled.")

#    # Optionally, you can send a start button to restart the conversation
#    keyboard = [
#        [InlineKeyboardButton("Start", callback_data='start')]
#    ]
#    reply_markup = InlineKeyboardMarkup(keyboard)
#
#    await context.bot.send_message(chat_id=chat_id, text="Press 'Start' to begin again.", reply_markup=reply_markup)

def fetch_public_ip():
    """Fetches the public IP address."""
    try:
        response = requests.get('https://ifconfig.me')
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Error occurred: {e}"

async def get_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fetches the public IP address and sends it to the user."""
    digest = make_digest()
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=f"{digest}", parse_mode='HTML')
    return await display_main_menu(update,context)

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user choice from the main menu."""
    user_choice = update.message.text
    chat_id = update.effective_chat.id

    if user_choice == 'Get digest':
        return await get_digest(update, context)
    elif user_choice == 'Get openvpn file':
        username = find_user_by_id(load_user_data(), update.effective_user.id)
        
        await context.bot.send_message(chat_id=chat_id, text=f"Please waiting... the ovpn file for precious friend <b>{username}</b> is being prepared", parse_mode='HTML')        
        try:
            file_path = f'userfiles/{username}.ovpn'
            client_ovpn_id = extract_client_id(file_path)
            if None != client_ovpn_id:
                remove_old_command = f'docker exec -i openvpn-running ./rmclient.sh {client_ovpn_id}'
                #should i manually remove the user folder
                result = subprocess.run(remove_old_command, shell=True, text=True, capture_output=True, check=True)
                logger.info(f"Remove old generated ovpn for {username} [{client_ovpn_id}]: {result}")
            command = f'docker exec -i openvpn-running ./genclient.sh o>userfiles/{username}.ovpn'
            result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            logger.info(f"Make new generated ovpn for {username}: {result}")              
            # Open the file and send it
            with open(file_path, 'rb') as file:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename=f'{username}.ovpn')
            return await get_digest(update, context)
        except subprocess.CalledProcessError as e:
            message = e.stderr
            await context.bot.send_message(chat_id=chat_id, text=f"Error {message}", parse_mode='HTML')
        return await get_digest(update, context)
    elif user_choice == 'Quit':
        await update.message.reply_text("Goodbye! You have exited the bot.", reply_markup=ReplyKeyboardMarkup([[]]))
        return ConversationHandler.END  # End the conversation
    else:
        await update.message.reply_text("Unknown option. Please choose again.")
        return await get_digest(update, context)
        
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    logger.error("------This is an error message--------")
    load_on_start()
    os.makedirs("userfiles", exist_ok=True)
    
    logger.info(f'Telegram bot token >{TELEGRAM_BOT_TOKEN}<')
    application = Application.builder().token(f'{TELEGRAM_BOT_TOKEN}').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            MAIN_MENU_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            MAIN_MENU_DISPLAY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, display_main_menu)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('adduser', add_user))
    application.add_handler(CommandHandler('deluser', remove_user))
    
    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    application.run_polling()

#start
if __name__ == '__main__':
    main()

