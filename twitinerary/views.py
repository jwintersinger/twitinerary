# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from models import ScheduledTweet, Twitterer, User
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
  user = request.session.get('user') or User(request.POST['username'], request.POST['password'])
  if Twitterer(user).verify_credentials():
    tweet = ScheduledTweet(username = user.username,
                           password = user.password,
                           tweet    = request.POST['tweet'],
                           datetime = datetime.utcfromtimestamp(float(request.POST['datetime'])) )
    tweet.put()
    request.session['user'] = user
    return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')
  else:
    return HttpResponse('Authentication with Twitter failed. Please check your username and password.',
      status=401, content_type='text/plain')


def review(request):
  tweets = ScheduledTweet.all()
  # TODO: require login.
  tweets.filter('username =', request.session['user'].username)
  tweets.order('-datetime')
  return direct_to_template(request, 'review.html', {'tweets': tweets})

def delete(request):
  if request.method == 'POST' and request.POST['key']:
    ScheduledTweet.get(request.POST['key']).delete()
  return HttpResponseRedirect(reverse(review))

# Should be a POST since request changes state of datastore, but (I believe) App Engine
# cron will only perform GET requests.
def mass_tweet(request):
  tweets = ScheduledTweet.all()
  tweets.filter('datetime <=', datetime.utcnow())
  for tweet in tweets:
    # TODO: add e-mail notification (or some other handling) if tweet fails
    if Twitterer(tweet.username, tweet.password).tweet(tweet.tweet):
      tweet.delete()
  return HttpResponse()

# Should be in its own separate application, perhaps, but this is the only user account-related view
# I have at the moment, and so its presence here is acceptable.
def logout(request):
  if 'user' in request.session:
    del request.session['user']
  return HttpResponseRedirect(reverse(home))
