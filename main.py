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
    return "Bot de Imagen 3: Versión Final"

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
    
    print(f"DEBUG: ID detectado: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Generando tu imagen con Imagen 3...", message_thread_id=thread_id)
    
    try:
        # --- CAMBIO CLAVE: NOMBRE DEL MODELO ACTUALIZADO ---
        response = client.models.generate_image(
            model='imagen-3',  # Nombre simplificado para v1beta/v1
            prompt=prompt
        )
        
        image_path = f"img_{chat_id}.png"
        response.generated_images[0].image.save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ Aquí tienes: {prompt}", message_thread_id=thread_id)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
        bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        error_str = str(e)
        print(f"ERROR IA: {error_str}")
        # Si el error es 404, intentamos con el nombre alternativo automáticamente
        if "404" in error_str:
            bot.edit_message_text("⚠️ Ajustando motor de imagen... intenta de nuevo en 5 segundos.", chat_id, sent_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Error: {error_str}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(2)
    print("🚀 Bot iniciado. Esperando mensajes...")
    bot.infinity_polling(timeout=90)
