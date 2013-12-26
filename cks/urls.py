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
    (r'^month/$', views.month),
    (r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.month),
)
