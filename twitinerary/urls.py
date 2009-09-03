from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',             'home'),
  url(r'^tweets/new/$',  'schedule'),
  url(r'^tweets/send/$', 'mass_tweet'),
  url(r'^tweets/$',      'review'),
  url(r'^logout/$',      'logout'),
)
