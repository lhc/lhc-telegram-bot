import httpx
import parsel

from joker import settings


async def status(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text="O LHC pode estar aberto \U0001F513 ou fechado \U0001F512. Eu não consegui descobrir.",
    )


async def quem(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text="Eu não faço a menor ideia quem está no LHC agora.",
    )


async def status_infra(update, context):
    response = httpx.get(settings.MONTASTIC_RSS_URL)
    rss = parsel.Selector(response.text)
    status = rss.css("item title::text").getall()
    status_msg = "\n".join(sorted(status))
    await context.bot.send_message(
        update.message.chat_id,
        text=f"Status da infraestrutura do LHC:\n\n{status_msg}",
    )
