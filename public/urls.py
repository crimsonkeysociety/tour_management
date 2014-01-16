from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^$', 'public.views.home', name='home'),
	url(r'^month/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'public.views.month', name='month'),
	url(r'^month/$', 'public.views.month', name='month-noargs'),
	url(r'^profile/(?P<year>\d{4})/(?P<semester>.+)/$', 'public.views.profile', name='profile'),
	url(r'^profile/$', 'public.views.profile', name='profile-current'),
	url(r'^claim/(?P<id>\d+)/$', 'public.views.claim', name='claim'),
	url(r'^claim/(?P<id>\d+)/confirm/(?P<confirm>\w+)/$', 'public.views.claim', name='claim-confirm'),
	url(r'^unclaim/(?P<id>\d+)/$', 'public.views.unclaim', name='unclaim'),
	url(r'^unclaim/(?P<id>\d+)/confirm/(?P<confirm>\w+)/$', 'public.views.unclaim', name='unclaim-confirm'),
	url(r'^help/$', 'public.views.help', name='help'),
	)