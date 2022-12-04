import hashlib
from django.db.models import Count
from scrapy.exceptions import DropItem
from events.models import Event, EventSource
from dateutil import parser
from datetime import datetime, timedelta, timezone
from html import unescape
import logging


class EventStorePipeline(object):
    def open_spider(self, spider):
        self.source = EventSource.objects.get(spider=spider.name)
        self.start = datetime.now(timezone.utc)
        self.create_count = 0
        self.update_count = 0

        logging.info({
            'action': 'crawl_started',
            'source': spider.name,
            'start': self.start.isoformat(),
        })

    def process_item(self, item, spider):
        if not item.get('url') or not item.get('name') or not item.get('start_dttm'):
            raise DropItem

        external_id = hashlib.md5(item['url'].encode()).digest(),

        (ev, created) = Event.objects.update_or_create(
            external_id=external_id,
            source_id=self.source.id,
            defaults={
                'url': item['url'],
                'name': self.unescape(item['name']),
                'description': self.unescape(item['description']),
                'location': self.unescape(item['location'] or self.source.default_location),
                'all_day': item.get('all_day', False),
                'start_dttm': self.parse_dttm(item, 'start_dttm'),
                'end_dttm': self.parse_dttm(item, 'end_dttm'),
                'canceled': item['canceled'],
                'last_crawled_dttm': datetime.now(timezone.utc),
            }
        )

        if created:
            self.create_count += 1
        else:
            self.update_count += 1

        return item

    def unescape(self, val):
        if val:
            return unescape(val)
        return None

    def parse_dttm(self, item, attr):
        if item.get(attr):
            return parser.parse(item[attr])
        return None

    def close_spider(self, spider):
        """
        Remove any events that are for the future but weren't picked up by this
        past crawl, and print some stats
        """

        # Note the actual delete here
        (deleted, _) = Event.objects.filter(
            source_id=self.source.id,
            start_dttm__gt=self.start,
            last_crawled_dttm__isnull=False,
            last_crawled_dttm__lt=self.start,
        ).delete()

        logging.info({
            'action': 'crawl_complete',
            'source': spider.name,
            'created': self.create_count,
            'updated': self.update_count,
            'deleted': deleted,
        })
