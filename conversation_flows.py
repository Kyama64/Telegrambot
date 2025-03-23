#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conversation handlers for user registration flows.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from typing import Union

from data_manager import (
    save_translator_data,
    save_client_data,
    get_user_type
)
from utils import send_instructions, validate_price, validate_language_level

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_USER_TYPE = 0
TRANSLATOR_FORM = 1
CLIENT_FORM = 2

# Define conversation states as strings for better mapping
TRANSLATOR_NAME = 'translator_name'
TRANSLATOR_CITY = 'translator_city'
TRANSLATOR_LEVEL = 'translator_language_level'
TRANSLATOR_PRICE = 'translator_price'
TRANSLATOR_CONTACT = 'translator_contact'
CLIENT_CITY = 'client_city'
CLIENT_VERIFICATION = 'client_verification'

async def translator_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the translator's name input."""
    user_id = update.effective_user.id
    name = update.message.text
    
    # Store the provided name
    context.user_data['name'] = name
    
    from russian_messages import TRANSLATOR_CITY_PROMPT
    await update.message.reply_text(
        TRANSLATOR_CITY_PROMPT.format(name)
    )
    
    return TRANSLATOR_CITY

async def translator_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the translator's city input."""
    city = update.message.text
    
    # Store the provided city
    context.user_data['city'] = city
    
    from russian_messages import TRANSLATOR_LEVEL_PROMPT
    await update.message.reply_text(TRANSLATOR_LEVEL_PROMPT)
    
    return TRANSLATOR_LEVEL

async def translator_language_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the translator's language level input."""
    level = update.message.text.upper()
    
    # Validate language level format
    if not validate_language_level(level):
        from russian_messages import TRANSLATOR_LEVEL_INVALID
        await update.message.reply_text(TRANSLATOR_LEVEL_INVALID)
        return TRANSLATOR_CITY  # Return to the city input stage to try again
    
    # Store the provided language level
    context.user_data['language_level'] = level
    
    from russian_messages import TRANSLATOR_PRICE_PROMPT
    await update.message.reply_text(TRANSLATOR_PRICE_PROMPT)
    
    return TRANSLATOR_PRICE

async def translator_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the translator's price input."""
    price_text = update.message.text
    
    # Validate price format
    if not validate_price(price_text):
        from russian_messages import TRANSLATOR_PRICE_INVALID
        await update.message.reply_text(TRANSLATOR_PRICE_INVALID)
        return TRANSLATOR_LEVEL  # Return to language level input to try again
    
    # Store the provided price
    context.user_data['price'] = price_text
    
    from russian_messages import TRANSLATOR_CONTACT_PROMPT
    await update.message.reply_text(TRANSLATOR_CONTACT_PROMPT)
    
    return TRANSLATOR_CONTACT

async def translator_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the translator's contact info and complete the registration."""
    contact = update.message.text
    
    # Store the provided contact info
    context.user_data['contact'] = contact
    
    # Save all translator data
    user_id = update.effective_user.id
    translator_data = {
        'name': context.user_data.get('name', ''),
        'city': context.user_data.get('city', ''),
        'language_level': context.user_data.get('language_level', ''),
        'price': context.user_data.get('price', ''),
        'contact': contact
    }
    
    save_translator_data(user_id, translator_data)
    
    # Send completion message
    from russian_messages import TRANSLATOR_REGISTRATION_COMPLETE
    await update.message.reply_text(
        TRANSLATOR_REGISTRATION_COMPLETE.format(
            translator_data['name'],
            translator_data['city'],
            translator_data['language_level'],
            translator_data['price'],
            translator_data['contact']
        ),
        parse_mode='Markdown'
    )
    
    # Send instructions
    await send_instructions(update, 'translator')
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

async def client_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Handle the client's city input and collect verification information."""
    city = update.message.text
    
    # Store the provided city
    context.user_data['city'] = city
    
    # Ask for verification details to ensure they're not a translator
    from russian_messages import CLIENT_VERIFICATION_PROMPT
    await update.message.reply_text(CLIENT_VERIFICATION_PROMPT)
    
    return CLIENT_VERIFICATION

async def client_verification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """Verify client status and complete registration."""
    verification = update.message.text
    user_id = update.effective_user.id
    city = context.user_data.get('city', '')
    
    # Check if verification text looks like a translator trying to game the system
    suspicious_patterns = [
        'translator', 'interpret', 'übersetz', 'dolmetsch', 
        'language service', 'sprach', 'translation', 'переводчик', 
        'перевод', 'язык', 'услуги перевода'
    ]
    
    is_suspicious = False
    verification_lower = verification.lower()
    
    for pattern in suspicious_patterns:
        if pattern.lower() in verification_lower:
            is_suspicious = True
            break
    
    if is_suspicious:
        from russian_messages import CLIENT_SUSPICIOUS
        await update.message.reply_text(CLIENT_SUSPICIOUS)
        context.user_data.clear()
        return ConversationHandler.END
    
    # Save client data with verification text
    client_data = {
        'city': city,
        'service_needed': verification,
        'registration_complete': True
    }
    save_client_data(user_id, client_data)
    
    # Send completion message
    from russian_messages import CLIENT_REGISTRATION_COMPLETE
    await update.message.reply_text(
        CLIENT_REGISTRATION_COMPLETE.format(city)
    )
    
    # Send instructions
    await send_instructions(update, 'client')
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    """End the conversation and clean up."""
    context.user_data.clear()
    return ConversationHandler.END
