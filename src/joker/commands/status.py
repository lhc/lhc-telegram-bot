import datetime
from importlib import resources

import httpx
import humanize
import parsel
import pytz
import random
from telegram.constants import ParseMode

from joker import settings

previous_lhc_status = None


def resource_when_closed():
    if random.randint(0, 100) > 70:
        return random.choice((
            "assets/lhc-fechado-olhinhos.jpg",
            "assets/0.mp4",
            "assets/1.mp4",
            "assets/2.mp4",
            "assets/3.mp4",
            "assets/4.mp4",
            "assets/5.mp4",
        ))
    return "assets/lhc-fechado.jpg"

async def send_lhc_status(context, chat_id, requested=True):
    SAO_PAULO_TZ = pytz.timezone("America/Sao_Paulo")
    humanize.activate("pt_BR")

    response = httpx.get("https://status.lhc.net.br/").json()

    # Se o HomeAssistant rebootar por algum motivo (por exemplo durante
    # uma atualização de sistema), ou a chave mudar de "fechada" para
    # "aberto para associados" (que é tecnicamente uma mudança de
    # estado mas publicamente continua fechado), evita mostrar
    # mensagens de estado automáticas a não ser que o estado seja
    # diferente da vez anterior que o timer expirou.
    if not requested:
        global previous_lhc_status
        if response["state"]["open"] == previous_lhc_status:
            return
        previous_lhc_status = response["state"]["open"]

    last_change = datetime.datetime.fromtimestamp(
        response["state"]["lastchange"], tz=SAO_PAULO_TZ
    )
    last_change_delta = datetime.datetime.now(tz=SAO_PAULO_TZ) - last_change
    if (
        requested
        or last_change_delta.total_seconds() < settings.STATUS_CHECK_INTERVAL * 60
    ):
        extra = ""
        if response["state"]["open"]:
            status = "🔓aberto"
            resource_name = "assets/lhc-aberto.jpg"
            if last_change_delta.total_seconds() > 86400:
                extra = ". Nunca vi o LHC aberto continuamente tanto tempo assim. Provavelmente alguém esqueceu a chave ligada e foi embora."
        else:
            status = "🔒fechado"
            resource_name = resource_when_closed()

        humanized_last_change = humanize.naturaltime(last_change)
        raw_last_change = last_change.strftime("%Y-%m-%d %H:%M:%S")

        msg = f"""O LHC está {status} {humanized_last_change}
(última alteração em {raw_last_change}){extra}"""

        resource_file_name = resources.files("joker") / resource_name
        async with open(resource_file_name, "rb") as status_file:
            if resource_name.endswith(".mp4"):
                await context.bot.send_animation(chat_id, status_file, caption=msg)
            else:
                await context.bot.send_photo(chat_id, status_file, caption=msg)


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
