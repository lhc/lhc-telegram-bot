import datetime

import httpx
import humanize
import os
import parsel
# import pytz
import time
from telegram.constants import ParseMode

from joker import settings


async def send_lhc_status(context, chat_id, requested=True):
    tz_saved = os.environ['TZ']
    os.environ['TZ'] = 'America/Sao_Paulo'
    time.tzset()
    humanize.activate("pt_BR")
    response = httpx.get("https://status.lhc.net.br/").json()

    last_change = datetime.datetime.fromtimestamp(
        response["state"]["lastchange"]
    )
    lastchange_delta = datetime.datetime.now() - last_change

    if requested or lastchange_delta.totalseconds() > 1800:
        status = "🔓 aberto" if response["state"]["open"] else "🔒 fechado"

        last_change = datetime.datetime.fromtimestamp(
            response["state"]["lastchange"]
        )
        humanized_last_change = humanize.precisedelta(last_change)
        raw_last_change = last_change.strftime("%Y-%m-%d %H:%M:%S")

        await context.bot.send_message(
            chat_id,
            text=f"""O LHC está {status} há {humanized_last_change}
(última alteração em {raw_last_change})""",
        )
    os.environ['TZ'] = tz_saved
    time.tzset()


async def status(update, context):
    await send_lhc_status(context, update.message.chat_id, requested=True)


async def recurring_status(context):
    await send_lhc_status(context, settings.LHC_CHAT_ID, requested=False)


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


async def send_status_infra(context, chat_id):
    await context.bot.send_message(
        chat_id,
        text=_get_status_infra(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


async def status_infra(update, context):
    await send_status_infra(context, update.message.chat_id)


async def recurring_status_infra(context):
    await send_status_infra(context, settings.LHC_CHAT_ID)
