import time
import hashlib
from google.appengine.api import urlfetch
from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
from cgi import escape as cgi_escape
from urllib import quote as urlquote

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
  user = request.user
  media = request.FILES.get('media')
  password = _retrieve_and_store_password(user, request.POST.get('password'))

  content_type, payload = _encode_to_multipart_form_data(
    {'username': user.username, 'password': password, 'media': media})
  headers = {'Content-Type': content_type, 'User-Agent': settings.USER_AGENT,
    'X-Originating-IP': request.META['REMOTE_ADDR']}
  response = urlfetch.fetch('http://twitpic.com/api/upload', headers=headers,
    payload=payload, method=urlfetch.POST)
  return HttpResponse(response.content, status=response.status_code,
      content_type=response.headers.get('content-type', 'application/xml'))

def _encode_to_multipart_form_data(data):
  # Taken from django.test.client -- imperfect, but good enough.
  is_file = lambda thing: hasattr(thing, "read") and callable(thing.read)

  boundary = 20*'-' + hashlib.sha1('Mmm, salty! %s' % time.time()).hexdigest()
  content_type = 'multipart/form-data; boundary=%s' % boundary
  lines = []
  for key in data:
    # Note that all strings coming from the framework are converted to byte strings
    # from Unicode strings to prevent UnicodeDecodeErrors.
    lines += ['--%s' % boundary, 'Content-Disposition: form-data; name="%s"' % _escape(key)]
    if is_file(data[key]):
      lines[-1] += '; filename="%s"' % _escape(data[key].name)
      lines.append('Content-Type: %s' % _escape(data[key].content_type))
    lines.append('')
    lines.append(is_file(data[key]) and data[key].read() or _escape(data[key]))
  lines += ['--%s--' % boundary, '']
  return (content_type, '\r\n'.join(lines))

def _retrieve_and_store_password(user, prospective_password):
  """If prospective_password is provided, write it to the datastore as the
  user's password and then return it. Otherwise, return the password already
  in the datastore."""
  if prospective_password:
    user.password = prospective_password
    user.put()
  return user.password

# Naiive attempt at esacping stings for headers. I hope it's sufficient.
def _escape(s):
  return cgi_escape(urlquote(smart_str(s)), True)

