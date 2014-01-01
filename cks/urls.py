from django.conf.urls import patterns, include, url
from app import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cks.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^calendar/$', views.cal),
    url(r'^month/$', views.month, name='month-url-noargs'),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.month, name='month-url'),
    url(r'^tour/(?P<id>\d+)/$', views.tour, name='tour-url'),
    url(r'^tour/new/$', views.new_tour, name='new-tour-url'),
    url(r'^tour/(?P<id>\d+)/delete/$', views.delete_tour, name='delete-tour-url'),
    url(r'^tour/(?P<id>\d+)/delete/(?P<confirm>\d+)/$', views.delete_tour, name='delete-tour-confirm-url'),
    url(r'^shift/(?P<id>\d+)/$', views.shift, name='shift-url'),
    url(r'^shift/(?P<id>\d+)/delete/$', views.delete_shift, name='delete-shift-url'),
    url(r'^shift/new/$', views.new_shift, name='new-shift-url'),
    url(r'^initialize_month/$', views.initialize_month, name='initialize-month-url-noargs'),
    url(r'^initialize_month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.initialize_month, name='initialize-month-url'),
    url(r'^month/edit/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.edit_month, name='edit-month-url'),
    url(r'^roster/$', views.roster, name='roster-url-noargs'),
    url(r'^roster/(?P<year>\d{4})/(?P<semester>.+)/$', views.roster, name='roster-url'),
    url(r'^person/(?P<id>\d+)/$', views.person, name='person-url'),
    url(r'^person/new/$', views.new_person, name='new-person-url'),
    url(r'^person/(?P<id>\d+)/delete/$', views.delete_person, name='delete-person-url'),
    url(r'^person/(?P<id>\d+)/delete/(?P<confirm>\d+)/$', views.delete_person, name='delete-person-confirm-url'),
)