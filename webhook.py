from flask import Flask, request, jsonify
import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Flask(__name__)

# Inicialize o cliente Pyrogram (pode ser necessário ajustar)
# client = Client("bot_webhook", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.route("/webhook/lexusbot", methods=["POST"])
def lexusbot_webhook():
    data = request.get_json()
    print("Webhook recebido:", data)
    # Aqui você processaria os dados do webhook e agiria com o bot Pyrogram
    # Exemplo: enviar uma mensagem para um chat específico
    # asyncio.run(client.send_message(chat_id, "Pagamento recebido!"))

    return jsonify({"status": "success", "message": "Webhook recebido"}), 200

if __name__ == "__main__":
    # Isso deve ser executado de forma assíncrona com o bot principal
    # Por enquanto, apenas para teste
    app.run(host="0.0.0.0", port=5000)
