import datetime

from ics import Calendar


def quando(update, context):
    with open("lhc.ics", "r") as f:
        calendar = Calendar(f.read())

    future_events = list(
        {
            event
            for event in calendar.events
            if event.begin.date() >= datetime.date.today()
        }
    )
    next_event = min(future_events, key=lambda e: e.begin)
    event = {
        "title": next_event.name,
        "date": next_event.begin.strftime("%d/%m/%Y"),
        "url": next_event.url,
    }
    next_event_msg = f"Vai rolar \"{event['title']}\" em {event['date']}. Mais informações em {event['url']}."
    context.bot.send_message(update.message.chat_id, text=next_event_msg)
