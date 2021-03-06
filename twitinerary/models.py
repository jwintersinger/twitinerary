import base64
import logging
from django.conf import settings
from google.appengine.ext import db
from google.appengine.api import urlfetch
from lib import ohauth
from urllib import urlencode

class Twitterer:
  def tweet(self, tweet):
    client = ohauth.TwitterClient(settings.OAUTH_CONSUMER_KEY,
      settings.OAUTH_CONSUMER_SECRET, settings.USER_AGENT)
    response = client.fetch('/statuses/update.json', method='POST',
      payload={'status': tweet.tweet}, access_token=tweet.user.access_token,
      access_secret=tweet.user.access_secret)

    if response.status_code == 200:
      logging.info('Successfully tweeted "%s"' % tweet.tweet)
      return True
    else:
      logging.error('Tweet failed [%s]: %s' % (response.status_code, tweet.tweet))
      return False

class AuthenticatedUser(db.Model):
  username      = db.StringProperty(required=True)
  password      = db.StringProperty()
  access_token  = db.StringProperty()
  access_secret = db.StringProperty()

  def is_authenticated(self):
    return True

class UnauthenticatedUser():
  def __init__(self):
    self.username = 'Unauthenticated'
    self.password = None

  def is_authenticated(self):
    return False

class ScheduledTweet(db.Model):
  user       = db.ReferenceProperty(AuthenticatedUser)
  tweet      = db.StringProperty(multiline=True)
  post_at    = db.DateTimeProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  ip_address = db.StringProperty()
  tweeted    = db.BooleanProperty(default = False)

  @classmethod
  def untweeted(cls, user, descending = True):
    tweets = cls.all()
    tweets.filter('user =', user)
    tweets.filter('tweeted =', False)
    direction = descending and '-' or ''
    tweets.order(direction + 'post_at')
    tweets.order(direction + 'created_at')
    return tweets
