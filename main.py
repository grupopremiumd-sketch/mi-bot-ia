import os
import telebot
import google.generativeai as genai
from PIL import Image
from flask import Flask
import threading
import time

# --- SERVIDOR WEB ---
app = Flask('')
@app.route('/')
def home():
    return "Bot Activo y Saludable"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Deja el 1 por ahora para detectar tu ID de tema en los logs
ID_TEMA_PERMITIDO = 1  

genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Esto te dirá el ID real en los logs de Render
    print(f"DEBUG: Mensaje recibido en el tema ID: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Generando imagen con Imagen 3...", message_thread_id=thread_id)
    
    try:
        # Forma correcta de llamar a Imagen 3
        model_imagen = genai.ImageGenerationModel("imagen-3.0")
        result = model_imagen.generate_images(prompt=prompt)
        
        path = f"img_{chat_id}.png"
        result.images[0].save(path)
        
        with open(path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ {prompt}", message_thread_id=thread_id)
        
        os.remove(path)
        bot.delete_message(chat_id, sent_msg.message_id)
    except Exception as e:
        print(f"ERROR: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    # Limpiamos conexiones previas
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot iniciado correctamente sin conflictos.")
    # CORRECCIÓN AQUÍ: Quitamos el non_stop manual porque infinity_polling ya lo trae
    bot.infinity_polling(timeout=60)
