import math
import time
import httpx
from importlib import resources

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters


async def pizza(update, context):
    numeric_keyboard = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
    await update.message.reply_text(
        "Quantas pessoas vão querer \U0001F355pizza?",
        reply_markup=ReplyKeyboardMarkup(numeric_keyboard, one_time_keyboard=True),
    )
    return 1


async def preco_pizza(cache={'last_update': 0}):
    # Essa função é Go-Horse puro! :)

    if time.time() - cache['last_update'] < 3600 * 24 * 7:
        return cache

    try:
        URL = 'https://deliverydireto.com.br/megapizzaforneria/megapizzaforneria?dd=menu'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0'
        }

        contents = httpx.get(URL, headers=headers)

        found = False
        json_contents = []

        for line in contents.text.split('\n'):
          line = line.strip()
          if found:
            if not line:
              break
            json_contents.append(line)
          if '<script id="googlePlaceActionsScript" type="application/ld+json" async>' in line:
            found = True

        contents = '\n'.join(json_contents)
        contents = contents.replace('</script>', '')
        contents = json.loads(contents)

        def eh_pizza(item):
          return item['name'].endswith(' FATIAS')

        def num_pedacos(nome):
          return int(nome.split(' ')[-2])

        pizzas = {
            num_pedacos(item['name']): item['offers']['price']
            for item in contents['owns']
            if eh_pizza(item)
        }

    except:
        pass

    finally:
        cache.update(pizzas)
        cache['last_update'] = time.time()

    return cache

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
            reply_message = ""
            for pedacos in (1, 2, 3):
                reply_message += f"Com {no_pessoas} pessoa{'s' if no_pessoas > 1 else ''} comendo {pedacos} pedaço{'s' if pedacos > 1 else ''}\U0001F355 cada:\n"
                ultimo_calculo = -1

                precos = await preco_pizza()

                for tamanho in (8, 16, 22):
                    no_pizzas = math.ceil((pedacos * no_pessoas) / tamanho)
                    if no_pizzas != ultimo_calculo:
                        reply_message += f"• {no_pizzas} {'pizzas' if no_pizzas > 1 else 'pizza'} de {tamanho} pedaços{preco}"

                        preco = precos.get(tamanho, 0)
                        if preco:
                            preco_total = no_pizzas * preco
                            reply_message += f' no total de R${preco_total:.2f} (R${preco_total / no_pessoas:.2f} por pessoa)'

                        sobra = no_pizzas * tamanho - pedacos * no_pessoas
                        if sobra == 1:
                            reply_message += f" (sobra {sobra} pedaço)"
                        elif sobra > 1:
                            reply_message += f" (sobram {sobra} pedaços)"

                        reply_message += "\n"
                        ultimo_calculo = no_pizzas
                reply_message += "\n"

        elif no_pessoas > 100:
            reply_message = "Mais que 100 pessoas no LHC? Isso vai dar overflow nos meus cálculos, se vira aí."
        else:
            reply_message = "Eu não entendi o que você quis dizer com isso."

    await update.message.reply_text(reply_message, reply_markup=ReplyKeyboardRemove())

    return -1


async def pizza_not_a_number(update, context):
    sticker_path = resources.files("joker") / "assets/sai-hacker.png"
    with open(sticker_path, "rb") as sticker:
        await update.message.reply_sticker(
            sticker,
            reply_markup=ReplyKeyboardRemove()
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
