import os
import telebot
from google import genai
from flask import Flask
import threading
import time

# --- SERVIDOR WEB ---
app = Flask('')
@app.route('/')
def home():
    return "Bot de Imagen 3: Conexión Limpia"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
IA_KEY = os.environ.get('GOOGLE_API_KEY')
ID_TEMA_PERMITIDO = 1 

client = genai.Client(api_key=IA_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # IMPORTANTE: Verás este número en los logs de Render
    print(f"DEBUG: ID detectado: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Dibujando... espera un momento.", message_thread_id=thread_id)
    
    try:
        response = client.models.generate_image(
            model='imagen-3.0-generate-001',
            prompt=prompt
        )
        
        image_path = f"img_{chat_id}.png"
        response.generated_images[0].image.save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ {prompt}", message_thread_id=thread_id)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
        bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        print(f"ERROR IA: {e}")
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    # --- RESET TOTAL DE CONEXIÓN ---
    print("Cerrando webhooks y sesiones fantasma...")
    bot.remove_webhook()
    time.sleep(3) # Pausa extendida para que Telegram limpie la sesión
    
    print("🚀 Intentando conexión exclusiva...")
    # non_stop=True ayuda a recuperar la conexión si hay micro-cortes
    bot.infinity_polling(timeout=90, long_polling_timeout=5, interval=1)
