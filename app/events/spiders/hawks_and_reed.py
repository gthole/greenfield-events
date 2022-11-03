import hashlib
import scrapy
import json
import re
from html import unescape
from markdownify import markdownify as md


class HawksAndReedSpider(scrapy.Spider):
    name = 'hawks-and-reed'

    start_urls = [
        'https://www.hawksandreed.com/events/list/page/1/'
    ]
    allowed_domains = [
        'www.hawksandreed.com'
    ]

    def parse(self, response):
        recipe_links = [
            link for link in
            response.css('a.cdev_event_list_item_permalink')
        ]
        for link in recipe_links:
            yield scrapy.Request(
                link.attrib['href'],
                callback=self.parse_event,
            )

        more = response.css('.pager .nav-next a')
        if more and more.attrib['href']:
            yield scrapy.Request(
                more.attrib['href'],
                callback=self.parse,
            )

    def parse_event(self, response):
        content = md(response.css('.overview').extract_first())
        description = re.sub('\n{3,}', '\n', content).strip()
        lower_description = description.lower()

        raw = response.css('script[type="application/ld+json"]::text').get()
        ldjson = json.loads(raw)[0]

        yield {
            'external_id': hashlib.md5(response.url.encode()).digest(),
            'url': response.url,
            'name': re.sub(
                '( at)? hawks (and|&) reed$', '',
                unescape(ldjson['name']), 0,
                re.IGNORECASE
            ),
            'description': description,
            'location': (ldjson.get('location') or {}).get('name'),
            'start_dttm': ldjson['startDate'],
            'end_dttm': None,
            'canceled': (
                'canceled' in lower_description or
                'cancelled' in lower_description or
                'postponed' in lower_description
            )
        }

