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
    return "Bot Online y Corregido"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Cámbialo por el número que veas en los logs (DEBUG: Mensaje recibido...)
ID_TEMA_PERMITIDO = 1  

genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Esto imprime el ID en Render para que lo configures
    print(f"DEBUG: Mensaje recibido en el tema ID: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Generando imagen con Imagen 3... espera un momento.", message_thread_id=thread_id)
    
    try:
        # --- SOLUCIÓN AL ERROR DE ATRIBUTO ---
        # Usamos el método de generación de imágenes de la versión 'v1beta' que es la que tiene Imagen 3 activo
        import google.ai.generativelanguage as gag
        
        # Configuramos el cliente de imagen específicamente
        imagen_model = genai.ImageGenerationModel("imagen-3.0")
        result = imagen_model.generate_images(prompt=prompt)
        
        path = f"img_{chat_id}.png"
        result.images[0].save(path)
        
        with open(path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ Resultado: {prompt}", message_thread_id=thread_id)
        
        os.remove(path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"ERROR DETALLADO: {e}")
        # Intento de respaldo si el modelo directo falla
        bot.edit_message_text(f"❌ Error técnico: El modelo de Google no respondió correctamente. Revisa tus logs de Render.", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot iniciado correctamente.")
    bot.infinity_polling(timeout=60)
