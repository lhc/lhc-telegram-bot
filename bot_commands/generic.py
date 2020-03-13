import logging
import random

from dynaconf import settings
from telegram import ParseMode

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("joker")


def batima(update, context):
    with open("media/batima.jpg", "rb") as batima:
        context.bot.send_photo(update.message.chat_id, batima)


def boom(update, context):
    with open("media/boom.mp4", "rb") as boom:
        context.bot.send_animation(chat_id=update.message.chat_id, animation=boom)


def quemsou(update, context):
    with open("media/joker.png", "rb") as joker:
        context.bot.send_photo(
            update.message.chat_id,
            joker,
            caption="Eu sou um palhaço, eu sou o coringa, o palhaço, o Joker, o palhaço!",
        )


def onde(update, context):
    message = update.message.text

    if message and message.startswith("/") and message == 'onde':
        with open("media/maps-link.html", "r") as link:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=link,
                parse_mode=ParseMode.HTML
            )


def non_commands(update, context):
    message = update.message.text

    messages_to_reply = {
        "/quém": "\U0001F986",
        "/grama": random.choice(["\U0001F331", "\U0001F33F", "\U0001F343"]),
        "/boo": "\U0001F47B",
    }
    reply_message = messages_to_reply.get(message)
    if reply_message is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

    if message.startswith("/") and reply_message is None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Eu ainda não sei o que você quer dizer com isso...",
        )
