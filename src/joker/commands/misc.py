import random
from importlib import resources


async def batima(update, context):
    batima_resource = resources.files("joker") / "assets/batima.jpg"
    with open(batima_resource, "rb") as batima_file:
        await context.bot.send_photo(update.message.chat_id, batima_file)


async def boom(update, context):
    boom_resource = resources.files("joker") / "assets/boom.mp4"
    with open(boom_resource, "rb") as boom_file:
        await context.bot.send_animation(
            chat_id=update.message.chat_id, animation=boom_file
        )


async def quemsou(update, context):
    joker_resource = resources.files("joker") / "assets/joker.png"
    with open(joker_resource, "rb") as joker_file:
        await context.bot.send_photo(
            update.message.chat_id,
            joker_file,
            caption="Eu sou um palhaço, eu sou o coringa, o palhaço, o Joker, o palhaço!",
        )


async def non_commands(update, context):
    message = update.message.text

    messages_to_reply = {
        "/quém": "\U0001F986",
        "/grama": random.choice(["\U0001F331", "\U0001F33F", "\U0001F343"]),
        "/boo": "\U0001F47B",
    }
    reply_message = messages_to_reply.get(message)
    if reply_message is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=reply_message
        )

    if message.startswith("/") and reply_message is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Eu ainda não sei o que você quer dizer com isso...",
        )
