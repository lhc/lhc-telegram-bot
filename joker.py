import logging
import math
import random
from commands import generic, status
from datetime import datetime

import requests
from dynaconf import settings
from ics import Calendar
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from models import Status, db

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("joker")


# def quando(update, context):
#     with open("lhc.ics", "r") as f:
#         calendar = Calendar(f.read())
#     next_event = min(list(calendar.events), key=lambda e: e.begin)
#     event = {
#         "title": next_event.name,
#         "date": next_event.begin.strftime("%d/%m/%Y"),
#         "url": next_event.url,
#     }
#     next_event_msg = f"Vai rolar \"{event['title']}\" em {event['date']}. Mais informações em {event['url']}."
#     context.bot.send_message(update.message.chat_id, text=next_event_msg)


# def grana(update, context):
#     context.bot.send_message(
#         update.message.chat_id,
#         text="Eu ainda não sei como verificar a situação financeira do LHC... mas você sempre pode [fazer uma doação via PayPal](http://bit.ly/doe-para-o-lhc) e ajudar a manter o hackerspace!",
#         parse_mode="Markdown",
#     )


# def historico(update, context):
#     context.bot.send_message(update.message.chat_id, text="\U0001F914")


# def pizza(update, context):
#     numeric_keyboard = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
#     update.message.reply_text(
#         "Quantas pessoas vão querer pizza \U0001F355 ???",
#         reply_markup=ReplyKeyboardMarkup(numeric_keyboard, one_time_keyboard=True),
#     )
#     return 1


# def pizza_calculator(update, context):
#     text = update.message.text
#     context.user_data["choice"] = text

#     no_pessoas = int(text)
#     if no_pessoas < 0:
#         reply_message = "Número negativo de pizzas? Não viramos uma pizzaria."
#     elif no_pessoas == 0:
#         reply_message = "Para nenhuma pessoa, é melhor nem comprar pizza."
#     elif 1 <= no_pessoas <= 100:
#         no_pizzas = math.ceil(3 * (no_pessoas + 1) / 8)
#         reply_message = (
#             f"Para {no_pessoas} pessoas, compre {no_pizzas} pizzas de 8 \U0001F355."
#         )
#     elif no_pessoas > 100:
#         reply_message = "Mais que 100 pessoas no LHC? Isso vai dar overflow nos meus cálculos, se vira aí."
#     else:
#         reply_message = "Eu não entendi o que você quis dizer com isso."

#     update.message.reply_text(reply_message, reply_markup=ReplyKeyboardRemove())

#     return -1


def init_bot():
    logger.info("Joker bot started.")
    updater = Updater(settings.TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    db.create_tables([Status])

    updater.job_queue.run_repeating(status.status_check, interval=60, first=0)
    dispatcher.add_handler(CommandHandler("quem", status.quem))
    dispatcher.add_handler(CommandHandler("status", status.status))

    # dispatcher.add_handler(CommandHandler("quando", quando))

    # dispatcher.add_handler(CommandHandler("grana", grana))

    # dispatcher.add_handler(CommandHandler("historico", historico))

    # pizza_conversation_handler = ConversationHandler(
    #     entry_points=[CommandHandler("pizza", pizza)],
    #     states={1: [MessageHandler(Filters.regex(r"^\d+$"), pizza_calculator)]},
    #     fallbacks=[],
    # )
    # dispatcher.add_handler(pizza_conversation_handler)

    dispatcher.add_handler(CommandHandler("quemsou", generic.quemsou))
    dispatcher.add_handler(CommandHandler("batima", generic.batima))
    dispatcher.add_handler(CommandHandler("boom", generic.boom))

    # This dispatcher must be the last included
    dispatcher.add_handler(MessageHandler(Filters.text, generic.non_commands))

    logger.info("Command handlers set. Start pooling.")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    init_bot()
