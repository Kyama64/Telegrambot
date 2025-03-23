"""
Custom filters for message processing.
"""
import re
from telegram.ext import filters

def create_spam_filter():
    """
    Create a filter to detect and filter out spam messages.
    This is a basic implementation that can be expanded.
    """
    # Define spam patterns (including Russian)
    spam_patterns = [
        # English patterns
        r'bitcoin',
        r'crypto',
        r'earn money fast',
        r'get rich',
        r'investment opportunity',
        r'\b(viagra|cialis)\b',
        r'https?:\/\/.*\.(ru|cn|bid|click|top|tk)',  # Suspicious domains
        r'casino',
        r'lottery',
        r'prize',
        r'you\'ve won',
        # Russian patterns
        r'биткоин',
        r'крипт(о|а|у|ой|е)',
        r'быстрый заработок',
        r'заработ(ок|ать) быстро',
        r'инвестиционн(ая|ый|ое) возможност(ь|и)',
        r'казино',
        r'лотере(я|и|ю)',
        r'выигр(ыш|ал|ать)',
        r'заработ(ай|аешь|ать|ок) деньги',
        r'доход от',
        r'зарабатыва(й|ть)',
        r'обогащение',
        r'разбогате(й|ть)',
        r'выплат(а|ы) каждый день',
        r'работа из дома',
        r'удаленная работа',
    ]
    
    # Compile regex patterns
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in spam_patterns]
    
    # Create a custom filter
    def spam_filter(message):
        """Return True if the message is spam."""
        if not message.text:
            return False
            
        text = message.text.lower()
        
        # Check for spam patterns
        for pattern in compiled_patterns:
            if pattern.search(text):
                return True
                
        # Check for excessive URLs or mentions
        url_count = len(re.findall(r'https?:\/\/\S+', text))
        mention_count = len(re.findall(r'@\w+', text))
        
        if url_count > 3 or mention_count > 5:
            return True
            
        return False
    
    # Return as a negated filter (passes when NOT spam)
    return filters.create(spam_filter, "SpamFilter")
