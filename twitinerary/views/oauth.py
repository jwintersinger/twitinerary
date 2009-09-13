from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import simplejson as json
from lib import ohauth
from twitinerary.models import AuthenticatedUser

def sign_out(request):
  if 'user_key' in request.session:
    del request.session['user_key']
  return HttpResponseRedirect(reverse('twitinerary.views.tweets.home'))

def authenticate(request):
  client = ohauth.TwitterClient(settings.OAUTH_CONSUMER_KEY,
                            settings.OAUTH_CONSUMER_SECRET,
                            settings.USER_AGENT)

  if ('oauth_token' in request.GET) and ('oauth_verifier' in request.GET):
    request_token = request.GET.get('oauth_token')
    verifier = request.GET.get('oauth_verifier')
    access_token, access_secret = client.get_access_token(request_token, verifier)
    response = client.fetch('/account/verify_credentials.json', access_token=access_token,
                            access_secret=access_secret)

    user_info = json.loads(response.content)
    username = user_info['screen_name']
    user = AuthenticatedUser.get_or_insert(key_name      = username,
                                           username      = username,
                                           access_token  = access_token,
                                           access_secret = access_secret)
    request.session['user_key'] = user.key()
    return HttpResponseRedirect(reverse('twitinerary.views.tweets.home'))
  else:
    return HttpResponseRedirect( client.get_authorization_url(request.build_absolute_uri()) )
