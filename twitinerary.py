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

    tweet.put()
    # No explicit response returns empty HTTP 200.


class Tweeter(webapp.RequestHandler):
  # Should be a POST since request changes state of datastore, but (I believe) cron will only
  # perform GET requests.
  def get(self):
    tweets = ScheduledTweet.all()
    tweets.filter('datetime <=', datetime.utcnow())
    for tweet in tweets:
      self.__tweet(tweet)
      tweet.delete()

  def __tweet(self, tweet):
    auth_string = 'Basic ' + base64.standard_b64encode('%s:%s' % (tweet.username, tweet.password))
    response = urlfetch.fetch('http://twitter.com/statuses/update.json',
                              urlencode({'status': tweet.tweet}),
                              method=urlfetch.POST, headers={'Authorization': auth_string})
    import cgi
    return cgi.escape(repr([response.content, response.status_code, response.headers]))



application = webapp.WSGIApplication([
                                       ('/',            Home),
                                       ('/tweets/new',  Scheduler),
                                       ('/tweets/send', Tweeter),
                                     ], debug=True)
def main():
  run_wsgi_app(application)
if __name__ == '__main__':
  main()
