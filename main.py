import os
import telebot
from google import genai
from PIL import Image
from flask import Flask
import threading
import time

# --- SERVIDOR WEB ---
app = Flask('')
@app.route('/')
def home():
    return "Servidor del Bot Activo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Cámbialo por el ID de tu tema cuando lo veas en los Logs de Render
ID_TEMA_PERMITIDO = 1  

client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Imprime el ID en los logs de Render para que lo copies
    print(f"DEBUG: ID detectado en este mensaje: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Generando imagen con Imagen 3...", message_thread_id=thread_id)
    
    try:
        # Generación oficial de Google GenAI
        response = client.models.generate_image(
            model='imagen-3.0-generate-001',
            prompt=prompt
        )
        
        image_path = f"img_{chat_id}.png"
        response.generated_images[0].image.save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ {prompt}", message_thread_id=thread_id)
        
        os.remove(image_path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"ERROR: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    # Limpieza de sesiones previas para eliminar el Error 409
    print("Limpiando conexiones anteriores...")
    bot.remove_webhook()
    time.sleep(2) 
    
    print("🚀 Bot iniciado correctamente con nuevo Token.")
    # Usamos parámetros más estables para Render
    bot.infinity_polling(timeout=90, long_polling_timeout=5)
