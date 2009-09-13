from google.appengine.api import urlfetch
from django.conf import settings
from django.http import HttpResponse

# Ideally, I could upload directly to TweetPic, load the resulting XML
# response into an iframe, then use Javascript to access the iframe's contents
# and report the URL to the user (or notify him of failure). Unfortunately,
# due to the "same origin domain" policy that applies to the contents of
# iframes, this is not possible -- since I'm on a different domain than the
# iframe, I am able to do nothing but read or change its URL.
# 
# As a result, I must use the server on my domain as a proxy of sorts -- I pass
# the browser's POST request directly through to TweeetPic without modifying
# it, then I pass TweetPic's response directly back to the browser. I do not
# believe that Django writes the uploaded image to disk at any point, so at
# least I ought not to have to worry about cleaning up stale uploaded images.
def upload_image(request):
  response = urlfetch.fetch('http://twitpic.com/api/upload',
    headers={'Content-Type':     request.META['CONTENT_TYPE'],
             'User-Agent':       settings.USER_AGENT,
             'X-Originating-IP': request.META['REMOTE_ADDR']},
    payload=request.raw_post_data, method=urlfetch.POST)
  return HttpResponse(response.content, content_type='application/xml')
