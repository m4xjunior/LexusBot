
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "6211829993:AAGG1ChoJaw259H1e0HE3rrAmBuW6Rr0YMc")

# ID e hash da API do telegrama. Este NÃO é o seu token de bot e não deve ser alterado.
API_ID = int(os.getenv("API_ID", "611335"))
API_HASH = os.getenv("API_HASH", "d524b414d21f4d37f08684c1df41ac9c")

# Chat usado para registrar erros.
LOG_CHAT = -1001659391281

# Bate-papo usado para registrar ações do usuário (como compra, presente, etc.).
ADMIN_CHAT = 5605472547
GRUPO_PUB = -1001592898932


# Quantas atualizações podem ser tratadas em paralelo.
# Não use valores altos para servidores de baixo custo.
WORKERS = 20

# Os administradores podem acessar o painel e adicionar novos materiais ao bot.
ADMINS = [5605472547, 5898679910]

# Sudoers têm acesso total ao servidor e podem executar comandos.
SUDOERS = [5980007588]

# Todos os sudoers também devem ser administradores
ADMINS.extend(SUDOERS)

GIFTERS = []

# Bote o Username do bot sem o @
# Exemplo: default
BOT_LINK = "hydra7storebot"



# Bote o Username do suporte sem o @
# Exemplo: suporte
BOT_LINK_SUPORTE = "hydra171"
##```
