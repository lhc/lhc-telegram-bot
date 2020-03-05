def grana(update, context):
    context.bot.send_message(
        update.message.chat_id,
        text="Eu ainda não sei como verificar a situação financeira do LHC... mas você sempre pode [fazer uma doação via PayPal](http://bit.ly/doe-para-o-lhc) e ajudar a manter o hackerspace!",
        parse_mode="Markdown",
    )
