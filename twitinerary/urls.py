from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',                     'tweets.home'),
  url(r'^tweets/new/$',          'tweets.new'),
  url(r'^tweets/save/$',         'tweets.save'),
  url(r'^tweets/delete/$',       'tweets.delete'),
  url(r'^tweets/edit/$',         'tweets.edit'),
  url(r'^tweets/$',              'tweets.view'),
  url(r'^cron/batch_delete/$',   'cron.batch_delete'),
  url(r'^cron/batch_send/$',     'cron.batch_send'),
  url(r'^user/authenticate/$',   'oauth.authenticate'),
  url(r'^user/logout/$',         'oauth.sign_out'),
  url(r'^upload_image/$',        'image_uploader.upload_image'),
)
