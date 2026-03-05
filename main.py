import os
import telebot
from google import genai
from PIL import Image
from flask import Flask
import threading
import time

# --- SERVIDOR WEB PARA MANTENER VIVO EL BOT ---
app = Flask('')
@app.route('/')
def home():
    return "Bot de Imagenes Online (Nueva Libreria)"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Cámbialo por el número que veas en los logs (DEBUG: ID detectado)
ID_TEMA_PERMITIDO = 1  

# Nueva forma de configurar el cliente de Google
client = genai.Client(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Imprime el ID en los logs de Render
    print(f"DEBUG: ID detectado en este mensaje: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Usando Imagen 3 para tu diseño... espera.", message_thread_id=thread_id)
    
    try:
        # NUEVA FORMA DE GENERAR IMÁGENES (Librería 2026)
        response = client.models.generate_image(
            model='imagen-3.0-generate-001',
            prompt=prompt
        )
        
        image_path = f"img_{chat_id}.png"
        response.generated_images[0].image.save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ Aquí tienes: {prompt}", message_thread_id=thread_id)
        
        os.remove(image_path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"ERROR: {e}")
        bot.edit_message_text(f"❌ Error al crear imagen: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot iniciado con la nueva librería google-genai.")
    bot.infinity_polling(timeout=60)
