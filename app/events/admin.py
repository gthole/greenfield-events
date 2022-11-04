from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group

from .models import Event, EventSource


@admin.register(EventSource)
class EventSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_dttm', 'source')
    search_fields = ('name', 'description')
    ordering = ('-start_dttm',)
    list_filter = ('source', 'recurrences')
    exclude = ('end_dttm', 'external_id', 'last_crawled_dttm', 'all_day')

admin.site.site_header = 'Greenfield Events Admin'
