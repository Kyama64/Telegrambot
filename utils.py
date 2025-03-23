#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for the Telegram bot.
"""

import logging
import re
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def send_instructions(update: Update, user_type: str) -> None:
    """Send instructions based on user type."""
    from russian_messages import TRANSLATOR_INSTRUCTIONS, CLIENT_INSTRUCTIONS
    
    if user_type == 'translator':
        instructions = TRANSLATOR_INSTRUCTIONS
    else:  # client
        instructions = CLIENT_INSTRUCTIONS
    
    await update.message.reply_text(instructions, parse_mode='Markdown')

def validate_price(price_text: str) -> bool:
    """Validate that the price is a number."""
    try:
        price = float(price_text.replace(',', '.'))
        return price > 0
    except ValueError:
        return False

def validate_language_level(level: str) -> bool:
    """Validate that the language level is one of the accepted values."""
    valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'NATIVE']
    return level.upper() in valid_levels

def get_admin_data_summary():
    """Get a summary of all data for admin review."""
    from data_manager import get_translator_list, get_client_list
    
    translators = get_translator_list()
    clients = get_client_list()
    
    translator_count_by_city = {}
    translator_levels = {}
    translator_prices = []
    
    for t in translators:
        city = t.get('city', 'Unknown')
        level = t.get('language_level', 'Unknown')
        price = t.get('price', '0')
        
        # Count by city
        translator_count_by_city[city] = translator_count_by_city.get(city, 0) + 1
        
        # Count by level
        translator_levels[level] = translator_levels.get(level, 0) + 1
        
        # Collect prices for analysis
        try:
            price_float = float(price.replace('€', '').strip())
            translator_prices.append(price_float)
        except (ValueError, AttributeError):
            pass
    
    # Client stats with verification information
    client_count_by_city = {}
    verified_clients = 0
    unverified_clients = 0
    suspicious_verifications = []
    
    for c in clients:
        city = c.get('city', 'Unknown')
        client_count_by_city[city] = client_count_by_city.get(city, 0) + 1
        
        # Check verification status
        if c.get('registration_complete', False):
            verified_clients += 1
        else:
            unverified_clients += 1
            
        # Check for suspicious verification responses
        service_needed = c.get('service_needed', '')
        if service_needed:
            suspicious_patterns = [
                'translator', 'interpret', 'übersetz', 'dolmetsch', 
                'language service', 'sprach', 'translation'
            ]
            
            for pattern in suspicious_patterns:
                if pattern.lower() in service_needed.lower():
                    suspicious_verifications.append({
                        'user_id': c.get('user_id'),
                        'city': city, 
                        'verification_text': service_needed
                    })
                    break
    
    # Calculate average price if we have prices
    avg_price = sum(translator_prices) / len(translator_prices) if translator_prices else 0
    min_price = min(translator_prices) if translator_prices else 0
    max_price = max(translator_prices) if translator_prices else 0
    
    summary = (
        f"📊 *Сводка данных администратора*\n\n"
        f"Всего переводчиков: {len(translators)}\n"
        f"Всего клиентов: {len(clients)}\n"
        f"Соотношение переводчиков/клиентов: {len(translators)/len(clients) if len(clients) > 0 else len(translators):.2f}\n\n"
    )
    
    # Client verification info
    summary += (
        f"*Верификация клиентов:*\n"
        f"• Подтверждённых клиентов: {verified_clients}\n"
        f"• Неподтверждённых клиентов: {unverified_clients}\n"
        f"• Подозрительных верификаций: {len(suspicious_verifications)}\n\n"
    )
    
    if translator_prices:
        summary += (
            f"*Информация о ценах:*\n"
            f"• Средняя цена: {avg_price:.2f}€\n"
            f"• Минимальная цена: {min_price:.2f}€\n"
            f"• Максимальная цена: {max_price:.2f}€\n\n"
        )
    
    summary += f"*Переводчики по городам:*\n"
    for city, count in sorted(translator_count_by_city.items()):
        summary += f"• {city}: {count}\n"
    
    summary += "\n*Клиенты по городам:*\n"
    for city, count in sorted(client_count_by_city.items()):
        summary += f"• {city}: {count}\n"
    
    summary += "\n*Уровни немецкого у переводчиков:*\n"
    for level, count in sorted(translator_levels.items()):
        summary += f"• {level}: {count}\n"
        
    # Add suspicious verifications if any
    if suspicious_verifications:
        summary += "\n*Подозрительные верификации клиентов:*\n"
        for i, sv in enumerate(suspicious_verifications, 1):
            summary += f"• Пользователь {sv.get('user_id', 'Неизвестно')} из {sv.get('city', 'Неизвестно')} - "
            verification = sv.get('verification_text', '')
            if len(verification) > 30:
                verification = verification[:27] + "..."
            summary += f"\"{verification}\"\n"
            
            # Limit to 5 suspicious users to avoid message size limits
            if i >= 5 and len(suspicious_verifications) > 5:
                summary += f"... и ещё {len(suspicious_verifications) - 5}\n"
                break
        
    return summary
