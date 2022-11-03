from django.contrib.auth.models import User
from django.db.models import Model, TextField, DateTimeField, Index, CharField, \
    URLField, BooleanField, TimeField, ForeignKey, CASCADE
from recurrence.fields import RecurrenceField


class EventSource(Model):
    """
    Link between events and web crawlers/users
    """
    name = CharField(max_length=255)
    spider = CharField(max_length=255, blank=True, null=True)
    default_location = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s (%d)' % (self.name, self.id)


class BaseEvent(Model):
    class Meta:
        abstract = True

    external_id = CharField(max_length=255)
    url = URLField(max_length=500)

    name = CharField(max_length=255)
    description = TextField(null=True)
    location = CharField(max_length=255)
    all_day = BooleanField(default=False)

    created_dttm = DateTimeField(auto_now_add=True, blank=True)
    updated_dttm = DateTimeField(auto_now=True, blank=True)
    last_crawled_dttm = DateTimeField(null=True, blank=True)


class Event(BaseEvent):
    class Meta:
        indexes = [
            Index(fields=['-start_dttm']),
            Index(fields=['source']),
        ]

    source = ForeignKey(EventSource, related_name='events', on_delete=CASCADE)
    start_dttm = DateTimeField(blank=True, null=True)
    end_dttm = DateTimeField(blank=True, null=True)
    canceled = BooleanField(default=False)


class RecurringEvent(BaseEvent):
    source = ForeignKey(EventSource, related_name='recurring_events', on_delete=CASCADE)
    start = TimeField()
    end = TimeField()
    recurrences = RecurrenceField()
