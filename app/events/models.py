from hashlib import md5
from django.contrib.auth.models import User
from django.db.models import Model, TextField, DateTimeField, Index, CharField, \
    URLField, BooleanField, TimeField, ForeignKey, CASCADE
from recurrence.fields import RecurrenceField


class EventSource(Model):
    """
    Link between events and web crawlers/users
    """
    name = CharField(max_length=255)
    extra_search_terms = CharField(max_length=255, blank=True, null=True)
    spider = CharField(max_length=255, blank=True, null=True)
    default_location = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s (%d)' % (self.name, self.id)


class Event(Model):
    class Meta:
        indexes = [
            Index(fields=['-start_dttm']),
            Index(fields=['source']),
        ]

    external_id = CharField(max_length=255, unique=True)
    url = URLField(max_length=500)

    name = CharField(max_length=255)
    description = TextField(null=True)
    location = CharField(max_length=255)
    all_day = BooleanField(default=False)

    source = ForeignKey(EventSource, related_name='events', on_delete=CASCADE)
    start_dttm = DateTimeField()
    end_dttm = DateTimeField(blank=True, null=True)
    canceled = BooleanField(default=False)

    created_dttm = DateTimeField(auto_now_add=True, blank=True)
    updated_dttm = DateTimeField(auto_now=True, blank=True)
    last_crawled_dttm = DateTimeField(null=True, blank=True)

    recurrences = RecurrenceField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Ensure we take the hashlib of the url and name for the external ID when
        saving through the admin portal
        """
        if not self.external_id:
            self.external_id = md5(self.url.encode()).digest()
        return super().save(*args, **kwargs)
