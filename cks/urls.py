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
    url(r'^initialize_month/$', views.initialize_month, name='initialize-month-url-noargs'),
    url(r'^initialize_month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.initialize_month, name='initialize-month-url'),
    url(r'^edit-month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.edit_month, name='edit-month-url'),
    url(r'^roster/$', views.roster, name='roster-url-noargs'),
    url(r'^roster/(?P<year>\d{4})/(?P<semester>.+)/$', views.roster, name='roster-url'),
)