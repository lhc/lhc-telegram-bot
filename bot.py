import random
import requests
from datetime import datetime
from ics import Calendar
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


was_open = False


def lhc_state():
    response = requests.get("https://lhc.net.br/spacenet.json")
    spacenet = response.json()
    state = spacenet.get("state", {})
    return state


def is_lhc_open(state):
    return state.get("open")


def check_status_change(context):
    global was_open  # I don't like this!

    state = lhc_state()
    is_open = is_lhc_open(state)
    if is_open != was_open:
        was_open = is_open
        since = state.get("lastchange")
        since_date = datetime.fromtimestamp(since)

        response = requests.get("https://lhc.net.br/spacenet.json?whois")
        whois = response.json()
        whois_connected = whois.get("who", [])
        who_opened = whois_connected[0]

        if is_open:
            msg = f"O LHC foi aberto \U0001F513 por {who_opened} às {since_date}."
        else:
            msg = f"O LHC está fechado \U0001F512 desde {since_date}"

        context.bot.send_message(context.job.context, text=msg)


def non_commands(update, context):
    message = update.message.text

    messages_to_reply = {
        "/quém": "\U0001F986",
        "/grama": random.choice(["\U0001F331", "\U0001F33F", "\U0001F343", ]),
        "/boo": "\U0001F47B",
    }
    reply_message = messages_to_reply.get(message)
    if reply_message is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=reply_message
        )

    if message.startswith("/") and reply_message is None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Eu ainda não sei o que você quer dizer com isso..."
        )

    if "check_status_change" not in [job.name for job in context.job_queue.jobs()]:
        context.job_queue.run_repeating(check_status_change, 60, context=update.message.chat_id)


def quando(update, context):
    with open("lhc.ics", "r") as f:
        calendar = Calendar(f.read())
    next_event = min(list(calendar.events), key=lambda e: e.begin)
    event = {
        "title": next_event.name,
        "date": next_event.begin.strftime("%d/%m/%Y"),
        "url": next_event.url,
    }
    next_event_msg = f"Vai rolar \"{event['title']}\" em {event['date']}. Mais informações em {event['url']}."
    context.bot.send_message(
        update.message.chat_id,
        text=next_event_msg
    )


def quem(update, context):
    response = requests.get("https://lhc.net.br/spacenet.json?whois")
    whois = response.json()

    full_msg = []
    whois_connected = whois.get("who", [])
    no_connected = len(whois_connected)
    if no_connected == 0:
        full_msg.append("Não tem nenhuma pessoa conhecida lá...")
    else:
        space_emoji = random.choice(["\U0001F30C", "\U0001F6F0", "\U0001F680", "\U0001F6F8"])
        connected = ", ".join(sorted(list(set(whois_connected))))
        full_msg.append(f"Pessoas conhecidas no espaço {space_emoji}: {connected}.")

    no_unknown_macs = whois.get("n_unknown_macs", 0)
    if no_unknown_macs > 0:
        if no_unknown_macs == 1:
            unknown_text = random.choice([
                "Mais um gato \U0001F408, provavelmente.",
                "Mais uma pessoa desconhecida.",
                "Mais um pingüim \U0001F427, provavelmente.",
                "Mais um bando de maritacas \U0001F99C, provavelmente."
            ])
        else:
            unknown_text = "Mais {no_unknown_macs} pessoas desconhecidas."
        full_msg.append(unknown_text)

    context.bot.send_message(
        update.message.chat_id,
        text=" ".join(full_msg)
    )


def status(update, context):
    state = lhc_state()
    is_open = is_lhc_open(state)

    if is_open is None:
        context.bot.send_message(
            update.message.chat_id,
            text="Não consegui descobrir se o espaço está aberto ou fechado."
        )
    else:
        status = "aberto \U0001F513" if is_open else "fechado \U0001F512"
        since = state.get("lastchange")
        since_date = datetime.fromtimestamp(since)

        msg = f"O LHC está {status} desde {since_date}."
        context.bot.send_message(
            update.message.chat_id,
            text=msg
        )

def grana(update, context):
    context.bot.send_message(
        update.message.chat_id,
        text="Eu ainda não sei como verificar a situação financeira do LHC... mas você sempre pode [fazer uma doação via PayPal](http://bit.ly/doe-para-o-lhc) e ajudar a manter o hackerspace!",
        parse_mode="Markdown",
    )


def pizza(update, context):
    context.bot.send_message(
        update.message.chat_id,
        text="Quero... \U0001F355",
    )


def historico(update, context):
    context.bot.send_message(
        update.message.chat_id,
        text="\U0001F914",
    )


def batima(update, context):
    context.bot.send_photo(update.message.chat_id, open("batima.jpg", "rb"))


def boom(update, context):
    context.bot.send_animation(
        chat_id=update.message.chat_id,
        animation=open("boom.mp4", "rb"),
    )


API_TOKEN = "TOKEN"
updater = Updater(API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("quando", quando))
dispatcher.add_handler(CommandHandler("quem", quem))
dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CommandHandler("grana", grana))
dispatcher.add_handler(CommandHandler("batima", batima))
dispatcher.add_handler(CommandHandler("boom", boom))
dispatcher.add_handler(CommandHandler("pizza", pizza))
dispatcher.add_handler(CommandHandler("historico", historico))

dispatcher.add_handler(MessageHandler(Filters.text, non_commands))

updater.start_polling()
updater.idle()
