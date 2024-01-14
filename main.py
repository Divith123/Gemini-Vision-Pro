from pathlib import Path
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters
import time
import requests

# Replace with your actual API key and bot token
GEMINI_VISION_PRO_API_KEY = 'gemini-vision-pro key'
GEMINI_VISION_PRO_ENDPOINT = 'https://api.geminivisionpro.com/v1/process'
TOKEN = 'bot token'

def send_typing_animation(context, user_id):
    context.bot.send_chat_action(chat_id=user_id, action="typing")

def send_spawning_animation(context, user_id):
    # Implement your spawning animation logic here
    pass

def process_image(file_info, context):
    try:
        image_url = file_info.file_path
        with requests.get(image_url, stream=True) as response:
            response.raise_for_status()
            image_data = response.content

            # Save the image locally with a specific name (optional)
            image_path = Path(f"image_{file_info.file_unique_id}.jpg")
            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)

            files = {'image': ('file.jpg', image_data, 'image/jpeg')}
            headers = {'x-api-key': GEMINI_VISION_PRO_API_KEY}
            response = requests.post(GEMINI_VISION_PRO_ENDPOINT, files=files, headers=headers)
            response.raise_for_status()
            return response.json()

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini Vision Pro API: {e}"

def message(update: Update, context):
    user_id = update.effective_chat.id

    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file_info = context.bot.get_file(photo.file_id)

            send_typing_animation(context, user_id)

            # Implement rate limiting with adjusted value
            elapsed_time = time.time() - context.user_data.get('last_request_time', 0)
            if elapsed_time < 1.0:  # Adjust this value as needed
                time.sleep(1.0 - elapsed_time)

            send_spawning_animation(context, user_id)

            result = process_image(file_info, context)
            context.bot.send_message(chat_id=user_id, text=f"Gemini: {result}")

        else:
            context.bot.send_message(chat_id=user_id, text="Please send an image for processing.")

    except requests.exceptions.RequestException as e:
        context.bot.send_message(chat_id=user_id, text=f"Error connecting to Gemini Vision Pro API: {e}")

    except Exception as e:
        context.bot.send_message(chat_id=user_id, text="An error occurred while processing the response.")
        print("Error:", e)

    finally:
        context.user_data['last_request_time'] = time.time()

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    message_handler = MessageHandler(Filters.photo, message)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
