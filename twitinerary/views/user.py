from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def logout(request):
  if 'user_key' in request.session:
    del request.session['user_key']
  return HttpResponseRedirect(reverse('twitinerary.views.tweets.home'))
