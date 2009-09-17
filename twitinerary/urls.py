from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',                     'tweets.home'),
  url(r'^tweets/new/$',          'tweets.schedule_tweet'),
  url(r'^tweets/create/$',       'tweets.create'),
  url(r'^tweets/delete/$',       'tweets.delete'),
  url(r'^tweets/$',              'tweets.view'),
  url(r'^cron/batch_send/$',     'cron.batch_tweet'),
  url(r'^cron/batch_delete/$',   'cron.batch_delete'),
  url(r'^user/authenticate/$',   'oauth.authenticate'),
  url(r'^user/logout/$',         'oauth.sign_out'),
  url(r'^upload_image/$',        'image_uploader.upload_image'),
)
