from django.conf.urls.defaults import *

urlpatterns = patterns('twitinerary.views',
  url(r'^$',             'home'),
  url(r'^tweets/new/$',  'scheduler'),
  url(r'^tweets/send/$', 'tweeter'),
)
