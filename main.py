import os
import telebot
import google.generativeai as genai
from PIL import Image

# Configuración
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
# Pon 0 o 1 temporalmente, luego lo cambiaremos con el ID real de tu tema
ID_TEMA_PERMITIDO = 1 

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.ImageGenerationModel("imagen-3")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    thread_id = message.message_thread_id
    chat_id = message.chat.id
    
    # Imprime el ID en la consola para que lo veas en Render
    print(f"Mensaje recibido en el tema ID: {thread_id}")

    if thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    status = bot.send_message(chat_id, "🎨 Dibujando...", message_thread_id=thread_id)
    
    try:
        result = model.generate_images(prompt=prompt)
        path = f"img_{chat_id}.png"
        result.images[0].save(path)
        
        with open(path, "rb") as photo:
            bot.send_photo(chat_id, photo, message_thread_id=thread_id)
        
        os.remove(path)
        bot.delete_message(chat_id, status.message_id)
    except Exception as e:
        print(f"Error: {e}")

print("Bot iniciado...")
bot.infinity_polling()
