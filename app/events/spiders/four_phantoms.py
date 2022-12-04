import scrapy
import json
import re
from html import unescape
from markdownify import markdownify as md


class FourPhantomsSpider(scrapy.Spider):
    name = 'four-phantoms'

    start_urls = [
        'https://www.fourphantoms.net/events/'
    ]
    allowed_domains = [
        'www.fourphantoms.net'
    ]

    def parse(self, response):
        recipe_links = [
            link for link in
            response.css('a.eventlist-title-link')
        ]
        for link in recipe_links:
            yield scrapy.Request(
                'https://www.fourphantoms.net%s' % (link.attrib['href'], ),
                callback=self.parse_event,
            )

    def parse_event(self, response):
        description = md(response.css('.sqs-block-content').extract_first(), strip=['a', 'img'])
        lower_description = description.lower()
        if 'private event' in lower_description:
            return

        blobs = [
            json.loads(el.get()) for el in
            response.css('script[type="application/ld+json"]::text')
        ]
        event_blobs = [blob for blob in blobs if blob.get('@type') == 'Event']
        if not event_blobs:
            return
        ldjson = event_blobs[0]

        yield {
            'url': response.url,
            'name': ldjson['name'],
            'description': description,
            'location': (ldjson.get('location') or {}).get('address'),
            'start_dttm': ldjson['startDate'],
            'end_dttm': ldjson.get('endDate'),
            'canceled': (
                'canceled' in lower_description or
                'cancelled' in lower_description or
                'postponed' in lower_description
            )
        }

