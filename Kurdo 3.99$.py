import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_cards(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if not is_user_authorized(chat_id):
        context.bot.send_message(chat_id=chat_id, text="❌ You are not authorized to use this bot.")
        return

    # Assuming user sends card details in a single message
    cards = update.message.text.splitlines()
    
    results = []
    max_workers = 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(validate_card, card): card for card in cards}
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing card: {str(e)}")
                results.append(f"⚠️ Error processing card {futures[future]}")

    for res in results:
        context.bot.send_message(chat_id=chat_id, text=res)
