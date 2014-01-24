from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'comp_poster.views.overlay', name="comp_poster-overlay"),
)