import asyncio

from pyrogram import Client, idle
from pyrogram.session import Session
from pyrogram.enums import ParseMode
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

from aiohttp import web

from config import API_HASH, API_ID, BOT_TOKEN, WORKERS
from database import db, save
from utils import get_user_transactions, get_info_wallet, create_copy_paste_pix
from payments import MercadoPago # Importar MercadoPago


client = Client(
    "bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    workers=WORKERS,
    parse_mode=ParseMode.HTML,
    plugins={"root": "plugins"},
)

user_states = {}

@client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💰 Comprar Saldo", callback_data="comprar_saldo")],
            [InlineKeyboardButton("💳 Minha Carteira", callback_data="minha_carteira")],
            [InlineKeyboardButton("📞 Suporte", url="https://t.me/" + config.BOT_LINK_SUPORTE)], # Assumindo BOT_LINK_SUPORTE no config.py
            [InlineKeyboardButton("⚙️ Configurações", callback_data="configuracoes")],
        ]
    )
    await message.reply_text("👋 Olá! Bem-vindo ao Bot Lexus. Escolha uma opção:", reply_markup=keyboard)


@client.on_message(filters.command("historico") & filters.private)
async def historico_command(client: Client, message: Message):
    user_id = message.from_user.id
    transactions = get_user_transactions(user_id)

    if not transactions:
        await message.reply_text("Você ainda não possui transações registradas.")
        return

    response_text = "📊 <b>Suas Últimas Transações:</b>\n\n"
    for transaction_type, value, date_str in transactions:
        date_obj = datetime.fromisoformat(date_str)  # Converte a string ISO para objeto datetime
        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S") # Formata para DD/MM/AAAA HH:MM:SS
        response_text += f"<b>├ Tipo:</b> {transaction_type.capitalize()}\n<b>├ Valor:</b> R$ {value:.2f}\n<b>└ Data:</b> {formatted_date}\n\n"
    
    await message.reply_text(response_text)

async def webhook_handler(request):
    data = await request.json()
    print("Webhook recebido:", data)
    
    # Exemplo de processamento do webhook (ajustar conforme a estrutura real do webhook da Sostrader)
    try:
        user_id_webhook = data.get("user_id")  # Assumindo que o webhook envia o user_id do Telegram
        valor_pago = data.get("amount") # Assumindo que o webhook envia o valor pago
        status_pagamento = data.get("status") # Assumindo que o webhook envia o status (ex: "APPROVED", "COMPLETED")

        if user_id_webhook and valor_pago and status_pagamento:
            if status_pagamento.upper() == "APROVADO" or status_pagamento.upper() == "COMPLETED": # Adapte os status
                message_to_user = f"🎉 Seu pagamento de R$ {float(valor_pago):.2f} foi **APROVADO**! Seu saldo foi atualizado.\n"\
                                  f"Obrigado por sua compra!"
                await client.send_message(chat_id=user_id_webhook, text=message_to_user)
                # Aqui você também pode adicionar a lógica para atualizar o saldo do usuário no banco de dados
                # update_user_balance(user_id_webhook, valor_pago)
            else:
                message_to_user = f"⚠️ Seu pagamento de R$ {float(valor_pago):.2f} está com o status: **{status_pagamento.upper()}**.\n"\
                                  f"Se houver algum problema, entre em contato com o suporte."
                await client.send_message(chat_id=user_id_webhook, text=message_to_user)
        
        # Enviar para o LOG_CHAT para depuração
        chat_id_log = -1001659391281 # LOG_CHAT (do config.py)
        await client.send_message(chat_id=chat_id_log, text=f"Webhook recebido:\n<pre>{data}</pre>")

    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        chat_id_log = -1001659391281 # LOG_CHAT (do config.py)
        await client.send_message(chat_id=chat_id_log, text=f"Erro ao processar webhook:\n<pre>{data}</pre>\nErro: {e}")

    return web.Response(text="OK", status=200)


@client.on_callback_query(filters.regex("^minha_carteira$"))
async def minha_carteira_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    wallet_info = get_info_wallet(user_id)
    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📊 Ver Histórico", callback_data="ver_historico")],
            [InlineKeyboardButton("💎 Resgatar Diamantes", callback_data="resgatar_diamantes")],
        ]
    )
    await callback_query.message.edit_text(wallet_info, reply_markup=keyboard)


@client.on_callback_query(filters.regex("^comprar_saldo$"))
async def comprar_saldo_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_states[user_id] = "aguardando_valor_compra"
    await callback_query.message.edit_text("Por favor, digite o valor em BRL que deseja comprar (ex: 10.00).")


@client.on_callback_query(filters.regex("^resgatar_diamantes$"))
async def resgatar_diamantes_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_states[user_id] = "aguardando_valor_resgate"
    await callback_query.message.edit_text("Por favor, digite a quantidade de diamantes que deseja resgatar.")


