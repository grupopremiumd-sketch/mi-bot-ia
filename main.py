import os
import telebot
import google.generativeai as genai
from PIL import Image
from flask import Flask
import threading

# --- SERVIDOR WEB PARA ENGAÑAR A RENDER (PLAN GRATUITO) ---
app = Flask('')

@app.route('/')
def home():
    return "El bot está vivo y funcionando"

def run_web():
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Iniciamos el servidor en un hilo separado
threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN DEL BOT ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# IMPORTANTE: Cambia el 1 por el ID de tu tema cuando lo sepas
ID_TEMA_PERMITIDO = 1 

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.ImageGenerationModel("imagen-3")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Imprime el ID en los Logs de Render para que sepas cuál es
    print(f"Mensaje recibido en el tema ID: {thread_id}")

    # Solo responde si es el tema permitido
    if thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    # Enviamos mensaje de espera en el mismo hilo
    sent_msg = bot.send_message(chat_id, "🎨 Dibujando tu idea... un momento.", message_thread_id=thread_id)
    
    try:
        # Generar imagen con Gemini
        result = model.generate_images(prompt=prompt)
        image_path = f"img_{chat_id}.png"
        result.images[0].save(image_path)
        
        # Enviar la foto al hilo correspondiente
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"Aquí tienes: {prompt}", message_thread_id=thread_id)
        
        # Limpieza
        os.remove(image_path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(f"❌ Error al generar: {str(e)}", chat_id, sent_msg.message_id)

print("Bot encendido y escuchando...")
bot.infinity_polling()
