import math

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler


def pizza(update, context):
    numeric_keyboard = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
    update.message.reply_text(
        "Quantas pessoas vão querer pizza \U0001F355 ???",
        reply_markup=ReplyKeyboardMarkup(numeric_keyboard, one_time_keyboard=True),
    )
    return 1

def try_parse_int(text):
    try:
        ret = int(text)
    except ValueError:
        return 0, ValueError
    finally:
        return ret, None

def pizza_calculator(update, context):
    text = update.message.text
    context.user_data["choice"] = text

    no_pessoas, err = try_parse_int(text)
    if err is not None:
        reply_message = "Muito engraçado, hein?"
    elif no_pessoas < 0:
        reply_message = "Número negativo de pizzas? Não viramos uma pizzaria."
    elif no_pessoas == 0:
        reply_message = "Para nenhuma pessoa, é melhor nem comprar pizza."
    elif 1 <= no_pessoas <= 100:
        no_pizzas = math.ceil(3 * (no_pessoas + 1) / 8)
        reply_message = (
            f"Para {no_pessoas} pessoas, compre {no_pizzas} pizzas de 8 \U0001F355."
        )
    elif no_pessoas > 100:
        reply_message = "Mais que 100 pessoas no LHC? Isso vai dar overflow nos meus cálculos, se vira aí."
    else:
        reply_message = "Eu não entendi o que você quis dizer com isso."

    update.message.reply_text(reply_message, reply_markup=ReplyKeyboardRemove())

    return -1


pizza_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("pizza", pizza)],
    states={1: [MessageHandler(Filters.regex(r"^\d+$"), pizza_calculator)]},
    fallbacks=[],
)
