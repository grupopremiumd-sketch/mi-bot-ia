import os
import telebot
import google.generativeai as genai
from PIL import Image
from flask import Flask
import threading

# --- SERVIDOR WEB PARA RENDER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot vivo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()

# --- CONFIGURACIÓN DEL BOT ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# IMPORTANTE: Cambia este 1 por el ID de tu tema cuando lo veas en los logs
ID_TEMA_PERMITIDO = 1 

genai.configure(api_key=GOOGLE_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def generate(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    # Esto te dirá el ID real en los logs de Render
    print(f"Mensaje recibido en el tema ID: {thread_id}")

    if thread_id != ID_TEMA_PERMITIDO:
        return 

    prompt = message.text
    sent_msg = bot.send_message(chat_id, "🎨 Dibujando tu idea con Imagen 3...", message_thread_id=thread_id)
    
    try:
        # NUEVA FORMA DE LLAMAR A IMAGEN 3
        # Usamos el modelo generativo estándar pero especificando el modelo de imagen
        imagen_model = genai.GenerativeModel('gemini-1.5-flash') 
        # Nota: Si tu API Key tiene acceso a Imagen 3, el comando es:
        result = genai.ImageGenerationModel("imagen-3.0").generate_images(prompt=prompt)
        
        image_path = f"img_{chat_id}.png"
        result.images[0].save(image_path)
        
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=f"✅ ¡Listo!: {prompt}", message_thread_id=thread_id)
        
        os.remove(image_path)
        bot.delete_message(chat_id, sent_msg.message_id)
        
    except Exception as e:
        print(f"Error: {e}")
        # Si da error de modelo, intentamos la alternativa
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, sent_msg.message_id)

print("Bot corregido y encendido...")
bot.infinity_polling()
