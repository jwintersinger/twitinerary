# -*- coding: utf-8 -*-
from google.appengine.ext import db
class ScheduledTweet(db.Model):
  username = db.StringProperty()
  password = db.StringProperty()
  tweet    = db.StringProperty(multiline=True)
  datetime = db.DateTimeProperty()

import base64
from google.appengine.api import urlfetch
from urllib import urlencode
class Twitterer:
  def __init__(self, username, password):
    self.__username = username
    self.__password = password
    self.__base_url = 'http://twitter.com'

  def tweet(self, tweet):
    response = self.__fetch('/statuses/update.json', {'status': tweet})
    # TODO: report error given in response.content, if it occurred
    return response.status_code == 200

  def verify_credentials(self):
    response = self.__fetch('/account/verify_credentials.json', method=urlfetch.GET)
    return response.status_code == 200

  def __fetch(self, url, params={}, method=urlfetch.POST):
    auth = 'Basic ' + base64.standard_b64encode('%s:%s' % (self.__username, self.__password))
    return urlfetch.fetch(self.__base_url + url, urlencode(params),
                          method=method, headers={'Authorization': auth})
