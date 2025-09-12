import math

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters


async def pizza(update, context):
    numeric_keyboard = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
    await update.message.reply_text(
        "Quantas pessoas vão querer pizza \U0001F355 ???",
        reply_markup=ReplyKeyboardMarkup(numeric_keyboard, one_time_keyboard=True),
    )
    return 1


async def pizza_calculator(update, context):
    text = update.message.text
    context.user_data["choice"] = text

    try:
        no_pessoas = int(text)
    except ValueError:
        reply_message = "Eu só entendo uma quantidade numérica e inteira de pessoas."
    else:
        if no_pessoas < 0:
            reply_message = "Número negativo de pizzas? Não viramos uma pizzaria."
        elif no_pessoas == 0:
            reply_message = "Para nenhuma pessoa, é melhor nem comprar pizza."
        elif 1 <= no_pessoas <= 100:
            for pedacos in (1, 2, 3):
                reply_message = f"Com {no_pessoas} pessoa{'s' if no_pessoas > 1 else ''} comendo {pedacos} pedaço{'s' if pedacos > 1 else ''}\U0001F355 cada:\n"
                ultimo_calculo = -1
                for tamanho in (8, 16, 22):
                    no_pizzas = math.ceil(pedacos * (no_pessoas + 1) / tamanho)
                    if no_pizzas != ultimo_calculo:
                        reply_message += f"• {no_pizzas} pizzas de {tamanho} pedaços\n"
                        ultimo_calculo = no_pizzas
            reply_message += "Essa quantidade é calculada para sobrar um pouco"
        elif no_pessoas > 100:
            reply_message = "Mais que 100 pessoas no LHC? Isso vai dar overflow nos meus cálculos, se vira aí."
        else:
            reply_message = "Eu não entendi o que você quis dizer com isso."

    await update.message.reply_text(reply_message, reply_markup=ReplyKeyboardRemove())

    return -1


async def pizza_not_a_number(update, context):
    await update.message.reply_text(
        "Muito engraçado, hein?", reply_markup=ReplyKeyboardRemove()
    )
    return -1


pizza_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("pizza", pizza)],
    states={
        1: [
            MessageHandler(filters.Regex(r"^\d+$"), pizza_calculator),
        ]
    },
    fallbacks=[
        MessageHandler(filters.Regex(r"^.*$"), pizza_not_a_number),
    ],
)
