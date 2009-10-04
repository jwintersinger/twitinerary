from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from google.appengine.ext.db import BadKeyError
from lib.view_decorators import *
from lib.http import JsonResponse
from twitinerary.models import ScheduledTweet, Twitterer

#=======
# Views
#=======
def home(request):
  response = direct_to_template(request, 'home.html')
  _indicate_twitter_password_stored(request.user, response)
  return response

@login_required()
def new(request):
  return direct_to_template(request, 'new_tweet.html')

@login_required()
def edit(request):
  return direct_to_template(request, 'edit_tweet.html',
      {'tweet': ScheduledTweet.get(request.GET.get('key'))})

@login_required()
@post_required
def save(request):
  user = request.user
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

@login_required()
def view(request):
  tweets = ScheduledTweet.untweeted(request.user)
  return direct_to_template(request, 'view_tweets.html', {'tweets': tweets})

@login_required()
@post_required
def delete(request):
  tweet = _get_untweeted_tweet(request.POST.get('key'), request.user)
  tweet.delete()
  return HttpResponse('Your Tweet has been deleted.', content_type='text/plain')

@login_required('json')
def next_scheduled(request):
  from django.template import Context
  from django.template.loader import get_template

  tweet = ScheduledTweet.untweeted(request.user, descending = False).get()
  if tweet:
    template = get_template('_next_scheduled_tweet.html')
    content = template.render(Context({'tweet': tweet}))
    return JsonResponse({'content': content})
  else:
    # HTTP status code must currently be 200 -- otherwise, jQuery's getJSON
    # won't execute my callback, thereby preventing me from handling the error.
    return JsonResponse({'error_code': 'no_tweets_scheduled', 'error_text': 'No Tweets scheduled.'})


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
