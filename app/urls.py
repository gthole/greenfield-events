from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from events.views import home, search, calendar


# TODO: Serve media images with another method
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    url(r'^accounts/password_reset/$', auth_views.PasswordResetView.as_view(
        email_template_name='email/password_reset.txt',
        html_email_template_name='email/password_reset.html',
        subject_template_name='email/password_reset_subject.txt',
    ), name='auth_password_reset'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^favicon.ico$', RedirectView.as_view(
        url=settings.STATIC_URL + 'assets/favicon.ico',
        permanent=True
    )),
    url(r'^search', search),
    url(r'^calendar', calendar),
    url(r'', home),
]
