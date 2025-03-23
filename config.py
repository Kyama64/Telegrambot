#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration settings for the Telegram bot.
"""

import os

# Bot configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Application configuration
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Language configuration
USE_RUSSIAN = True  # Set to True to use Russian language, False for English

# Group configuration
GROUP_USERNAME = "dolmecher"  # Username of your Telegram group without @
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID")  # Will be obtained and set when bot joins the group

# Spam filter configuration
MAX_MESSAGES_PER_MINUTE = 5  # Maximum messages a user can send per minute

# Admin user IDs (for admin-only commands)
# Default to your user ID (from testing) if environment variable not set
ADMIN_USER_IDS = [int(id_str) for id_str in os.environ.get("ADMIN_USER_IDS", "892197915").split(",") if id_str]

# Message trigger phrases
TRANSLATOR_FOUND_PHRASES = ["переводчик найден", "translator found", "нашел переводчика", "нашла переводчика"]
NEED_REPLACEMENT_PHRASES = ["нужна замена", "need replacement", "ищу замену", "требуется замена"]

# Cities in Germany (for validation and suggestions) - including Russian names
GERMAN_CITIES = [
    # German/English names
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf",
    "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden", "Hanover", "Nuremberg",
    "Duisburg", "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster", "Karlsruhe",
    "Mannheim", "Augsburg", "Wiesbaden", "Gelsenkirchen", "Mönchengladbach",
    "Braunschweig", "Chemnitz", "Kiel", "Aachen", "Halle", "Magdeburg", "Freiburg",
    "Krefeld", "Lübeck", "Oberhausen", "Erfurt", "Mainz", "Rostock", "Kassel",
    "Hagen", "Hamm", "Saarbrücken", "Mülheim", "Potsdam", "Ludwigshafen", "Oldenburg",
    "Leverkusen", "Osnabrück", "Solingen", "Heidelberg", "Herne", "Neuss", "Darmstadt",
    
    # Russian names
    "Берлин", "Гамбург", "Мюнхен", "Кёльн", "Франкфурт", "Штутгарт", "Дюссельдорф",
    "Дортмунд", "Эссен", "Лейпциг", "Бремен", "Дрезден", "Ганновер", "Нюрнберг",
    "Дуйсбург", "Бохум", "Вупперталь", "Билефельд", "Бонн", "Мюнстер", "Карлсруэ",
    "Маннгейм", "Аугсбург", "Висбаден", "Гельзенкирхен", "Мёнхенгладбах",
    "Брауншвейг", "Хемниц", "Киль", "Аахен", "Галле", "Магдебург", "Фрайбург",
    "Крефельд", "Любек", "Оберхаузен", "Эрфурт", "Майнц", "Росток", "Кассель",
    "Хаген", "Хамм", "Саарбрюккен", "Мюльхайм", "Потсдам", "Людвигсхафен", "Ольденбург",
    "Леверкузен", "Оснабрюк", "Золинген", "Гейдельберг", "Херне", "Нойс", "Дармштадт"
]
