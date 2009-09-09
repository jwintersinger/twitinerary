from datetime import date, datetime, timedelta
from django.views.generic.simple import direct_to_template
from twitinerary.models import ScheduledTweet, Twitterer, AuthenticatedUser
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from google.appengine.ext.db import BadKeyError
from lib import oauth as oa

def home(request):
  tweets = ScheduledTweet.all()
  tweets.order('-post_at')

  today = date.today()
  days = [today + timedelta(days=n) for n in range(4)]

  return direct_to_template(request, 'index.html', {'tweets': tweets, 'days': days})

def _too_many_tweets_sent(user):
  tweets = ScheduledTweet.all()
  tweets.filter('username =', user.username)
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
  tweets.filter('username =', request.user.username)
  tweets.filter('tweeted =', False)
  tweets.order('-post_at')
  return direct_to_template(request, 'view.html', {'tweets': tweets})

def delete(request):
  try:
    tweet = ScheduledTweet.get(request.POST.get('key'))
  except BadKeyError:
    tweet = None
  if request.method == 'POST' and tweet and tweet.username == request.user.username:
    tweet.delete()
  return HttpResponseRedirect(reverse(view))

def oauth(request):
  consumer_key = 'xDxIgRQFQegu5TWLv1IQ'
  consumer_secret = 'jyKqZ1Hr5SlAiYDQBsDwuXdZPUp1UApA9HBEtvhpL1c'
  client = oa.TwitterClient(consumer_key, consumer_secret, request.build_absolute_uri())

  if ('oauth_token' in request.GET) and ('oauth_verifier' in request.GET):
    request_token = request.GET.get('oauth_token')
    verifier = request.GET.get('oauth_verifier')
    user_info = client.fetch('http://twitter.com/account/verify_credentials.json', request_token, verifier)
    username = user_info['screen_name']

    user = AuthenticatedUser.get_or_insert(key_name = username, username = username)
    request.session['user_key'] = user.key()
    return HttpResponseRedirect(reverse(home))
  else:
    return HttpResponseRedirect(client.get_authorization_url())
