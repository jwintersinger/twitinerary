from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',                     'tweets.home'),
  url(r'^tweets/new/$',          'tweets.new'),
  url(r'^tweets/delete/$',       'tweets.delete'),
  url(r'^tweets/$',              'tweets.view'),
  url(r'^oauth/$',               'tweets.oauth_test'),
  url(r'^tweets/batch_send/$',   'cron.batch_tweet'),
  url(r'^tweets/batch_delete/$', 'cron.batch_delete'),
  url(r'^logout/$',              'user.logout'),
)
