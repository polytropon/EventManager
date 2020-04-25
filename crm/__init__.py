
import os
import logging

from datetime import datetime
from custom_utils.template import simple_render

from celery.task import task
from aldryn_celery.celery import app
from tasks_app.tasks import sendTelegram, send_mail

__all__ = ["os","logging","send_mail","datetime","simple_render","send_mail"]
import telegram

logger = logging.getLogger("telegram_logger")
from logging import Handler
logger.setLevel("INFO")
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')



try:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
# ## Solution:
# ##https://github.com/python-telegram-bot/python-telegram-bot/issues/538
    # def sendTelegram(message):
    #     ## chat_id is integer in url of telegram group
    #     bot.send_message(chat_id=-486822659, text=message)
    
    class TelegramHandler(Handler):
        def emit(self, record):
            sendTelegram.delay(record.msg)
    logger.addHandler(TelegramHandler())
    logger.info("Logging in " + os.getenv("ENVIRONMENT"))
except:
    pass

