import datetime
import itertools
import json
from urllib.parse import urljoin

import requests
from ics import Calendar, Event
from parsel import Selector


def grupy_campinas_events():
    """ List Grupy-Campinas events that will happen in LHC """
    GRUPY_CAMPINAS_MEETUP_ICAL_URL = (
        "https://www.meetup.com/Grupy-Campinas/events/ical/"
    )
    response = requests.get(GRUPY_CAMPINAS_MEETUP_ICAL_URL)
    calendar = Calendar(response.text)

    grupy_events = []
    for event in calendar.events:
        if "Laboratório Hacker de Campinas" in event.location:
            grupy_events.append(event)

    return grupy_events


def lhc_meetup_events():
    LHC_MEETUP_ICAL_URL = "https://www.meetup.com/LabHackerCampinas/events/ical/"
    response = requests.get(LHC_MEETUP_ICAL_URL)
    calendar = Calendar(response.text)
    return calendar.events


def lhc_wiki_events():
    LHC_WIKI_EVENTS_URL = "https://lhc.net.br/wiki/Categoria:Eventos"
    response = requests.get(LHC_WIKI_EVENTS_URL)
    selector = Selector(text=response.text)
    raw_events = selector.xpath(
        "//script[contains(text(), 'window.eventCalendarData.push')]/text()"
    ).re_first(r"window.eventCalendarData.push\((.*)\)")
    events = json.loads(raw_events)

    lhc_events = []
    for event_data in events:
        event = Event(
            name=event_data.get("title"),
            begin=event_data.get("start"),
            end=event_data.get("end"),
            url=urljoin("https://lhc.net.br", event_data.get("url", "")),
            location="Laboratório Hacker de Campinas",
        )
        lhc_events.append(event)
    return lhc_events


def generate_ics(event_sources, future_only=True):
    calendar = Calendar()
    all_events = list(itertools.chain(*event_sources))

    if future_only:
        yesterday = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(days=1)
        all_events = [
            event for event in all_events if event.begin.datetime >= yesterday
        ]

    calendar = Calendar()
    for event in all_events:
        calendar.events.add(event)
    return calendar


def lhc_ics():
    event_sources = [lhc_wiki_events(), lhc_meetup_events(), grupy_campinas_events()]
    calendar = generate_ics(event_sources)
    with open("lhc.ics", "w") as f:
        f.write(str(calendar))


if __name__ == "__main__":
    lhc_ics()
