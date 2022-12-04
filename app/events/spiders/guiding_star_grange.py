import scrapy
import datetime
import os
import re
from markdownify import markdownify as md
from googleapiclient.discovery import build


class GuidingStarGrangeSpider(scrapy.Spider):
    """
    https://guidingstargrange.org/events.html
    """

    name = 'guiding-star-grange'

    start_urls = [
        'https://example.com/'
    ]
    allowed_domains = [
        'example.com'
    ]
    calendar_ids = [
        '6agg3rtppgj82p854na6qmcsls',
        'llfb18hnki77ac2udmhnk0q0g0',
        'o9i7kao90s96in4sm4trtf2p9c',
        'nud1hf5mfloegr0565muiumsd8',
        'ch2r1iv9fqjfapg26tp8ia56qo',
        'eebg2r45fcj1ujhir9o0hi1fks',
        'sm782g97b6me0g2oualn4dp1vk',
        'tpnri3iul94a6e1082om29cogo',
        '69hvhbml5qee2s949n2abce7vo',
        'oti261eau3175gebpfh028sk5k',
        'fn07tvma25qsm628a0q0jm3vb4',
        'au4j5pvg5cg7jrdt6h9q81h4sk',
    ]

    def parse(self, response):
        key = os.environ.get('GOOGLE_API_KEY')
        service = build('calendar', 'v3', developerKey=key)

        for calendar_id in self.calendar_ids:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = service.events().list(
                calendarId='%s@group.calendar.google.com' % (calendar_id,),
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return

            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                yield {
                    'url': event.get('htmlLink'),
                    'name': event['summary'],
                    'description': md(re.sub('html-blob', 'div', event.get('description', '')), strip=['a', 'img']),
                    'location': event.get('location'),
                    'start_dttm': start,
                    'end_dttm': end,
                    'canceled': (event['status'] != 'confirmed') or event.get('canceled', False),
                }
