from base64 import b64encode
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse
from datetime import datetime, timedelta
from django_ical.utils import build_rrule_from_recurrences_rrule
from django_ical.views import ICalFeed
from events.views import get_events, get_events_context, get_event_url
import pytz

TZ = pytz.timezone(settings.TIME_ZONE)


class EventsFeed(Feed):
    title = 'Greenfield Events Feed'
    link = '/feed/'
    description = 'Upcoming events in Greenfield MA.'

    def items(self):
        start = datetime.now()
        end = start + timedelta(days=28)
        return get_events_context(now=start, start=start, end=end)

    def item_title(self, item):
        return item['name']

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        return item['url']


class ICALEventsFeed(ICalFeed):
    product_id = '-//%s//Upcoming Events//EN' % (settings.ALLOWED_HOSTS[0],)
    timezone = settings.TIME_ZONE
    file_name = "upcoming-events.ics"

    def items(self):
        start = datetime.now()
        end = start + timedelta(days=90)
        return get_events(start=start, end=end)

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_location(self, item):
        return item.location

    def item_start_datetime(self, item):
        return item.start_dttm.astimezone(tz=TZ)

    def item_end_datetime(self, item):
        if item.end_dttm:
            return item.end_dttm.astimezone(tz=TZ)

        # In general evening events have a long duration
        if item.start_dttm.astimezone(tz=TZ).hour >= 14:
            return item.start_dttm.astimezone(tz=TZ) + timedelta(hours=4)

        return None

    def item_link(self, item):
        return get_event_url(item, item.start_dttm)

    def item_rrule(self, item):
        """Adapt Event recurrence to Feed Entry rrule."""
        if item.recurrences:
            rules = []
            for rule in item.recurrences.rrules:
                rules.append(build_rrule_from_recurrences_rrule(rule))
            return rules

    def item_exrule(self, item):
        """Adapt Event recurrence to Feed Entry exrule."""
        if item.recurrences:
            rules = []
            for rule in item.recurrences.exrules:
                rules.append(build_rrule_from_recurrences_rrule(rule))
            return rules

    def item_rdate(self, item):
        """Adapt Event recurrence to Feed Entry rdate."""
        if item.recurrences:
            return item.recurrences.rdates

    def item_exdate(self, item):
        """Adapt Event recurrence to Feed Entry exdate."""
        if item.recurrences:
            return item.recurrences.exdates