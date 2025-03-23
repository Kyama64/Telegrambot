#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data management functions for the Telegram bot.
"""

import logging
import json
import os
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# In-memory storage
_users = {}  # user_id -> user_type (translator or client)
_translators = {}  # user_id -> translator data
_clients = {}  # user_id -> client data

# File paths for persistence
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TRANSLATORS_FILE = os.path.join(DATA_DIR, "translators.json")
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Load data from files if they exist
def load_data():
    """Load all data from persistence files."""
    global _users, _translators, _clients
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                _users = json.load(f)
        
        if os.path.exists(TRANSLATORS_FILE):
            with open(TRANSLATORS_FILE, 'r', encoding='utf-8') as f:
                _translators = json.load(f)
        
        if os.path.exists(CLIENTS_FILE):
            with open(CLIENTS_FILE, 'r', encoding='utf-8') as f:
                _clients = json.load(f)
                
        # Convert string keys to integers
        _users = {int(k): v for k, v in _users.items()}
        _translators = {int(k): v for k, v in _translators.items()}
        _clients = {int(k): v for k, v in _clients.items()}
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading data: {e}")


# Save data to files
def save_data():
    """Save all data to persistence files."""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_users, f, ensure_ascii=False, indent=4)
        
        with open(TRANSLATORS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_translators, f, ensure_ascii=False, indent=4)
        
        with open(CLIENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_clients, f, ensure_ascii=False, indent=4)
    
    except IOError as e:
        logger.error(f"Error saving data: {e}")


# User type management
def save_user_type(user_id: int, user_type: str) -> None:
    """Save the user type for a given user ID."""
    _users[user_id] = user_type
    save_data()


def get_user_type(user_id: int) -> Optional[str]:
    """Get the user type for a given user ID."""
    return _users.get(user_id)


# Translator data management
def save_translator_data(user_id: int, data: Dict[str, Any]) -> None:
    """Save translator data for a given user ID."""
    _translators[user_id] = data
    save_data()


def get_translator_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get translator data for a given user ID."""
    return _translators.get(user_id)


def get_translator_list() -> List[Dict[str, Any]]:
    """Get a list of all translators with their data."""
    return [
        {"user_id": user_id, **data}
        for user_id, data in _translators.items()
    ]


def get_translators_by_city(city: str) -> List[Dict[str, Any]]:
    """Get a list of translators in a specific city."""
    city = city.lower()
    return [
        {"user_id": user_id, **data}
        for user_id, data in _translators.items()
        if data.get('city', '').lower() == city
    ]


# Client data management
def save_client_data(user_id: int, data: Dict[str, Any]) -> None:
    """Save client data for a given user ID."""
    _clients[user_id] = data
    save_data()


def get_client_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get client data for a given user ID."""
    return _clients.get(user_id)


def get_client_list() -> List[Dict[str, Any]]:
    """Get a list of all clients with their data."""
    return [
        {"user_id": user_id, **data}
        for user_id, data in _clients.items()
    ]


def get_clients_by_city(city: str) -> List[Dict[str, Any]]:
    """Get a list of clients in a specific city."""
    city = city.lower()
    return [
        {"user_id": user_id, **data}
        for user_id, data in _clients.items()
        if data.get('city', '').lower() == city
    ]


# Spam detection
def is_spam_message(text: str) -> bool:
    """
    Basic spam detection.
    Returns True if the message appears to be spam.
    """
    # Basic spam detection rules with Russian support
    spam_patterns = [
        r'https?://(?!t\.me)',  # Links except Telegram links
        
        # English spam words
        r'(?i)viagra|casino|lottery|winner|prize|money|bitcoin|crypto',
        
        # Russian spam words
        r'(?i)казино|лотерея|выигрыш|приз|деньги|биткоин|крипто|обогащение|доход',
        r'(?i)заработок онлайн|быстрые деньги|инвестиции|вложения|пассивный доход',
        
        r'\+\d{9,}',  # International phone numbers (not related to translation services)
    ]
    
    # Check if any pattern matches
    for pattern in spam_patterns:
        if re.search(pattern, text):
            return True
            
    # Check for excessive capitalization
    if sum(1 for c in text if c.isupper()) / max(1, len(text)) > 0.7:
        return True
        
    return False


# Initialize data
load_data()
