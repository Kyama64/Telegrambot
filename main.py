#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the Translation Service Telegram Bot and Admin Web Interface.
"""

import logging
import os
import threading
import time
from flask import Flask, render_template, jsonify, request, redirect, url_for
from bot import create_bot, run_bot, get_group_info
from data_manager import get_translator_list, get_client_list, get_translators_by_city, get_clients_by_city
from config import ADMIN_USER_IDS, GROUP_USERNAME

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Store bot instance
bot_instance = None

def start_bot_thread():
    """Start the bot in a separate thread."""
    global bot_instance
    
    logger.info("Starting the Translation Service Bot")
    token = os.getenv("TELEGRAM_BOT_TOKEN","7880135656:AAGzSy3FKl_AZd28Bvq1kC0pa9yeZWRxGu4")
    
    if not token:
        logger.error("No bot token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
        
    try:
        if bot_instance:
            logger.info("Stopping existing bot instance")
            asyncio.run(bot_instance.stop())
            bot_instance = None
            
        bot_instance = create_bot(token)
        logger.info("Bot instance created successfully")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        return None
    
    # Start bot in a separate thread with proper thread name
    bot_thread = threading.Thread(
        target=run_bot, 
        args=(bot_instance,), 
        name="TelegramBotThread",
        daemon=True
    )
    bot_thread.start()
    
    # Give the bot some time to initialize
    time.sleep(1)
    
    return bot_instance

# Routes for the web interface
@app.route('/')
def index():
    """Admin dashboard homepage."""
    return render_template('index.html', 
                          translator_count=len(get_translator_list()), 
                          client_count=len(get_client_list()),
                          group_name=GROUP_USERNAME)

@app.route('/translators')
def translators():
    """View all translators."""
    city_filter = request.args.get('city')
    
    if city_filter:
        translators_list = get_translators_by_city(city_filter)
    else:
        translators_list = get_translator_list()
        
    return render_template('translators.html', 
                          translators=translators_list,
                          city_filter=city_filter)

@app.route('/clients')
def clients():
    """View all clients."""
    city_filter = request.args.get('city')
    
    if city_filter:
        clients_list = get_clients_by_city(city_filter)
    else:
        clients_list = get_client_list()
        
    return render_template('clients.html', 
                          clients=clients_list,
                          city_filter=city_filter)

@app.route('/api/stats')
def api_stats():
    """Return statistics as JSON for API consumers."""
    return jsonify({
        'translator_count': len(get_translator_list()),
        'client_count': len(get_client_list()),
        'cities': {
            'translators': list(set(t.get('city', '') for t in get_translator_list())),
            'clients': list(set(c.get('city', '') for c in get_client_list()))
        }
    })

@app.route('/start-bot', methods=['POST'])
def start_bot_route():
    """Start the bot from the web interface."""
    global bot_instance
    
    # Always restart the bot even if it's already running
    # This ensures we get a clean start
    start_bot_thread()
    
    return jsonify({'status': 'success', 'message': 'Bot started successfully'})

def main():
    """Initialize and run the bot."""
    # Check if we're running with gunicorn
    if os.environ.get('GUNICORN_CMD_ARGS') is not None:
        # When running with gunicorn, just return the app
        # The bot will be started by the '/start-bot' endpoint
        pass
    else:
        # Running as script directly, just start the bot without Flask
        start_bot_thread()
        
        try:
            # Keep the script running
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()
