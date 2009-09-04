from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',                     'home'),
  url(r'^tweets/new/$',          'schedule'),
  url(r'^tweets/batch_send/$',   'batch_tweet'),
  url(r'^tweets/batch_delete/$', 'batch_delete'),
  url(r'^tweets/delete/$',       'delete'),
  url(r'^tweets/$',              'review'),
  url(r'^logout/$',              'logout'),
)
