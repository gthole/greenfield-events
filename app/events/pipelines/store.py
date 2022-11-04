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
        if not item.get('external_id') or not item.get('start_dttm'):
            raise DropItem

        (ev, created) = Event.objects.get_or_create(
            external_id=item['external_id'],
            source_id=self.source.id
        )

        if created:
            self.create_count += 1
        else:
            self.update_count += 1

        ev.url = item['url']
        ev.name = self.unescape(item['name'])
        ev.description = self.unescape(item['description'])
        ev.location = self.unescape(item['location'] or self.source.default_location)
        ev.all_day = item.get('all_day', False)
        ev.start_dttm = self.parse_dttm(item, 'start_dttm')
        ev.end_dttm = self.parse_dttm(item, 'end_dttm')
        ev.canceled = item['canceled']
        ev.last_crawled_dttm = datetime.now(timezone.utc)
        ev.save()

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
