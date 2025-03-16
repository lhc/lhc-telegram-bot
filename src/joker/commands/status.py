import httpx
import parsel
import datetime
from telegram.constants import ParseMode

from joker import settings


async def status(update, context):
    response = httpx.get("https://status.lhc.net.br/").json()

    status = "aberto" if response["state"]["open"] else "fechado"

    last_change = datetime.utcfromtimestamp(response["state"]["lastchange"])
    last_change = last_change.strftime("%Y-%m-%d %H:%M:%S")

    await context.bot.send_message(
        update.message.chat_id,
        text=f"O LHC está {status} desde {last_change}",
    )

async def quem(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text="Eu não faço a menor ideia quem está no LHC agora.",
    )


def _get_status_infra():
    response = httpx.get(settings.MONTASTIC_RSS_URL)
    rss = parsel.Selector(response.text)
    statuses = rss.css("item title::text").getall()

    status_emojis = {
        "[OK]": "🟢",
        "[Alert]": "🔴",
    }
    formatted_statuses = []
    for status in sorted(statuses):
        condition, _ = status.split(" - ")
        emoji = status_emojis.get(condition, "🟡")
        formatted_statuses.append(status.replace(condition, emoji))

    if formatted_statuses:
        status_msg = "\n".join(formatted_statuses)
        return f"Status da infraestrutura do LHC:\n\n{status_msg}"

    return "🔴 Não foi possível obter o status da infraestrutura do LHC."


async def status_infra(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text=_get_status_infra(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


async def recurring_status_infra(context):
    await context.bot.send_message(
        settings.LHC_CHAT_ID,
        text=_get_status_infra(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
