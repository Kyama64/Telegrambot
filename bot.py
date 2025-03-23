#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot initialization and core functionality.
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from handlers import (
    start_command,
    help_command,
    error_handler,
    button_callback,
    handle_text_message,
    cancel_command,
    admin_data_command
)

from conversation_flows import (
    SELECTING_USER_TYPE,
    TRANSLATOR_FORM,
    CLIENT_FORM,
    translator_name,
    translator_city,
    translator_language_level,
    translator_price,
    translator_contact,
    client_city,
    client_verification,
    end_conversation
)

logger = logging.getLogger(__name__)

def create_bot(token):
    """Create and configure the bot with all necessary handlers."""
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add conversation handler for user registration 
    # Import all states from conversation_flows
    from conversation_flows import (
        SELECTING_USER_TYPE,
        TRANSLATOR_FORM,
        CLIENT_FORM,
        TRANSLATOR_NAME,
        TRANSLATOR_CITY,
        TRANSLATOR_LEVEL,
        TRANSLATOR_PRICE, 
        TRANSLATOR_CONTACT,
        CLIENT_CITY,
        CLIENT_VERIFICATION
    )
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            SELECTING_USER_TYPE: [CallbackQueryHandler(button_callback)],
            TRANSLATOR_FORM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translator_name),
            ],
            TRANSLATOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translator_city),
            ],
            TRANSLATOR_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translator_language_level),
            ],
            TRANSLATOR_LEVEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translator_price),
            ],
            TRANSLATOR_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translator_contact),
            ],
            CLIENT_FORM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, client_city),
            ],
            CLIENT_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, client_verification),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        allow_reentry=True, # Allow users to restart registration
        name="registration_conversation", # Name the conversation for easier tracking
        persistent=False # Don't require persistence, which simplifies the setup
    )
    
    application.add_handler(conv_handler)
    
    # Command handlers
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('found', lambda update, context: 
                                          handle_text_message(update, context, "translator found")))
    application.add_handler(CommandHandler('admin', admin_data_command))
    
    # General message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

async def get_group_info(application, group_username):
    """Get information about the group, including its ID.
    
    This function attempts to get the chat ID for the specified group
    and store it in the environment for future use.
    """
    from config import GROUP_USERNAME
    
    try:
        bot = application.bot
        logger.info(f"Attempting to get information for group @{GROUP_USERNAME}")
        
        # Try to get chat info by username
        chat = await bot.get_chat(f"@{GROUP_USERNAME}")
        chat_id = chat.id
        
        logger.info(f"Successfully retrieved info for group @{GROUP_USERNAME}")
        logger.info(f"Chat ID: {chat_id}")
        logger.info(f"Chat Type: {chat.type}")
        logger.info(f"Chat Title: {chat.title}")
        
        # In a real environment, we could store this in an environment variable
        # or configuration file for future use
        from config import GROUP_CHAT_ID
        import os
        os.environ["GROUP_CHAT_ID"] = str(chat_id)
        
        return chat_id
    except Exception as e:
        logger.error(f"Error getting group info: {str(e)}")
        logger.info("Bot will continue to run without group integration until added to the group.")
        return None

def run_bot(application):
    """Run the bot until the user presses Ctrl-C"""
    import asyncio
    from config import GROUP_USERNAME
    
    logger.info("Starting the Translation Service Bot")
    
    # Создаем новый event loop для потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запускаем бота с правильной конфигурацией для потоков
    try:
        # Используем только поддерживаемые параметры для данной версии библиотеки
        # И запускаем в созданном event loop
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.updater.start_polling(drop_pending_updates=True))
        loop.run_until_complete(application.start())
        loop.run_forever()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Закрываем loop при выходе
        try:
            # Останавливаем application и updater
            if hasattr(application, 'updater') and application.updater.running:
                loop.run_until_complete(application.updater.stop())
            if application.running:
                loop.run_until_complete(application.stop())
            # Закрываем loop
            loop.close()
        except Exception as e:
            logger.error(f"Error closing bot: {e}")
