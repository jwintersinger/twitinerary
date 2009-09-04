# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from models import ScheduledTweet, Twitterer, AuthenticatedUser
from datetime import date, datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
  tweets = ScheduledTweet.all()
  tweets.order('-post_at')

  today = date.today()
  days = [today + timedelta(days=n) for n in range(4)]

  return direct_to_template(request, 'index.html', {'tweets': tweets, 'days': days})

def too_many_tweets_sent(user):
  tweets = ScheduledTweet.all()
  tweets.filter('username =', user.username)
  return tweets.count() >= 5

def schedule(request):
  user = request.user
  if not user.is_authenticated():
    user = AuthenticatedUser(request.POST.get('username'), request.POST.get('password'))
    if Twitterer(user).verify_credentials():
      request.session['user'] = user
    else:
      return HttpResponse('Authentication with Twitter failed. Please check your username and password.',
        status=401, content_type='text/plain')

  if too_many_tweets_sent(user):
    return HttpResponse('Too many Tweets sent.', status=403, content_type='text/plain')

  tweet = ScheduledTweet(username   = user.username,
                         password   = user.password,
                         tweet      = request.POST.get('tweet'),
                         post_at    = datetime.utcfromtimestamp( float(request.POST.get('post_at', 0)) ),
                         ip_address = request.META.get('REMOTE_ADDR'),
                         )
  tweet.put()
  return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')

def review(request):
  tweets = ScheduledTweet.all()
  # TODO: require login.
  tweets.filter('username =', request.user.username)
  tweets.order('-post_at')
  return direct_to_template(request, 'review.html', {'tweets': tweets})

def delete(request):
  if request.method == 'POST' and request.POST['key']:
    ScheduledTweet.get(request.POST.get('key')).delete()
  return HttpResponseRedirect(reverse(review))

# Should be a POST since request changes state of datastore, but (I believe) App Engine
# cron will only perform GET requests.
def batch_tweet(request):
  tweets = ScheduledTweet.all()
  tweets.filter('post_at  <=', datetime.utcnow())
  tweets.filter('tweeted =', False)
  for tweet in tweets:
    # TODO: add e-mail notification (or some other handling) if tweet fails
    if Twitterer(AuthenticatedUser(tweet.username, tweet.password)).tweet(tweet):
      tweet.tweeted = True
      tweet.put()
  return HttpResponse()

def batch_delete(request):
  tweets = ScheduledTweet.all()
  tweets.filter('tweeted =', True)
  # Delete all Tweets >= 1 day old.
  tweets.filter('created_at <=', datetime.utcnow() - timedelta(days=1))
  for tweet in tweets:
    tweet.delete()
  return HttpResponse()

# Should be in its own separate application, perhaps, but this is the only user account-related view
# I have at the moment, and so its presence here is acceptable.
def logout(request):
  # If user unauthenticated, he will not be stored in the session.
  if request.user.is_authenticated():
    del request.session['user']
  return HttpResponseRedirect(reverse(home))
