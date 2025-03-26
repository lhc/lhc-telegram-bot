import datetime

import httpx
import humanize
import parsel
import pytz
from telegram.constants import ParseMode

from joker import settings

humanize.activate("pt_BR")

async def send_lhc_status(context, chat_id, requested=True):
    response = httpx.get("https://status.lhc.net.br/").json()

    lastchange = response["state"]["lastchange"]
    if requested or (datetime.datetime.now() - lastchange).totalseconds() > 1800:
        em_sao_paulo = datetime.datetime.fromtimestamp(lastchange, tz=pytz.timezone("America/Sao_Paulo"))
        data_hora = em_sao_paulo.strftime("%Y-%m-%d %H:%M:%S")
        humanizada = humanize.naturaltime(em_sao_paulo)

        status = "🔓aberto" if response["state"]["open"] else "🔒fechado"

        await context.bot.send_message(
            update.message.chat_id,
            text=f"O LHC está {status} há {humanizada}.\n\nÚltima mudança de estado ocorreu em {data_hora}.",
        )

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
