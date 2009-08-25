import base64
import os
from datetime import datetime, date, timedelta
from urllib import urlencode
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import urlfetch

#=======
# Models
#=======
class ScheduledTweet(db.Model):
  username = db.StringProperty()
  password = db.StringProperty()
  tweet    = db.StringProperty(multiline=True)
  datetime = db.DateTimeProperty()


#=========
# Handlers
#=========
class Home(webapp.RequestHandler):
  def get(self):
    tweets = ScheduledTweet.all()
    tweets.order('-datetime')

    today = date.today()
    days = [today + timedelta(days=n) for n in range(4)]

    template_values = {'tweets': tweets, 'days': days}
    template_path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(template_path, template_values))

class Scheduler(webapp.RequestHandler):
  def post(self):
    tweet = ScheduledTweet()
    tweet.username = self.request.get('username')
    tweet.password = self.request.get('password')
    tweet.tweet    = self.request.get('tweet')
    tweet.datetime = datetime.utcfromtimestamp(float(self.request.get('datetime')))

    self.response.headers['Content-Type'] = 'text/plain'
    if Twitterer(tweet.username, tweet.password).verify_credentials():
      tweet.put()
      self.response.set_status(200)
      self.response.out.write('Woohoo! Your Tweet has been scheduled.')
    else:
      self.response.set_status(401)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write('Authentication with Twitter failed. Please check your username and password.')

  def __verify_credentials(self, username, password):
    response = urlfetch.fetch('http://twitter.com/account/verify_credentials.json')



class Tweeter(webapp.RequestHandler):
  # Should be a POST since request changes state of datastore, but (I believe) cron will only
  # perform GET requests.
  def get(self):
    tweets = ScheduledTweet.all()
    tweets.filter('datetime <=', datetime.utcnow())
    for tweet in tweets:
      # TODO: add e-mail notification (or some other handling) if tweet fails
      if Twitterer(tweet.username, tweet.password).tweet(tweet.tweet):
        tweet.delete()


#===========
# Miscellany
#===========
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


application = webapp.WSGIApplication([
                                       ('/',            Home),
                                       ('/tweets/new',  Scheduler),
                                       ('/tweets/send', Tweeter),
                                     ], debug=True)
def main():
  run_wsgi_app(application)
if __name__ == '__main__':
  main()