@client.on_message(filters.text & filters.private)
async def handle_buy_value(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        if user_states[user_id] == "aguardando_valor_compra":
            try:
                value = float(message.text.replace(",", "."))
                if value <= 0:
                    await message.reply_text("Por favor, digite um valor positivo.")
                    return
                
                # Simular credenciais do Mercado Pago para o teste
                mp_access_token = "YOUR_MERCADOPAGO_ACCESS_TOKEN"  # Substitua pelo seu token real
                mp = MercadoPago(mp_access_token)

                # Simular dados do usuário para a criação do pagamento
                full_name = message.from_user.first_name + (f" {message.from_user.last_name}" if message.from_user.last_name else "")
                cpf = "12345678900" # CPF de exemplo. Em um bot real, você coletaria do usuário.
                email = "teste@example.com" # E-mail de exemplo. Em um bot real, você coletaria do usuário.

                payment_info = await mp.create_payment(value, email, full_name, cpf, user_id)

                if payment_info and payment_info.get("status") != "error":
                    copy_paste_code = payment_info.get("copy_paste")
                    qr_code_base64 = payment_info.get("qr_code")
                    
                    response_text = f"💰 Seu pagamento PIX foi gerado!\n\n<b>Valor:</b> R$ {value:.2f}\n<b>Código PIX Copia e Cola:</b>\n<code>{copy_paste_code}</code>\n\nEscaneie o QR Code ou copie o código acima para pagar.\n\n" # Exemplo simplificado

                    keyboard = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("📋 Copiar Código PIX", callback_data=f"copy_pix_{copy_paste_code}")],
                        ]
                    )

                    if qr_code_base64:
                        await client.send_photo(chat_id=user_id, photo=base64.b64decode(qr_code_base64), caption=response_text, reply_markup=keyboard)
                    else:
                        await message.reply_text(response_text, reply_markup=keyboard)

                else:
                    await message.reply_text(f"Não foi possível gerar o pagamento. Erro: {payment_info.get("message", "Desconhecido")}")

            except ValueError:
                await message.reply_text("Valor inválido. Por favor, digite um número (ex: 10.00).")
            finally:
                del user_states[user_id] # Limpa o estado
        elif user_states[user_id] == "aguardando_valor_resgate":
            try:
                diamonds_to_redeem = float(message.text.replace(",", "."))
                if diamonds_to_redeem <= 0:
                    await message.reply_text("Por favor, digite uma quantidade positiva de diamantes.")
                    return
                
                success = redeem_diamonds(user_id, diamonds_to_redeem)
                if success:
                    await message.reply_text(f"🎉 {diamonds_to_redeem:.2f} diamantes resgatados com sucesso! Seu saldo foi atualizado.")
                else:
                    await message.reply_text("Não foi possível resgatar os diamantes. Verifique seu saldo ou tente novamente mais tarde.")

            except ValueError:
                await message.reply_text("Quantidade inválida. Por favor, digite um número (ex: 50).")
            finally:
                del user_states[user_id] # Limpa o estado


@client.on_callback_query(filters.regex("^copy_pix_.*"))
async def copy_pix_callback(client: Client, callback_query: CallbackQuery):
    pix_code = callback_query.data.replace("copy_pix_", "")
    await callback_query.answer("Código PIX copiado!", show_alert=True)
    # Pyrogram não tem uma forma direta de copiar para o clipboard do usuário.
    # A mensagem acima é apenas um feedback.


@client.on_callback_query(filters.regex("^configuracoes$"))
async def configuracoes_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text("Configurações em desenvolvimento.")


@client.on_callback_query(filters.regex("^ver_historico$"))
async def ver_historico_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    transactions = get_user_transactions(user_id)

    if not transactions:
        await callback_query.message.edit_text("Você ainda não possui transações registradas.")
        return

    response_text = "📊 <b>Suas Últimas Transações:</b>\n\n"
    for transaction_type, value, date_str in transactions:
        date_obj = datetime.fromisoformat(date_str)  # Converte a string ISO para objeto datetime
        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S") # Formata para DD/MM/AAAA HH:MM:SS
        response_text += f"<b>├ Tipo:</b> {transaction_type.capitalize()}\n<b>├ Valor:</b> R$ {value:.2f}\n<b>└ Data:</b> {formatted_date}\n\n"
    
    await callback_query.message.edit_text(response_text)


Session.notice_displayed = True


async def main():
    await client.start()
    print("Bot rodando...")
    client.me = await client.get_me()

    # Configurar e iniciar o servidor aiohttp para o webhook
    app = web.Application()
    app.router.add_post("/webhook/lexusbot", webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000) # Porta 5000 para o webhook
    await site.start()
    print("Servidor Webhook aiohttp iniciado na porta 5000")

    await idle()

    await client.stop()
    save()
    db.close()
    
    await runner.cleanup()


loop = asyncio.get_event_loop()

if __name__ == "__main__":
    loop.run_until_complete(main())