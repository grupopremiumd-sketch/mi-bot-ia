import os
import telebot
from google import genai
from google.genai import types
from flask import Flask
import threading
import time

# --- SERVIDOR WEB ---
app = Flask('')
@app.route('/')
def home():
    return "Bot de Imagen 3 Online"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
IA_KEY = os.environ.get('GOOGLE_API_KEY')
ID_TEMA_PERMITIDO = 1 

# Inicializar cliente de Google GenAI
client = genai.Client(api_key=IA_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Esto aparecerá en los logs de Render para que copies tu ID
    print(f"DEBUG: ID detectado: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Generando con Imagen 3... espera un momento.", message_thread_id=thread_id)
    
    try:
        # --- NUEVA SINTAXIS CORREGIDA ---
        # Usamos el método de generación de imágenes por nombre de modelo directo
        response = client.models.generate_image(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=types.GenerateImageConfig(
                number_of_images=1,
                include_rai_reasoning=True
            )
        )
        
        # Guardar la imagen generada
        image_path = f"img_{chat_id}.png"
        for generated_image in response.generated_images:
            generated_image.image.save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ {prompt}", message_thread_id=thread_id)
        
        os.remove(image_path)
        bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        print(f"ERROR: {e}")
        # Si el error persiste, el bot te avisará por Telegram
        bot.edit_message_text(f"❌ Error de sistema: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot iniciado correctamente.")
    bot.infinity_polling(timeout=60)
