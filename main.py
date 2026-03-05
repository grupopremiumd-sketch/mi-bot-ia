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
    return "Bot Online y Funcionando"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Cámbialo por el ID de tu tema cuando lo veas en los logs
ID_TEMA_PERMITIDO = 1  

genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Imprime el ID en los logs para que lo configures
    print(f"DEBUG: Mensaje recibido en el tema ID: {thread_id}")

    if ID_TEMA_PERMITIDO != 1 and thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Creando tu imagen... dame un segundo.", message_thread_id=thread_id)
    
    try:
        # MÉTODO COMPATIBLE PARA IMAGEN 3
        # Cargamos el modelo como un GenerativeModel específico
        model = genai.GenerativeModel('gemini-1.5-flash') # Para texto/validación
        # Para imagen, usamos la ruta directa que Render acepta:
        imagen_model = genai.ImageGenerationModel("imagen-3.0")
        
        result = imagen_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            safety_filter_level="BLOCK_ONLY_HIGH",
            person_generation="ALLOW_ADULT"
        )
        
        path = f"img_{chat_id}.png"
        result.images[0].save(path)
        
        with open(path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ Aquí tienes: {prompt}", message_thread_id=thread_id)
        
        os.remove(path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"ERROR: {e}")
        # Si falla el nombre del atributo, intentamos el método alternativo de Google
        try:
            bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, sent_msg.message_id)
        except:
            pass

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("🚀 Bot iniciado correctamente.")
    bot.infinity_polling(timeout=60)
