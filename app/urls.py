from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from events.feeds import EventsFeed, ICALEventsFeed
from events.views import home, search, calendar, event_link

urlpatterns = [
    url(r'^accounts/password_reset/$', auth_views.PasswordResetView.as_view(
        email_template_name='email/password_reset.txt',
        html_email_template_name='email/password_reset.html',
        subject_template_name='email/password_reset_subject.txt',
    ), name='auth_password_reset'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^favicon.ico$', RedirectView.as_view(
        url=settings.STATIC_URL + 'img/favicon-32.png',
        permanent=True
    )),
    url('robots.txt', TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    )),
    url(r'^events/(?P<date>[\d\-]+)/(?P<b64_external_id>[\w=]+)', event_link),
    url(r'^feed.ics', ICALEventsFeed()),
    url(r'^feed.rss', EventsFeed()),
    url(r'^search', search),
    url(r'^calendar', calendar),
    url(r'^$', home),
]
