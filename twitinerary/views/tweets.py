from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from google.appengine.ext.db import BadKeyError
from twitinerary.models import ScheduledTweet, Twitterer


#=======
# Views
#=======
def home(request):
  response = direct_to_template(request, 'home.html')
  _indicate_twitter_password_stored(request.user, response)
  return response

def new(request):
  return direct_to_template(request, 'new_tweet.html')

def edit(request):
  return direct_to_template(request, 'edit_tweet.html',
      {'tweet': ScheduledTweet.get(request.GET.get('key'))})

def save(request):
  user = request.user
  if not user.is_authenticated():
    return HttpResponse('Not authenticated.', status=401, content_type='text/plain')

  key = request.POST.get('key')
  if key:
    tweet = _get_untweeted_tweet(key, user)
  else:
    # Only check if user exceeded usage limits when new Tweet created, not when
    # editing existing one.
    if _too_many_tweets_sent(user):
      return HttpResponse('Too many Tweets sent.', status=403, content_type='text/plain')
    tweet = ScheduledTweet()

  properties = {'user':       user,
                'tweet':      request.POST.get('tweet'),
                'post_at':    datetime.utcfromtimestamp( float(request.POST.get('post_at', 0)) ),
                'ip_address': request.META.get('REMOTE_ADDR')}
  [setattr(tweet, property, properties[property]) for property in properties]
  tweet.put()
  return HttpResponse('Woohoo! Your Tweet has been scheduled.', content_type='text/plain')

def view(request):
  if not request.user.is_authenticated():
    return HttpResponse('Not authenticated.', status=401, content_type='text/plain')
  tweets = ScheduledTweet.untweeted(request.user)
  return direct_to_template(request, 'view_tweets.html', {'tweets': tweets})

def delete(request):
  tweet = _get_untweeted_tweet(request.POST.get('key'), request.user)
  if request.method == 'POST':
    tweet.delete()
  return HttpResponse('Your Tweet has been deleted.', content_type='text/plain')

def next_scheduled(request):
  from django.utils import simplejson as json
  # Use same conversion method that Django uses in date:"U" filter.
  from django.utils.dateformat import DateFormat

  user = request.user
  if not user.is_authenticated():
    response = {'error': 'Not authenticated.'}
  else:
    tweet = ScheduledTweet.untweeted(user).get()
    response = {'tweet': tweet.tweet, 'post_at': DateFormat(tweet.post_at).U()}
  return HttpResponse(json.dumps(response), content_type='application/json')


#====================
# Assisting functions
#====================
def _indicate_twitter_password_stored(user, response):
  if user.password:
    # The same cookie is used by image_uploader.js, so remember to change its name
    # and value there if you do so here, and vice versa. Don't worry about
    # deleting it or setting it for beyond the browsing session -- both tasks are
    # handled in Javascript. This is only to prevent the user from being prompted
    # for his password in the event that his password is stored in the datastore,
    # but the cookie indicating such has not been set by prior execution of the
    # associated Javascript.
    response.set_cookie('twitter_password_stored', 'true')

def _too_many_tweets_sent(user):
  tweets = ScheduledTweet.all()
  tweets.filter('user =', user)
  return tweets.count() >= 5

# Ensures Tweet belogns to given user and that it has not already been Tweeted.
def _get_untweeted_tweet(key, user):
  tweet = ScheduledTweet.get(key)
  if tweet.user != user:
    raise Exception('User does not own Tweet')
  if tweet.tweeted:
    raise Exception('Tweet already Tweeted')
  return tweet

