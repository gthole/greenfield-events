import hashlib
import scrapy
import json
import re
from html import unescape
from markdownify import markdownify as md


class TenForwardSpider(scrapy.Spider):
    name = '10-forward'

    start_urls = [
        'https://www.10forwardartsvenue.org/new-events'
    ]
    allowed_domains = [
        'www.10forwardartsvenue.org'
    ]

    def parse(self, response):
        event_sections = [
            link for link in
            response.css('.eventlist-event a.eventlist-title-link')
        ]
        for link in event_sections:
            url = 'https://www.10forwardartsvenue.org%s' % (link.attrib['href'],)
            yield scrapy.Request(url, callback=self.parse_event)

    def parse_event(self, response):
        content = md(response.css('.sqs-block-content').extract_first())
        description = re.sub('\n{3,}', '\n', content).strip()
        lower_description = description.lower()

        raw = response.css('script[type="application/ld+json"]::text').getall()
        all_ld_json = [json.loads(r) for r in raw]
        ldjson = [j for j in all_ld_json if j.get('startDate')][0]

        yield {
            'external_id': hashlib.md5(response.url.encode()).digest(),
            'url': response.url,
            'name': re.sub(
                '( at| -| —)? 10 forward$', '',
                unescape(ldjson['name']).strip(), 0,
                re.IGNORECASE
            ),
            'description': description,
            'location': None,
            'start_dttm': ldjson['startDate'],
            'end_dttm': None,
            'canceled': False,
        }

