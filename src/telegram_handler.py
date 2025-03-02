import logging
import socket
import json
from telegram import Bot
import asyncio

class TelegramHandler(logging.Handler):
    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=self.bot_token)

    def emit(self, record):
        log_entry = self.format(record)
        try:
            asyncio.get_event_loop().create_task(self.bot.send_message(chat_id=self.chat_id, text=log_entry)) 
        except Exception as e:
            print("Error sending log telegram:", e)

if __name__ == '__main__':

    # Configure the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    telegram_handler = TelegramHandler('***********************************', '********************')

    # Add the handler to the logger
    logger.addHandler(telegram_handler)

    # Test logging
    logger.debug('This is a debug message.')
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    logger.critical('This is a critical message.')