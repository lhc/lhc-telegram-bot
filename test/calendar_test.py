import unittest
import os
from datetime import datetime, timedelta

from unittest.mock import patch, Mock

from ics import Event

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

    def setUp(self):
        os.environ["LHC_CHAT_ID"] = "1"
        os.environ["TELEGRAM_API_TOKEN"] = "abcdef"
        os.environ["MONTASTIC_RSS_URL"] = "https://lhc.net.br/rss"
        os.environ["FINANCE_STATUS_URL"] = "https://lhc.net.br/finance"
        os.environ["ICS_LOCATION"] = "https://gancio-eventos-lhc.fly.dev/api/events"

    @patch('httpx.get')
    @patch('ics.Calendar')
    def test_today_2events_one_in_the_past_other_in_the_future(self, mock_Calendar, mock_get):
        # GIVEN
        mock_response = Mock()
        mock_response.text = gancio_events_json_response  # Example ICS content
        mock_get.return_value = mock_response

        now = datetime.now()
        print(f'Today is {now}')
        two_hours_ago = now - timedelta(hours=2)
        three_hours_ahead = now + timedelta(hours=3)
        after_two_hours = three_hours_ahead + timedelta(hours=2)

        event1 = Event("Oficina IoT", begin=two_hours_ago, end=now)
        event2 = Event("CofeeOps", begin=three_hours_ahead, end=after_two_hours)

        mock_calendar = Mock()
        mock_calendar.events = [ event1, event2 ]
        mock_Calendar.return_value = mock_calendar
        # WHEN
        events = cal.get_events("today")
        print(events)
        # THEN the test may run at a time when the event2 still in the future
        if event2.begin.date() == datetime.today():
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].name, "CofeeOps")
        else:
            self.assertEqual(len(events), 0)

    @patch('httpx.get')
    @patch('ics.Calendar')
    def test_today_2events_one_in_the_past_other_now(self, mock_Calendar, mock_get):
        # GIVEN
        mock_response = Mock()
        mock_response.text = gancio_events_json_response  # Example ICS content
        mock_get.return_value = mock_response

        now = datetime.now()
        print(f'Today is {now}')
        two_hours_ago = now - timedelta(hours=2)
        after_two_hours = now + timedelta(hours=2)

        event1 = Event("Oficina IoT", begin=two_hours_ago, end=now)
        event2 = Event("CofeeOps", begin=(now+timedelta(seconds=1)), end=after_two_hours)

        mock_calendar = Mock()
        mock_calendar.events = [ event1, event2 ]
        mock_Calendar.return_value = mock_calendar
        # WHEN
        events = cal.get_events("today")
        print(events)
        # THEN
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "CofeeOps")


if __name__ == '__main__':
    unittest.main()