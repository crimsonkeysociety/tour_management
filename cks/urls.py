from django.conf.urls import patterns, include, url
from django.contrib import admin
from public import urls as public_urls
from comp_poster import urls as comp_poster_urls

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name='home-url'),
    url(r'^settings/$', 'app.views.settings_page', name='settings-url'),
    url(r'^month/$', 'app.views.month', name='month-url-noargs'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'app.views.month', name='month-url'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/edit/$', 'app.views.edit_month', name='edit-month-url'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/edit-initialization/$', 'app.views.edit_month_initialization', name='edit-month-initialization-url'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/uninitialize/$', 'app.views.uninitialize_month', name='uninitialize-month-url'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/uninitialize/(?P<confirm>\w+)/$', 'app.views.uninitialize_month', name='uninitialize-month-confirm-url'),
    url(r'^tour/(?P<id>\d+)/$', 'app.views.tour', name='tour-url'),
    url(r'^tour/new/$', 'app.views.new_tour', name='new-tour-url'),
    url(r'^tour/(?P<id>\d+)/delete/$', 'app.views.delete_tour', name='delete-tour-url'),
    url(r'^tour/(?P<id>\d+)/delete/(?P<confirm>\w+)/$', 'app.views.delete_tour', name='delete-tour-confirm-url'),
    url(r'^shift/(?P<id>\d+)/$', 'app.views.shift', name='shift-url'),
    url(r'^shift/(?P<id>\d+)/delete/$', 'app.views.delete_shift', name='delete-shift-url'),
    url(r'^shift/new/$', 'app.views.new_shift', name='new-shift-url'),
    url(r'^initialize_month/$', 'app.views.initialize_month', name='initialize-month-url-noargs'),
    url(r'^initialize_month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'app.views.initialize_month', name='initialize-month-url'),
    url(r'^roster/$', 'app.views.roster', name='roster-url-noargs'),
    url(r'^roster/(?P<year>\d{4})/(?P<semester>.+)/$', 'app.views.roster', name='roster-url'),
    url(r'^person/(?P<id>\d+)/$', 'app.views.person', name='person-url'),
    url(r'^person/new/$', 'app.views.new_person', name='new-person-url'),
    url(r'^person/(?P<id>\d+)/delete/$', 'app.views.delete_person', name='delete-person-url'),
    url(r'^person/(?P<id>\d+)/delete/(?P<confirm>\w+)/$', 'app.views.delete_person', name='delete-person-confirm-url'),
    url(r'^inactive-semester/delete/(?P<id>\d+)/$', 'app.views.delete_inactive_semester', name='delete-inactive-semester-url'),
    url(r'^default-tour/edit/(?P<id>\d+)/$', 'app.views.default_tour', name='edit-default-tour-url'),
    url(r'^default-tour/delete/(?P<id>\d+)/$', 'app.views.delete_default_tour', name='delete-default-tour-url'),
    url(r'^default-tour/new/$', 'app.views.new_default_tour', name='new-default-tour-url'),
    url(r'^login/$', 'app.views.login'),
    url(r'^logout/$', 'app.views.logout', name='logout-url'),
    url(r'^unsupported-browser/$', 'app.views.unsupported_browser', name='unsupported-browser-url'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^open-month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'app.views.open_month', name='open-month-url'),
    url(r'^close-month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'app.views.close_month', name='close-month-url'),
    url(r'^public/', include(public_urls, namespace='public')),
    url(r'^comp/poster/', include(comp_poster_urls))
)

admin.autodiscover()

urlpatterns += (url(r'^admin/', include(admin.site.urls)),)