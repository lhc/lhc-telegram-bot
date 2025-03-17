import unittest
import os
from datetime import datetime, timedelta

from unittest.mock import patch, Mock
from parameterized import parameterized

from ics import Event

os.environ["LHC_CHAT_ID"] = "1"
os.environ["TELEGRAM_API_TOKEN"] = "abcdef"
os.environ["MONTASTIC_RSS_URL"] = "https://lhc.net.br/rss"
os.environ["FINANCE_STATUS_URL"] = "https://lhc.net.br/finance"
os.environ["ICS_LOCATION"] = "https://gancio-eventos-lhc.fly.dev/api/events"

import joker.commands.calendar as cal

gancio_events_json_response = [{
    "id": 164,
    "title": "Oficina de IoT: Quinta Temporada - Março",
    "slug": "oficina-de-iot-quinta-temporada-marco",
    "start_datetime": 1741818600,
    "end_datetime": 1741824000,
    "media": [
      {
        "url": "536a0f4aa63815e48e991c8ddd321a19.jpg",
        "height": 675,
        "width": 1200,
        "name": "Oficina de IoT: Quinta Temporada - Março",
        "size": 90844,
        "focalpoint": [
          0,
          0
        ]
      }
    ],
    "online_locations": [
      "https://pretix.lhc.net.br/IoT/iotx02/"
    ],
    "updatedAt": "2025-02-25T15:15:45.216Z",
    "apUserApId": None,
    "tags": [
      "Oficina de IoT",
      "comunidade",
      "hardware",
      "iot",
      "oficinadeiot",
      "plaquinhas"
    ],
    "place": {
      "id": 1,
      "name": "Laboratório Hacker de Campinas",
      "address": "Rua Araribóia, 121 Ponte Preta, Campinas - SP 13041-350",
      "latitude": -22.9178033,
      "longitude": -47.0524533
    },
    "ap_user": None
}]

class CalendarTest(unittest.TestCase):

    @parameterized.expand([
        ("today"),
        ("future")
    ])
    @patch('httpx.get')
    @patch('ics.Calendar')
    @patch('datetime.datetime')
    def test_today_2events_one_in_the_past_other_in_the_future(self, when, mock_datetime, mock_Calendar, mock_http_get):
        # GIVEN
        now = datetime(2025, 2, 25, 8, 0, 0)
        print(f'Base date/time is {now}')
        four_hours_earlier = now - timedelta(hours=4)
        four_hours_ahead = now + timedelta(hours=4)
        event1 = Event("Oficina IoT", begin=four_hours_earlier, end=(four_hours_earlier + timedelta(hours=2)))
        event2 = Event("CofeeOps", begin=four_hours_ahead, end=(four_hours_ahead + timedelta(hours=2)))
        # GIVEN mocks
        mock_response = Mock()
        mock_response.text = gancio_events_json_response
        mock_http_get.return_value = mock_response

        mock_calendar = Mock()
        mock_calendar.events = [ event1, event2 ]
        mock_Calendar.return_value = mock_calendar

        mock_datetime.now.return_value = now
        # WHEN
        events = cal.get_events(when)
        print(events)
        # THEN
        self.assertEqual(len(events), 1, msg="It should contain the event that starts in the future")
        self.assertEqual(events[0].name, "CofeeOps", msg="It should be the event name that starts in the future")

    @parameterized.expand([
        ("today"),
        ("future")
    ])
    @patch('httpx.get')
    @patch('ics.Calendar')
    @patch('datetime.datetime')
    def test_today_2events_one_in_the_past_other_now(self, when, mock_datetime, mock_Calendar, mock_http_get):
        # GIVEN
        now = datetime(2025, 2, 25, 8, 0, 0)
        print(f'Base date/time is {now}')
        four_hours_earlier = now - timedelta(hours=4)
        event1 = Event("Oficina IoT", begin=four_hours_earlier, end=(four_hours_earlier + timedelta(hours=2)))
        event2 = Event("CofeeOps", begin=now, end=(now + timedelta(hours=2)))
        # GIVEN mocks
        mock_response = Mock()
        mock_response.text = gancio_events_json_response
        mock_http_get.return_value = mock_response

        mock_calendar = Mock()
        mock_calendar.events = [ event1, event2 ]
        mock_Calendar.return_value = mock_calendar

        mock_datetime.now.return_value = now
        # WHEN
        events = cal.get_events(when)
        print(events)
        # THEN
        self.assertEqual(len(events), 1, msg="It should contain the event that starts from now")
        self.assertEqual(events[0].name, "CofeeOps", msg="It should be the event name that starts from now")

    @parameterized.expand([
        ("today"),
        ("future")
    ])
    @patch('httpx.get')
    @patch('ics.Calendar')
    @patch('datetime.datetime')
    def test_today_2events_in_the_future(self, when, mock_datetime, mock_Calendar, mock_http_get):
        # GIVEN
        now = datetime(2025, 2, 25, 8, 0, 0)
        print(f'Base date/time is {now}')
        four_hours_ahead = now + timedelta(hours=4)
        ten_hours_ahead = now + timedelta(hours=10)
        event1 = Event("Oficina IoT", begin=four_hours_ahead, end=(four_hours_ahead + timedelta(hours=2)))
        event2 = Event("CofeeOps", begin=ten_hours_ahead, end=(ten_hours_ahead + timedelta(hours=2)))
        # GIVEN mocks
        mock_response = Mock()
        mock_response.text = gancio_events_json_response
        mock_http_get.return_value = mock_response

        mock_calendar = Mock()
        mock_calendar.events = [ event1, event2 ]
        mock_Calendar.return_value = mock_calendar

        mock_datetime.now.return_value = now
        # WHEN
        events = cal.get_events(when)
        print(events)
        # THEN
        self.assertEqual(len(events), 2, msg="It should contain the two future events")
        self.assertEqual(min(events, key=lambda e: e.begin).name, "Oficina IoT", msg="First event should be the earliest date")


if __name__ == '__main__':
    unittest.main()