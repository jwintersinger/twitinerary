# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from models import ScheduledTweet, Twitterer
from datetime import date, datetime, timedelta
from django.http import HttpResponse

def home(request):
  tweets = ScheduledTweet.all()
  tweets.order('-datetime')

  today = date.today()
  days = [today + timedelta(days=n) for n in range(4)]

  return direct_to_template(request, 'index.html', {'tweets': tweets, 'days': days})

def schedule(request):
  tweet = ScheduledTweet()
  tweet.username = request.POST['username']
  tweet.password = request.POST['password']
  tweet.tweet    = request.POST['tweet']
  tweet.datetime = datetime.utcfromtimestamp(float(request.POST['datetime']))

  if Twitterer(tweet.username, tweet.password).verify_credentials():
    tweet.put()
    return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')
  else:
    return HttpResponse('Authentication with Twitter failed. Please check your username and password.',
      status=401, content_type='text/plain')


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
