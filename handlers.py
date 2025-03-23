#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command and message handlers for the Telegram bot.
"""

import logging
import re
from typing import Union
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from conversation_flows import SELECTING_USER_TYPE, TRANSLATOR_FORM, CLIENT_FORM
from data_manager import (
    save_user_type,
    get_translator_list,
    get_client_list,
    is_spam_message
)
from utils import send_instructions, get_admin_data_summary
from config import ADMIN_USER_IDS, USE_RUSSIAN, TRANSLATOR_FOUND_PHRASES, NEED_REPLACEMENT_PHRASES

# Import Russian messages
from russian_messages import *

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Start command handler that initiates user registration."""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    keyboard = [
        [
            InlineKeyboardButton(TRANSLATOR_BUTTON, callback_data='translator'),
            InlineKeyboardButton(CLIENT_BUTTON, callback_data='client')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        START_MESSAGE.format(user.first_name),
        reply_markup=reply_markup
    )
    
    return SELECTING_USER_TYPE

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help information about how to use the bot."""
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_USER_IDS
    
    admin_command = HELP_ADMIN_COMMAND if is_admin else ""
    
    help_text = HELP_MESSAGE.format(admin_command)
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Process the callback data when user selects their type."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_type = query.data
    
    # Save the user type
    save_user_type(user_id, user_type)
    
    if user_type == 'translator':
        await query.edit_message_text(
            TRANSLATOR_SELECTED,
            parse_mode='Markdown'
        )
        # Use the first step of translator registration flow
        from conversation_flows import TRANSLATOR_NAME
        return TRANSLATOR_NAME
    else:  # client
        await query.edit_message_text(
            CLIENT_SELECTED,
            parse_mode='Markdown'
        )
        # Use the first step of client registration flow
        from conversation_flows import CLIENT_CITY
        return CLIENT_CITY

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, override_text=None) -> None:
    """Handle regular text messages in the group."""
    message_text = override_text or update.message.text.lower()
    user_id = update.effective_user.id
    
    # Check if message is in a group chat (not private)
    is_group_message = update.effective_chat.type in ["group", "supergroup"]
    
    # Get user type (translator or client)
    from data_manager import get_user_type, get_client_data
    user_type = get_user_type(user_id)
    
    # Check if the message is related to finding a translator
    translator_found = any(phrase in message_text.lower() for phrase in TRANSLATOR_FOUND_PHRASES)
    if translator_found:
        await update.message.reply_text(TRANSLATOR_FOUND_MESSAGE)
        return
    
    # Check for spam
    if is_spam_message(message_text):
        await update.message.reply_text(SPAM_WARNING)
        return
    
    # Enforce group message permissions
    if is_group_message:
        # In groups, enforce permission rules
        
        # Special case - if it contains "need replacement" and user is a translator, allow it
        replacement_needed = any(phrase in message_text.lower() for phrase in NEED_REPLACEMENT_PHRASES)
        if replacement_needed and user_type == "translator":
            # This is allowed - translator looking for a replacement
            return
            
        # If user is a translator but trying to post a regular message (not replacement request)
        if user_type == "translator" and not replacement_needed:
            await update.message.reply_text(
                TRANSLATOR_GROUP_RESTRICTION,
                reply_to_message_id=update.message.message_id
            )
            return
            
        # If user has not registered yet
        if not user_type:
            await update.message.reply_text(
                REGISTRATION_REQUIRED,
                reply_to_message_id=update.message.message_id
            )
            return
            
        # If client is not fully verified
        if user_type == "client":
            client_data = get_client_data(user_id)
            if not client_data or not client_data.get('registration_complete'):
                await update.message.reply_text(
                    CLIENT_VERIFICATION_REQUIRED,
                    reply_to_message_id=update.message.message_id
                )
                return
    
    # Check if we're in the middle of a conversation but it wasn't caught by the handler
    if hasattr(context, 'user_data') and context.user_data:
        logger.debug(f"User data found: {context.user_data}")
        # This helps with debugging any potential conversation state issues
    
    # Default response if needed
    # This is left empty to avoid responding to all messages in the group

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Cancel the current operation and end the conversation."""
    await update.message.reply_text(CANCEL_MESSAGE)
    return ConversationHandler.END

async def admin_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to get data summary about translators and clients."""
    user_id = update.effective_user.id
    
    # Check if the user is an admin
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text(ADMIN_NOT_ALLOWED)
        return
    
    # Get the data summary
    summary = get_admin_data_summary()
    
    # Send the summary to the admin
    await update.message.reply_text(
        summary,
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Send a message to the user
    if update:
        await update.effective_message.reply_text(ERROR_MESSAGE)
