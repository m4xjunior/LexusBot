import sqlite3

db = sqlite3.connect("main.db")
cur = db.cursor()


cur.execute("PRAGMA journal_mode=WAL")

cur.executescript(
    """
-- Configurações gerais do bot --
CREATE TABLE IF NOT EXISTS bot_config(
    lara_name TEXT DEFAULT 'Ana Paula Cristina Dos Santos',
    lara_key TEXT DEFAULT 'd44af075-559d-4a9c-94ff-2631ea6d80d4',
    main_img TEXT DEFAULT 'https://telegra.ph/Venha-Adiquirir-Sua-cc-03-16',
    support_user TEXT DEFAULT '@hydra171',
    channel_user TEXT DEFAULT '@hydraofc',
    is_on INTEGER DEFAULT 1,
    gate_chk TEXT DEFAULT 'w4rlock',
    gate_exchange TEXT DEFAULT 'w4rlock',
    pay_auto TEXT DEFAULT 'w4rlock',
    random_pix TEXT,
    random_pix_pb TEXT,
    time_exchange INTEGER DEFAULT 5,
    exchange_is INTEGER DEFAULT 1,
    db_version INTEGER DEFAULT 9
);

-- Inicializa a configuração com os valores padrão acima --
-- As configurações podem ser alteradas via painel posteriormente --
INSERT OR IGNORE INTO bot_config(ROWID) values(0);

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT,
    name_user TEXT,
    nome TEXT,
    email TEXT,
    telefone TEXT,
    chavepix TEXT,
    balance NUMERIC NOT NULL DEFAULT 0,
    balance_diamonds NUMERIC NOT NULL DEFAULT 0,
    agreed_tos INTEGER NOT NULL DEFAULT 0,
    registroaceito INTEGER NOT NULL DEFAULT 0,
    last_bought TEXT,
    is_action_pending INTEGER DEFAULT 0,
    is_blacklisted INTEGER NOT NULL DEFAULT 0,
    refer INTEGER
);

CREATE TABLE IF NOT EXISTS gifts(
    token TEXT PRIMARY KEY NOT NULL,
    value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tokens(
    type_token TEXT PRIMARY KEY NOT NULL,
    client_id TEXT,
    client_secret TEXT,
    name_cert_pem TEXT,
    name_cert_key TEXT,
    bearer_tk TEXT
);

-- Table para fazer o relatorio de vendas de entrada de saldo diario. --
CREATE TABLE IF NOT EXISTS sold_balance(
    type TEXT NOT NULL,
    value INTEGER NOT NULL,
    owner INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    add_balance_date TEXT DEFAULT CURRENT_TIMESTAMP
);

-- tabela para configurar bonus e preços e etc. --
CREATE TABLE IF NOT EXISTS values_config(
    transaction_type TEXT NOT NULL,
    min_value INTEGER NOT NULL,
    bonus_value INTEGER NOT NULL
);
"""
)






database_version = cur.execute("SELECT db_version FROM bot_config").fetchone()[0]











if database_version == 0:
    cur.executescript(
        """
    ALTER TABLE bot_config ADD COLUMN gate_chk TEXT DEFAULT w4rlock;
    ALTER TABLE bot_config ADD COLUMN gate_exchange TEXT DEFAULT w4rlock;
        """
    )

    database_version += 1

if database_version == 1:
    cur.executescript(
        """
    ALTER TABLE bot_config ADD COLUMN time_exchange INTEGER DEFAULT 5;
        """
    )
    database_version += 1

if database_version == 2:
    cur.executescript(
        """
    ALTER TABLE bot_config ADD COLUMN exchange_is INTEGER DEFAULT 1;
        """
    )
    database_version += 1

if database_version == 3:
    cur.executescript(
        """
    ALTER TABLE users ADD COLUMN is_action_pending INTEGER DEFAULT 0;
        """
    )
    database_version += 1


if database_version == 4:
    cur.executescript(
        """
    ALTER TABLE bot_config ADD COLUMN pay_auto TEXT DEFAULT 'mercado pago';
    ALTER TABLE bot_config ADD COLUMN random_pix TEXT;
        """
    )
    database_version += 1

if database_version == 5:
    cur.executescript(
        """
    ALTER TABLE tokens ADD COLUMN name_cert_pem TEXT NOT NULL;
    ALTER TABLE tokens ADD COLUMN name_cert_key TEXT NOT NULL;
        """
    )
    database_version += 1

if database_version == 6:
    cur.executescript(
        """
    ALTER TABLE tokens ADD COLUMN bearer_tk TEXT DEFAULT 'None';
    ALTER TABLE bot_config ADD COLUMN random_pix_pb TEXT;
        """
    )
    database_version += 1


if database_version == 7:
    cur.executescript(
        """
    ALTER TABLE sold_balance ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1
        """
    )
    database_version += 1


cur.execute("UPDATE bot_config SET db_version = ?", (database_version,))

cur.execute("UPDATE users SET is_action_pending = 0")


save = lambda: db.commit()
