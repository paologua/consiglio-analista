import os
import telebot
import requests
from flask import Flask, request

# CONFIGURAZIONE
TOKEN = os.getenv("TOKEN_ANALYST")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def ask_claude(question):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1024,
        "system": "Sei l'Analista del Consiglio IA. Fornisci analisi profonde.",
        "messages": [{"role": "user", "content": question}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        if 'content' in res_json:
            return res_json['content'][0]['text']
        else:
            # Ti restituisce il vero errore di Anthropic
            error_msg = res_json.get('error', {}).get('message', 'Errore sconosciuto')
            return f"Dettaglio Errore Anthropic: {error_msg}"
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

@app.route('/webhook/analyst', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Error', 403

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    risposta = ask_claude(message.text)
    bot.reply_to(message, f"🧠 [ANALYST REPORT]:\n\n{risposta}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
