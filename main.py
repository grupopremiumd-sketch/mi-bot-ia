import os
import telebot
import requests
from flask import Flask
import threading
import time

# --- SERVIDOR WEB ---
app = Flask('')
@app.route('/')
def home():
    return "Bot de Arte Libre Online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Deja esto en 1 para ver tu ID en los logs la primera vez
ID_TEMA_PERMITIDO = 1 

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    prompt = message.text

    # Log para capturar el ID del tema
    print(f"DEBUG: ID detectado: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    sent_msg = bot.send_message(chat_id, "🎨 Dibujando... (Motor Libre)", message_thread_id=thread_id)
    
    try:
        # Generamos la URL de la imagen usando Pollinations (Gratis y sin API Key)
        image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={time.time()}&model=flux"
        
        # Enviamos la imagen directamente por URL
        bot.send_photo(chat_id, image_url, caption=f"✅ {prompt}", message_thread_id=thread_id)
        bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(f"❌ Error al generar: {e}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot con Motor Libre iniciado!")
    bot.infinity_polling(timeout=60)
