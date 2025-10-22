import datetime
import logging
import time
from dataclasses import dataclass

import httpx
import ics
from telegram.constants import ParseMode

from joker import settings

logger = logging.getLogger("joker")


@dataclass
class Event:
    date: datetime.date
    name: str
    url: str


def _future_event_filter(event):
    return event.begin.date() > datetime.date.today() or (
        event.begin.date() == datetime.date.today()
        and event.begin.time() >= datetime.datetime.now().time()
    )

def _today_event_filter(event):
    return event.begin.date() == datetime.date.today() and (
        event.begin.time() >= datetime.datetime.now().time()
    )

def _today_for_status_filter(event):
    return event.begin.date() == datetime.date.today()

def _no_filter(event):
    return True

EVENT_FILTERS = {
    'future': _future_event_filter,
    'today': _today_event_filter,
    'today_for_status': _today_for_status_filter,
}


def try_hard_to_get(url, tries=4):
    for _ in range(tries):
        try:
            return httpx.get(url)
        except httpx.ReadTimeout:
            time.sleep(1)

    class EmptyResponse:
        text = ''
    return EmptyResponse()


def get_events(when=""):
    response = try_hard_to_get(settings.ICS_LOCATION)
    calendar = ics.Calendar(response.text)
    filter = EVENT_FILTERS.get(when, _no_filter)
    return list(event for event in calendar.events if filter(event))


async def quando(update, context):
    future_events = get_events("future")
    next_event = min(future_events, key=lambda e: e.begin)
    logger.info(f"Next Event: {next_event}")
    if next_event:
        event = {
            "title": next_event.name,
            "date": next_event.begin.strftime("%d/%m/%Y"),
            "url": next_event.url,
        }
        next_event_msg = f"Vai rolar \"{event['title']}\" em {event['date']}. Mais informações em {event['url']}."
        await context.bot.send_message(update.message.chat_id, text=next_event_msg)
    else:
        await context.bot.send_message(
            update.message.chat_id,
            text="Não existe nenhum evento agendado até o momento.",
        )


def get_semana():
    today = datetime.date.today()
    future_events = get_events("future")
    end_of_week = today + datetime.timedelta(days=7)

    week_events = []
    for event in future_events:
        if event.begin.date() > end_of_week:
            continue
        week_events.append(
            Event(
                date=event.begin.strftime("%d/%m/%Y"),
                name=event.name,
                url=event.url,
            )
        )

    if not week_events:
        message = "Não existe nenhum evento agendado nos próximos 7 dias 😞"
    else:
        week_events = sorted(week_events, key=lambda e: e.date)
        events_details = "\n".join(
            [
                f"- *{event.date}* - [{event.name}]({event.url})"
                for event in week_events
            ]
        )
        message = f"""**🔜 Agenda para os próximos 7 dias:**

{events_details}

🗓️ [Acesse aqui a agenda completa do LHC](https://eventos.lhc.net.br/)"""

    return message


async def semana(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text=get_semana(),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def recurring_semana(context):
    await context.bot.send_message(
        settings.LHC_CHAT_ID,
        text=get_semana(),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def pin_today_event(update, context):
    today_events = get_events("today")
    today_event = min(today_events, key=lambda e: e.begin)
    if today_event:
        event = {
            "title": today_event.name,
            "date": today_event.begin.strftime("%d/%m/%Y"),
            "url": today_event.url,
        }
        today_event_msg = f"**Hoje** {event['date']} vai rolar \"{event['title']}\". Mais informações em {event['url']}."

        message = await context.bot.send_message(
            settings.LHC_CHAT_ID,
            text=today_event_msg,
            parse_mode=ParseMode.MARKDOWN,
        )

        await context.bot.pin_chat_message(
            settings.LHC_CHAT_ID, message.message_id, disable_notification=False
        )
    else:
        chat = update.message.bot.get_chat(settings.LHC_CHAT_ID)
        pinned_message = chat.pinned_message
        if pinned_message.from_user.username == "lhc_joker_bot":
            await context.bot.pin_chat_message(
                settings.LHC_CHAT_ID, pinned_message.message_id
            )
