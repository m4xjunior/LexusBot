# LexusBot - Bot de Pagamentos PIX para Telegram

Este é um bot Telegram construído com Pyrogram, projetado para gerenciar transações de pagamento e contas de usuário, com foco em pagamentos PIX no Brasil. O bot se integra a diversas gateways de pagamento populares e mantém um sistema robusto de gerenciamento de usuários e transações.

## Funcionalidades Principais

*   **Processamento de Pagamentos PIX**: Integração com Mercado Pago, Gerencianet, PagBank e Juno para geração de códigos PIX (copia e cola) e QR Codes, com verificação de status de pagamento.
*   **Sistema de Carteira do Usuário**: Gerenciamento de saldo e um sistema de pontos de diamante para os usuários.
*   **Histórico de Transações**: Usuários podem consultar suas últimas transações de saldo e resgate de diamantes.
*   **Resgate de Diamantes**: Possibilidade de converter diamantes acumulados em saldo na carteira do usuário.
*   **Menu Interativo**: Navegação facilitada através de um menu principal com botões inline para acesso rápido às funcionalidades.
*   **Notificações de Webhook**: Integração com webhooks para receber notificações de pagamento em tempo real e alertar os usuários.
*   **Controle de Concorrência**: Mecanismo de bloqueio de ações para prevenir compras ou trocas simultâneas por um mesmo usuário.
*   **Configurações Flexíveis**: Gerenciamento de configurações do bot, incluindo status de manutenção e banimento de usuários.

## Tecnologias Utilizadas

*   **Python**: Linguagem de programação principal.
*   **Pyrogram**: Framework assíncrono para construção de bots Telegram.
*   **aiohttp**: Para a criação do servidor web assíncrono para o webhook.
*   **httpx**: Cliente HTTP assíncrono para interações com APIs de pagamento.
*   **sqlite3**: Banco de dados SQLite para armazenamento de dados.
*   **async-lru**: Para cache de funções assíncronas.
*   **meval**: Para avaliação de expressões.
*   **TgCrypto**: Para criptografia.

## Instalação

Para configurar e executar o bot localmente, siga os passos abaixo:

1.  **Clone o Repositório**:

    ```bash
    git clone https://github.com/seu-usuario/LexusBot.git
    cd LexusBot
    ```

2.  **Instale as Dependências**:

    Certifique-se de ter o `pip` instalado. As dependências estão listadas no arquivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

## Configuração

As configurações do bot são gerenciadas no arquivo `config.py`. É crucial proteger suas credenciais de API. O bot agora suporta o carregamento de tokens sensíveis através de variáveis de ambiente. Recomenda-se definir as seguintes variáveis de ambiente:

*   `BOT_TOKEN`: Seu token de bot do Telegram (obtido via BotFather).
*   `API_ID`: Seu API ID do Telegram (obtido em my.telegram.org).
*   `API_HASH`: Seu API Hash do Telegram (obtido em my.telegram.org).

Exemplo de como definir (para Linux/macOS):

```bash
export BOT_TOKEN="SEU_BOT_TOKEN"
export API_ID="SEU_API_ID"
export API_HASH="SEU_API_HASH"
```

Ou crie um arquivo `.env` e use uma biblioteca como `python-dotenv` para carregá-las (não incluído por padrão, mas recomendado para desenvolvimento).

Outras configurações, como `LOG_CHAT`, `ADMIN_CHAT`, `ADMINS`, `SUDOERS`, e `BOT_LINK_SUPORTE` podem ser ajustadas diretamente no `config.py`.

## Executando o Bot

Após a instalação das dependências e configuração, você pode iniciar o bot:

```bash
python bot.py
```

O bot iniciará o cliente Pyrogram e o servidor de webhook na porta 5000.

## Uso do Bot

Interaja com o bot no Telegram:

*   Envie `/start` para acessar o menu principal interativo.
*   No menu, selecione **"Minha Carteira"** para ver seu saldo e diamantes, e acessar o histórico de transações.
*   Selecione **"Comprar Saldo"** para iniciar o processo de compra via PIX.
*   Selecione **"Resgatar Diamantes"** para converter seus pontos de diamante em saldo.
*   Use o comando `/historico` diretamente para ver suas transações.
*   O botão **"📋 Copiar Código PIX"** estará disponível após a geração de um PIX para facilitar a cópia.

## Integração com Webhook (Sostrader)

O bot está configurado para receber notificações de um webhook POST no endpoint `/webhook/lexusbot` na porta `5000`. Para integrar com o serviço da Sostrader (`https://webhook.sostrader.com.br/webhook/lexusbot`):

1.  Certifique-se de que seu bot está rodando e acessível publicamente na porta 5000.
2.  Configure o webhook na plataforma da Sostrader para enviar requisições POST para a URL do seu servidor, por exemplo: `http://SEU_IP_PUBLICO_OU_DOMINIO:5000/webhook/lexusbot`.
3.  O bot processará as informações do webhook (assumindo que contenham `user_id`, `amount`, `status`) e notificará o usuário correspondente no Telegram.

## Estrutura do Banco de Dados (SQLite)

O `main.db` (SQLite) contém as seguintes tabelas principais:

*   `bot_config`: Configurações globais do bot (nome da "Lara", chave PIX, status online/offline, etc.).
*   `users`: Informações dos usuários (ID, username, nome, saldo, diamantes, status de banimento, etc.).
*   `gifts`: Sistema de tokens de presente.
*   `tokens`: Credenciais de gateways de pagamento.
*   `sold_balance`: Histórico de transações de vendas e adições de saldo.
*   `values_config`: Configurações de bônus e regras de preço.

## Gateways de Pagamento Suportados

O bot possui integração com os seguintes gateways de pagamento PIX:

*   **MercadoPago**
*   **Gerencianet**
*   **PagBank**
*   **Juno**

## Notas de Segurança

*   **Credenciais de API**: O arquivo `config.py` foi atualizado para carregar `BOT_TOKEN`, `API_ID` e `API_HASH` de variáveis de ambiente. É *altamente recomendável* usar variáveis de ambiente para todas as credenciais sensíveis em um ambiente de produção.
*   **Dados Sensíveis**: Credenciais de gateways de pagamento são armazenadas no banco de dados, que deve ser protegido adequadamente.
*   **Prevenção de Ataques Concorrentes**: O bot inclui um mecanismo de bloqueio (`lock_user_buy`) para evitar problemas de concorrência em transações de compra/troca.

---

Para suporte ou dúvidas, entre em contato com `@` + `BOT_LINK_SUPORTE` (definido em `config.py`).
