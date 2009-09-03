# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from models import ScheduledTweet, Twitterer, AuthenticatedUser
from datetime import date, datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
  tweets = ScheduledTweet.all()
  tweets.order('-datetime')

  today = date.today()
  days = [today + timedelta(days=n) for n in range(4)]

  return direct_to_template(request, 'index.html', {'tweets': tweets, 'days': days})

def schedule(request):
  user = request.user
  if not user.is_authenticated():
    user = AuthenticatedUser(request.POST.get('username'), request.POST.get('password'))

  if Twitterer(user).verify_credentials():
    request.session['user'] = user
    tweet = ScheduledTweet(username = user.username,
                           password = user.password,
                           tweet    = request.POST.get('tweet'),
                           datetime = datetime.utcfromtimestamp(float(request.POST.get('datetime', 0))) )
    tweet.put()
    return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')
  else:
    return HttpResponse('Authentication with Twitter failed. Please check your username and password.',
      status=401, content_type='text/plain')

def review(request):
  tweets = ScheduledTweet.all()
  # TODO: require login.
  tweets.filter('username =', request.user.username)
  tweets.order('-datetime')
  return direct_to_template(request, 'review.html', {'tweets': tweets})

def delete(request):
  if request.method == 'POST' and request.POST['key']:
    ScheduledTweet.get(request.POST.get('key')).delete()
  return HttpResponseRedirect(reverse(review))

# Should be a POST since request changes state of datastore, but (I believe) App Engine
# cron will only perform GET requests.
def mass_tweet(request):
  tweets = ScheduledTweet.all()
  tweets.filter('datetime <=', datetime.utcnow())
  for tweet in tweets:
    # TODO: add e-mail notification (or some other handling) if tweet fails
    if Twitterer(AuthenticatedUser(tweet.username, tweet.password)).tweet(tweet.tweet):
      tweet.delete()
  return HttpResponse()

# Should be in its own separate application, perhaps, but this is the only user account-related view
# I have at the moment, and so its presence here is acceptable.
def logout(request):
  # If user unauthenticated, he will not be stored in the session.
  if request.user.is_authenticated():
    del request.session['user']
  return HttpResponseRedirect(reverse(home))
