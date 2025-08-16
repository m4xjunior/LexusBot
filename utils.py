import html
from asyncio import Lock
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Iterable, Optional, Tuple, Union
import json
from random import randint
import httpx
from async_lru import alru_cache
from pyrogram import Client
from pyrogram.types import CallbackQuery, User

from database import cur

timeout = httpx.Timeout(40, pool=None)

hc = httpx.AsyncClient(http2=True, timeout=timeout)


lock = Lock()


def is_bot_online() -> bool:
    """Retorna `True` se o bot está online ou `False` se ele está em manutenção."""

    q = cur.execute("SELECT is_on from bot_config")

    return bool(q.fetchone()[0])


def is_user_banned(user_id: int) -> bool:
    """Retorna `True` se o usuário está banido ou `False` caso contrário."""

    q = cur.execute("SELECT is_blacklisted from users WHERE id = ?", [user_id])
    res = q.fetchone()

    return bool(res[0] if res else res)


def get_lara_info() -> Tuple[str, str]:
    """Retorna uma tupla contendo o nome da lara e chave Pix."""

    q = cur.execute("SELECT lara_name, lara_key from bot_config")

    return q.fetchone()


def get_support_user() -> str:
    """Retorna uma string contendo o username do usuário de suporte."""

    q = cur.execute("SELECT support_user from bot_config")

    return q.fetchone()[0]


def get_news_user() -> str:
    """Retorna uma string contendo o username do canal de notícias."""

    q = cur.execute("SELECT channel_user from bot_config")

    return q.fetchone()[0]


def get_info_wallet(user_id: int) -> str:
    base = """<b>🏦 DASHBOARD FINANCEIRO:</b>
<b> ├👥 Titular:</b> <code>{}</code>
<b> ├🏷 Usuário:</b> <code>{}</code>
<b> ├🆔 Identificação:</b> <code>{}</code>
<b> ├💳 Saldo Em Conta:</b> <code>R$ {}</code>
<b> └🔄 Pontos acumulados:</b> <code>{}</code>"""
    rt = cur.execute(
        "SELECT name_user, username, id, balance, balance_diamonds FROM users WHERE id=?", [user_id]
    ).fetchone()

    if rt is None:
        return base.format("", "Sem username", "", "", "")
    else:
        name_user, username, id, balance, balance_diamonds = rt
        if username is None:
            username = "Sem username"
        return base.format(name_user, username, id, balance, balance_diamonds)

def get_user_transactions(user_id: int, limit: int = 10) -> list:
    """Retorna uma lista das últimas transações de um usuário."""
    q = cur.execute(
        "SELECT type, value, add_balance_date FROM sold_balance WHERE owner = ? ORDER BY add_balance_date DESC LIMIT ?",
        [user_id, limit]
    )
    return q.fetchall()


def insert_sold_balance(value: int, owner: int, type_add_saldo: str, quantity: int = 1):
    cur.execute(
        """INSERT INTO sold_balance(type, value, owner, quantity) VALUES(?, ?, ?, ?)""",
        [type_add_saldo, value, owner, quantity],
    )


def redeem_diamonds(user_id: int, diamonds_amount: float) -> bool:
    """Resgata diamantes por saldo, retorna True se bem-sucedido, False caso contrário."""
    cur.execute("BEGIN TRANSACTION")
    try:
        q = cur.execute("SELECT balance, balance_diamonds FROM users WHERE id = ?", [user_id]).fetchone()
        if q:
            current_balance, current_diamonds = q
            if current_diamonds >= diamonds_amount and diamonds_amount > 0:
                new_balance = current_balance + diamonds_amount # Assumindo 1 diamante = 1 BRL
                new_diamonds = current_diamonds - diamonds_amount
                cur.execute("UPDATE users SET balance = ?, balance_diamonds = ? WHERE id = ?",
                            [new_balance, new_diamonds, user_id])
                insert_sold_balance(diamonds_amount, user_id, "resgate_diamantes") # Registrar como venda/transacao
                cur.execute("COMMIT")
                return True
        cur.execute("ROLLBACK")
        return False
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"Erro ao resgatar diamantes: {e}")
        return False


def create_mention(user: User, with_id: bool = True) -> str:
    name = f"@{user.username}" if user.username else html.escape(user.first_name)

    mention = f"<a href='tg://user?id={user.id}'>{name}</a>"

    if with_id:
        mention += f" (<code>{user.id}</code>)"

    return mention


def to_hex(dec: float):
    digits = "0123456789ABCDEF"
    x = dec % 16
    rest = dec // 16
    if rest == 0:
        return digits[x]
    return to_hex(rest) + digits[x]


def get_crc16(payload: str):
    crc = 0xFFFF
    for i in range(len(payload)):
        crc ^= ord(payload[i]) << 8
        for j in range(8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return to_hex(crc & 0xFFFF).upper()


def create_copy_paste_pix(location: str) -> str:
    
    copy_paste = f"00020126830014br.gov.bcb.pix2561{location}520489995303986540105802BR5921{get_lara_info()[0]}6009SAO PAULO62070503***6304"

    return copy_paste + get_crc16(copy_paste)


def lock_user_buy(f: Callable):
    @wraps(f)
    async def lock_user(c: Client, m: CallbackQuery, *args, **kwargs):
        q = cur.execute(
            "SELECT is_action_pending FROM users WHERE id = ?", [m.from_user.id]
        ).fetchone()
        cur.execute(
            "UPDATE users SET is_action_pending = ? WHERE id = ?",
            [True, m.from_user.id],
        )
        if q[0]:
            return await m.answer(
                "Você só pode fazer uma compra/troca por vez. Por favor aguarde seu pedido anterior ser concluído.",
                show_alert=True,
            )
        try:
            return await f(c, m, *args, **kwargs)
        finally:
            cur.execute(
                "UPDATE users SET is_action_pending = ? WHERE id = ?",
                [False, m.from_user.id],
            )

    return lock_user
