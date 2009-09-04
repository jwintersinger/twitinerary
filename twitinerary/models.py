from google.appengine.ext import db
class ScheduledTweet(db.Model):
  username   = db.StringProperty()
  password   = db.StringProperty()
  tweet      = db.StringProperty(multiline=True)
  post_at    = db.DateTimeProperty()
  created_at = db.DateTimeProperty(auto_now_add = True)
  ip_address = db.StringProperty()
  tweeted    = db.BooleanProperty(default = False)

import base64
from google.appengine.api import urlfetch
from urllib import urlencode
class Twitterer:
  def __init__(self, user):
    self.__user     = user
    self.__base_url = 'http://twitter.com'

  def tweet(self, tweet):
    response = self.__fetch('/statuses/update.json', {'status': tweet.tweet},
                            additional_headers = {'X-Originating-IP': tweet.ip_address})
    # TODO: report error given in response.content, if it occurred
    return response.status_code == 200

  def verify_credentials(self):
    response = self.__fetch('/account/verify_credentials.json', method=urlfetch.GET)
    return response.status_code == 200

  def __fetch(self, url, params = {}, method = urlfetch.POST, additional_headers = {}):
    auth = 'Basic ' + base64.standard_b64encode('%s:%s' % (self.__user.username, self.__user.password))
    headers = {'Authorization': auth, 'User-Agent': 'Twitinerary'}
    headers.update(additional_headers)
    return urlfetch.fetch(self.__base_url + url, urlencode(params), method = method, headers = headers)

class AuthenticatedUser():
  def __init__(self, username, password):
    self.username = username
    self.password = password

  def is_authenticated(self):
    return True

class UnauthenticatedUser():
  def __init__(self):
    self.username = 'Unauthenticated'

  def is_authenticated(self):
    return False
