from django.shortcuts import render
from django.db.models import Q
from .models import EventSource, Event, RecurringEvent
from datetime import datetime, timedelta
import pytz


def to_context(obj, start_dttm):
    return {
        'url': obj.url,
        'name': obj.name,
        'source': obj.source,
        'start_dttm': start_dttm,
    }


def get_events_context(*args, now, start, end, **kwargs):
    tz = pytz.timezone('America/New_York')
    tz_start = start.replace(tzinfo=tz)

    objs = Event.objects.prefetch_related('source').filter(
        *args,
        start_dttm__gt=start.replace(tzinfo=tz),
        start_dttm__lte=end.replace(tzinfo=tz),
        **kwargs
    ).order_by('start_dttm')

    events = [to_context(ev, ev.start_dttm) for ev in objs]

    robjs = RecurringEvent.objects.prefetch_related('source').filter(*args, **kwargs)
    for rec in robjs:
        dates = rec.recurrences.between(start, end)
        for date in dates:
            start_dttm = date.replace(
                hour=rec.start.hour,
                minute=rec.start.minute,
                tzinfo=tz
            )
            events.append(to_context(rec, start_dttm))

    events.sort(key=lambda e: e['start_dttm'])

    days = {}
    tznow = now.replace(tzinfo=tz)
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
        k = event['start_dttm'].astimezone(tz).strftime('%d/%b/%Y')
        days[k]['events'].append(event)

    return days


def home(request):
    start = datetime.now()
    end = start + timedelta(days=7)

    days = get_events_context(now=start, start=start, end=end)
    days = dict((key, day) for key, day in days.items() if day['events'])

    return render(request, 'views/home.html', {
        'view': 'home',
        'header': "What's Happening in Greenfield This Week?",
        'days': days,
        'search': ''
    })


def search(request):
    query = request.GET.get('search')
    if query is None:
        return home(request)

    start = datetime.now()
    end = start + timedelta(days=7)
    search_args = [
        Q(name__icontains=query) | \
        Q(source__name__icontains=query)
    ]

    days = get_events_context(*search_args, now=start, start=start, end=end)
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

    days = get_events_context(now=now, start=start, end=end)

    return render(request, 'views/calendar.html', {
        'view': 'calendar',
        'header': 'Greenfield Events Calendar',
        'days': days,
        'search': ''
    })
