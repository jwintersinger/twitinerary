import logging
from datetime import datetime, timedelta
from twitinerary.models import ScheduledTweet, Twitterer, AuthenticatedUser
from django.http import HttpResponse

# Should be a POST since request changes state of datastore, but (I believe) App Engine
# cron will only perform GET requests.
def batch_send(request):
  tweets = ScheduledTweet.all()
  tweets.filter('post_at  <=', datetime.utcnow())
  tweets.filter('tweeted =', False)
  twitterer = Twitterer()
  for tweet in tweets:
    try:
      successfully_tweeted = twitterer.tweet(tweet)
    except Exception, e:
      # TODO: add e-mail notification (or some other handling) if tweet fails. Or perhaps
      # should simply notify whenever logging.error is called.
      logging.error('%s raised when sending Tweet %s: %s' % (repr(e), tweet, e))
    else:
      if successfully_tweeted:
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
