from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from .models import EventSource, Event
from datetime import datetime, timedelta
from base64 import b64decode, b64encode
import pytz

TZ = pytz.timezone(settings.TIME_ZONE)


def get_event_url(obj, start_dttm):
    return '/events/%d-%d-%d/%s/' % (
        start_dttm.year,
        start_dttm.month,
        start_dttm.day,
        b64encode(obj.external_id.encode('utf-8')).decode('utf-8'),
    )


def to_context(obj, start_dttm):
    return {
        'url': get_event_url(obj, start_dttm),
        'name': obj.name,
        'description': obj.description,
        'source': obj.source,
        'start_dttm': start_dttm,
    }

def get_events(*args, start, end, **kwargs):
     # Get all events between start/end or are recurring since the start
    return Event.objects.prefetch_related('source').filter(
        *args,
        Q(start_dttm__gt=start.astimezone(tz=TZ)) | Q(recurrences__isnull=False),
        start_dttm__lte=end.astimezone(tz=TZ),
        **kwargs
    ).order_by('start_dttm')


def get_events_context(*args, now, start, end, **kwargs):
    tz_start = start.astimezone(tz=TZ)
    objs = get_events(*args, start=start, end=end, **kwargs)

    events = []
    for event in objs.all():
        context = to_context(event, event.start_dttm)
        if event.recurrences:
            dates = event.recurrences.between(start, end)
            for date in dates:
                start_dttm = date.replace(
                    hour=event.start_dttm.astimezone(tz=TZ).hour,
                    minute=event.start_dttm.minute,
                ).astimezone(tz=TZ)
                events.append(to_context(event, start_dttm))
        else:
            events.append(context)

    events.sort(key=lambda e: e['start_dttm'])
    return events


def get_days_context(*args, now, start, end, **kwargs):
    tz_start = start.astimezone(tz=TZ)
    events = get_events_context(*args, now=now, start=start, end=end, **kwargs)

    days = {}
    tznow = now.astimezone(tz=TZ)
    for index in range(0, (end - start).days):
        d = tz_start + timedelta(days=index)
        key = d.strftime('%d/%b/%Y')
        entry = {
            'date': d,
            'is_past': d < tznow,
            'is_today': d == tznow,
            'is_tomorrow': d == tznow + timedelta(days=1),
            'is_weekend': d.weekday() == 5 or d.weekday() == 6,
            'events': [],
        }
        days[key] = entry

    for event in events:
        k = event['start_dttm'].astimezone(TZ).strftime('%d/%b/%Y')
        if not days.get(k):
            continue
        days[k]['events'].append(event)

    return days


def home(request):
    start = datetime.now()
    end = start + timedelta(days=7)

    days = get_days_context(now=start, start=start, end=end)
    days = dict((key, day) for key, day in days.items() if day['events'])

    return render(request, 'views/home.html', {
        'view': 'home',
        'header': "What's Happening in Greenfield This Week?",
        'days': days,
        'search': ''
    })


def search(request):
    query = request.GET.get('search')
    if not query:
        return home(request)

    start = datetime.now()
    end = start + timedelta(days=28)
    search_args = [
        Q(name__icontains=query) | \
        Q(source__name__icontains=query) | \
        Q(source__extra_search_terms__icontains=query)
    ]

    days = get_days_context(*search_args, now=start, start=start, end=end)
    days = dict((key, day) for key, day in days.items() if day['events'])

    return render(request, 'views/search.html', {
        'view': 'home',
        'days': days,
        'search': query,
    })


def calendar(request):
    days_out = 28
    now = datetime.now()
    start = now - timedelta(days=now.weekday())
    end = start + timedelta(days=days_out)

    days = get_days_context(now=now, start=start, end=end)

    return render(request, 'views/calendar.html', {
        'view': 'calendar',
        'header': 'Greenfield Events Calendar',
        'days': days,
        'search': ''
    })


def event_link(request, date, b64_external_id):
    """
    Use internal permalinks that we route to the event URL so that we can have
    unique links for recurring events that have the same event URL
    """
    external_id = b64decode(b64_external_id).decode('utf-8')
    event = get_object_or_404(Event, external_id=external_id)
    return HttpResponseRedirect(event.url)
