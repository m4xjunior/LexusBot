# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot built with Pyrogram for managing payment transactions and user accounts in Portuguese. The bot integrates with multiple Brazilian payment gateways (MercadoPago, Gerencianet, PagBank, Juno) for PIX payments and maintains a SQLite database for user management.

## Development Commands

### Running the Bot
```bash
python bot.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

The main dependencies are:
- Custom Pyrogram build from AmanoTeam
- httpx with HTTP/2 support
- async-lru for caching
- meval for expression evaluation
- TgCrypto for encryption

## Code Architecture

### Core Components

**bot.py**: Main entry point that initializes the Pyrogram client with plugin discovery from the `plugins/` directory. Uses configuration from config.py and database from database.py.

**config.py**: Contains all bot configuration including API credentials, admin/sudoer user IDs, chat IDs for logging, and worker settings. **WARNING: Contains hardcoded tokens and should be secured**.

**database.py**: SQLite database initialization with schema versioning system. Creates tables for users, bot configuration, gifts, payment tokens, sales reporting, and value configurations. Includes migration logic for schema updates.

**payments.py**: Payment gateway integrations for PIX transactions. Supports multiple providers:
- MercadoPago: Standard integration
- Gerencianet: Certificate-based authentication
- PagBank: Certificate with token caching
- Juno: Base64 auth with private tokens

**utils.py**: Utility functions including user validation, PIX copy-paste generation, user locking mechanisms, and database helpers.

### Plugin System

The bot uses Pyrogram's plugin system with plugins loaded from the `plugins/` directory. Currently, the plugins directory appears to be empty, but the bot.py file is configured to load plugins from `{"root": "plugins"}`.

### Database Schema

- **users**: User accounts with balance, diamonds, contact info, and status flags
- **bot_config**: Global bot settings with versioning
- **gifts**: Gift token system
- **tokens**: Payment gateway credentials storage
- **sold_balance**: Sales reporting and transaction history
- **values_config**: Configurable bonus and pricing rules

### Key Features

- Multi-gateway PIX payment processing
- User balance and diamond point system
- Admin/sudoer permission levels
- Gift token system
- Transaction locking to prevent concurrent purchases
- Sales reporting and analytics
- Configurable bonuses and pricing

## Security Notes

- The config.py file contains hardcoded API tokens and should be properly secured
- Payment gateway credentials are stored in the database
- User actions are locked during transactions to prevent race conditions
- Bot includes blacklisting and maintenance mode features

## Development Notes

- The bot uses async/await throughout for proper concurrency
- Database operations use WAL mode for better performance
- HTTP client is configured with HTTP/2 support and timeouts
- The codebase is primarily in Portuguese with some English variable names