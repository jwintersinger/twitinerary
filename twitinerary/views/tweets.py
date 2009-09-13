from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from google.appengine.ext.db import BadKeyError
from twitinerary.models import ScheduledTweet, Twitterer

def home(request):
  tweets = ScheduledTweet.all()
  tweets.order('-post_at')

  today = date.today()
  days = [today + timedelta(days=n) for n in range(4)]

  return direct_to_template(request, 'index.html', {'tweets': tweets, 'days': days})

def _too_many_tweets_sent(user):
  tweets = ScheduledTweet.all()
  tweets.filter('user =', user)
  return tweets.count() >= 5

def new(request):
  user = request.user
  if not user.is_authenticated():
    return HttpResponse('Not authenticated.', status=401, content_type='text/plain')
  if _too_many_tweets_sent(user):
    return HttpResponse('Too many Tweets sent.', status=403, content_type='text/plain')

  tweet = ScheduledTweet(user       = user,
                         tweet      = request.POST.get('tweet'),
                         post_at    = datetime.utcfromtimestamp( float(request.POST.get('post_at', 0)) ),
                         ip_address = request.META.get('REMOTE_ADDR') )
  tweet.put()
  return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')

def view(request):
  if not request.user.is_authenticated():
    return HttpResponse('Not authenticated.', status=401, content_type='text/plain')
  tweets = ScheduledTweet.all()
  # TODO: require login.
  tweets.filter('user =', request.user)
  tweets.filter('tweeted =', False)
  tweets.order('-post_at')
  return direct_to_template(request, 'view.html', {'tweets': tweets})

def delete(request):
  try:
    tweet = ScheduledTweet.get(request.POST.get('key'))
  except BadKeyError:
    tweet = None
  if request.method == 'POST' and tweet and tweet.user == request.user:
    tweet.delete()
  return HttpResponseRedirect(reverse(view))

