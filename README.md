# Translation Service Telegram Bot

A Telegram bot that automates management of a translation service group for Russian/Ukrainian-speaking people in Germany. It handles user registration, data collection, and client-translator matching.

## Features

- **User Category Selection**: Distinguishes between Translators and Clients
- **Translator Registration**: Collects name, city, German language level, price per hour, and contact information
- **Client Registration**: Collects city information for better matching
- **Automated Instructions**: Provides role-specific instructions to each user type
- **Spam Filtering**: Removes unnecessary messages to keep the group clean
- **Request Management**: Command to mark "translator found" to avoid duplicate responses

## How It Works

1. **For Translators**:
   - Register with the bot by providing name, city, German language level, hourly rate, and contact details
   - Receive instructions on finding clients and translation service best practices
   - Contact clients directly through private messages

2. **For Clients**:
   - Register by specifying their city
   - Post requests in the group chat
   - Mark "translator found" when they've found someone
   - Receive a brief explanation on how to submit a request

## Setup

1. Create a Telegram bot via BotFather:
   - Open Telegram and search for @BotFather
   - Start a chat and type `/newbot`
   - Follow instructions to create your bot and get a token

2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
   - `ADMIN_USER_IDS`: Comma-separated list of admin Telegram user IDs (optional)
   - `DEBUG`: Set to "True" for verbose logging (optional)

3. Start the bot:
   ```
   python main.py
   ```

## Bot Commands

- `/start` - Begin registration as a translator or client
- `/help` - Display help information and instructions
- `/found` - Mark that a client has found a translator
- `/cancel` - Cancel the current registration process
- `/admin` - (Admin only) View statistics on registered translators and clients
   