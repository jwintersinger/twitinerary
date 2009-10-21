#!/usr/bin/env python
# TODO: add error checking, as requests to Twitter often seem to fail.
# TODO: implement a cron to clean out old tokens periodically

"""
OhAuth is a simple OAuth implementation for authenticating users with
third parties. It is based on AppEngine-OAuth-Library by Mike Knapp.

========
1. Usage
========
Following is a typical OhAuth use case inside a Django view on App Engine. The
example can easily be adapted for use with other Python frameworks on App
Engine, including Google's webapp framework.

1. Create the OhAuth client. In this case we'll use the Twitter client,
   but you can write other clients to connect to different services.

   import ohauth

   consumer_key = "LKlkj83kaio2fjiudjd9...etc"
   consumer_secret = "58kdujslkfojkjsjsdk...etc"

   client = ohauth.TwitterClient(consumer_key, consumer_secret)

2. Send the user to Twitter in order to authenticate:

   return HttpResponseRedirect(client.get_authorization_url('http://example.com/callback'))

3. Once the user has arrived back at your callback URL, you can
   get the authenticated user information:

   request_token = request.GET.get('oauth_token')
   verifier = request.GET.get('oauth_verifier')
   response = client.fetch('/account/verify_credentials.json',
     request_token=request_token, verifier=verifier)

   from django.utils import simplejson as json
   content = json.loads(response.content)
   return HttpResponse(content)

4. Should you wish, the access_token and access_secret can be cached
   to prevent having to go through the OAuth authentication process
   prior to making more API calls. The above example would read as follows:

   request_token = request.GET.get('oauth_token')
   verifier = request.GET.get('oauth_verifier')
   access_token, access_secret = client.get_access_token(request_token, verifier)

   # Store access_token and access_secret as you please, such as in Memcache or
   # the datastore. Then, in a later request, to Tweet:

   # Omitted: retrieve access_token and access_secret from storage, set up client as above
   response = client.fetch('/statuses/update.json', method='POST',
     payload={'status': 'Hello, world!'}, access_token=access_token, access_secret=access_secret)

Note that OhAuth adds a new model to your datastore to store Request Tokens,
and also makes use of Memcache.


===============
2. OAuth Primer
===============
Following is a thirty-second primer on OAuth. For greater detail (including a
more expansive walkthrough), see the OAuth spec (http://oauth.net/core/1.0a).

Definitions:
  * You, programmer extraordinaire, are the Consumer.
  * You consume the service provided by the Service Provider (Twitter).
  * The User is, ah, using your app.

Process:
  1. The Consumer requests a Request Token from the Service Provider. When
     doing so, the Consumer provides a callback URL that will be used in
     the next step.
  2. The Consumer directs the User to the Service Provider, where the Request
     Token obtained in the previous step is authorized by the User.
  3. The Service Provider directs the User back to the callback URL provided
     in step 1. The Request Token is appended to the URL.
  4. The Consumer takes the now-authorized Request Token and exchanges it for
     an Access Token and Access Secret.
  5. The Access Token and Access Secret can now be used to make requests to the
     Service Provider, identifying you as having access to the User's data
     without you knowing his password. It's like magic!
     

================
3. Modifications
================
OhAuth is based on AppEngine-OAuth-Library
(http://github.com/mikeknapp/AppEngine-OAuth-Library/tree/master) by Mike Knapp
(micknapp@gmail.com). Modifications made include:

  * Ripped out all code that provided access to non-Twitter services
    (MySpace, Yahoo). Done as other updates made by me resulted in this code
    not functioning.
  * Ripped out all code that dealt specifically with providing access to user
    details.
  * Added code to permit one to easily request arbitrary resources, rather
    than being limited to user details.
  * Changed nomenclature for consistency with OAuth spec:
    "auth_token" -> "request_token"
  * Moved specification of callback URL from constructor to call for
    authorization URL, preventing us from having to specify it when it will
    not be used.
  * Removed duplication of protocol and domain name from URLs by supporting
    a URL prefix.
  * Permit non-GET requests (e.g., POST).
  * Added ability to send user agent string with requests.
  * OAuth parameters can be sent in the Authorization header rather than the
    request body or as part of the URL query string, as per the OAuth spec.
  * Rudimentary error handling has been added, with network requests retried
    when they fail.


============
4. Resources
============
  * OAuth specification: http://oauth.net/core/1.0a
  * Altenative library: http://github.com/tav/tweetapp/tree/master


@author: Jeff Wintersinger <jeff@micand.com>
@copyright: Unrestricted. Feel free to use modify however you see fit.
"""

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import db

from cgi import parse_qs
from django.utils import simplejson as json
from hashlib import sha1
from hmac import new as hmac
from random import getrandbits
from time import time
from urllib import urlencode
from urllib import quote as urlquote
from urllib import unquote as urlunquote

import logging


class OauthRequestToken(db.Model):
  """Request Token.

  The Request Token must be authorized by the Service Provider (e.g., Twitter).
  Once this is done, it is exchanged for an Access Token and then used to make
  requests.
  """
  service = db.StringProperty(required=True)
  token = db.StringProperty(required=True)
  secret = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)


class OhAuthClient():
  def __init__(self, service_name, consumer_key, consumer_secret,
               authorization_url, request_url, access_url, user_agent=""):
    self.service_name = service_name
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self._authorization_url = authorization_url
    self.request_url = request_url
    self.access_url = access_url
    self._user_agent = user_agent
    self._realm = self._url_prefix

  def get_authorization_url(self, callback_url):
    """Returns the URL to which the User must be directed to get his Request Token authorized.
    
    Must pass the callback_url to which the User will be redirected after
    authorizing his Request Token."""
    return "%s%s?oauth_token=%s" % (self._url_prefix, self._authorization_url,
                                    self._get_request_token(callback_url))

  def get_access_token(self, request_token, verifier):
    """Exchanges a Request Token for an Access Token. Returns (access_token, access_secret).
    
    Note that the access_token and access_secret can be stored, allowing future
    requests to be made without going through the happy OAuth dance again.
    """
    request_token, verifier = urlunquote(request_token), urlunquote(verifier)
    request_secret = self._retrieve_request_secret(request_token)

    access_request = self._make_request(self.access_url,
                                       method            = 'POST',
                                       token             = request_token,
                                       secret            = request_secret,
                                       additional_oauth  = {"oauth_verifier": verifier})
    access_response = self._extract_credentials(access_request)
    return (access_response["token"], access_response["secret"])

  def fetch(self, resource_url, method='GET', payload={},
            access_token=None, access_secret=None,
            request_token=None, verifier=None):
    """Fetch a resource once OAuth authentication is complete.
    
    One Must supply either a request_token and verifier, or an access_token and
    access_secret. In the former case, the request_token is exchanged for an
    acecss_token before making the request.

    method can be GET, POST, HEAD, PUT, or DELETE. payload is the body content
    for a POST or PUT request.
    """
    if request_token and verifier:
      access_token, access_secret = self.get_access_token(request_token, verifier)
    elif not (access_token and access_secret):
      raise Exception, "Must pass request_token and verifier, or access_token and access_secret."
    return self._make_request(resource_url, method=method, payload=payload,
                             token=access_token, secret=access_secret)

  def _request_method_name_to_constant(self, name):
    # A similar method exists in the App Engine API, but it's not public, so I rewrote my own.
    methods = {
      'GET': urlfetch.GET,
      'POST': urlfetch.POST,
      'HEAD': urlfetch.HEAD,
      'PUT': urlfetch.PUT,
      'DELETE': urlfetch.DELETE
    }
    return methods[name]

  def _encode(self, text):
    """Encodes value as per the OAuth API."""
    return urlquote(str(text), "")

  def _generate_signature(self, method, url, oauth_params, payload, secret):
    """Generates a HMAC-SHA1 signature for the request."""
    # Join all of the params together.
    combined = oauth_params.copy()
    combined.update(payload)
    params_str = "&".join(["%s=%s" % (self._encode(k), self._encode(combined[k]))
                           for k in sorted(combined)])
    # Join the entire message together per the OAuth specification.
    message = "&".join([self._encode(item) for item in (method, url, params_str)])

    # Create a HMAC-SHA1 signature of the message.
    key = "%s&%s" % (self.consumer_secret, secret) # Note compulsory "&".
    signature = hmac(key, message, sha1)
    return signature.digest().encode("base64").strip()

  def _configure_oauth_params(self, token, additional_oauth):
    """Returns all OAuth params needed for request save for the signature."""
    oauth_params = {
      "oauth_consumer_key": self.consumer_key,
      "oauth_signature_method": "HMAC-SHA1",
      "oauth_timestamp": str(int(time())),
      "oauth_nonce": str(getrandbits(64)),
      "oauth_version": "1.0"
    }
    if token:
      oauth_params["oauth_token"] = token
    if additional_oauth:
      oauth_params.update(additional_oauth)
    return oauth_params

  def _configure_request_headers(self, oauth_params, payload):
    """Generates the appropriate headers for the request.

    Note that if the OAuth client is configured not to use the Authorization
    header, payload will instead receive the parameters rather than having them
    inserted as a header. This way, the OAuth params will be included as part
    of the URL query string (GET request) or request body (POST request).
    """
    headers = {}
    if self._use_auth_header:
      params_str = ", ".join(['%s="%s"' % (self._encode(k), self._encode(oauth_params[k])) for k in oauth_params])
      headers["Authorization"] = 'OAuth realm="%s", %s' % (self._encode(self._realm), params_str)
    else:
      payload.update(oauth_params)
    if self._user_agent:
      headers["User-Agent"] = self._user_agent
    return headers

  def _make_request(self, path, method='GET', payload={},
                   additional_oauth={}, token="", secret=""):
    """Fetches the resource specified by path.

    If the request fails (the response's status code indicates failure, or an
    exception is raised), it will be retried once.
    """
    url = "%s%s" % (self._url_prefix, path)
    method = method.upper()
    oauth_params = self._configure_oauth_params(token, additional_oauth)
    oauth_params['oauth_signature'] = self._generate_signature(method, url, oauth_params, payload, secret)
    headers = self._configure_request_headers(oauth_params, payload)

    encoded_payload = None
    if method in ('POST', 'PUT'):
      encoded_payload = urlencode(payload)
    elif payload:
      url = "%s?%s" % (url, urlencode(payload))

    request = lambda: urlfetch.fetch(url, payload=encoded_payload,
      method=self._request_method_name_to_constant(method), headers=headers)
    try:
      response = request()
      if response.status_code == 503: # Retry once if status is "Service Unavailable".
        logging.error('urlfetch attempt returned HTTP 503 Service Unavailable.')
        response = request()
    except urlfetch.DownloadError:
      logging.error('urlfetch attempt raised DownloadError on %s %s' % (url, method))
      response = request() # Retry once if DownloadError raised.
    return response
    
  def _retrieve_request_secret(self, request_token):
    """Retrieves the request_secret corresponding to request_token from the DB or Memcache."""
    request_secret = memcache.get(self._get_memcache_request_token_key(request_token))
    if request_secret:
      return request_secret
    else: # If request_secret not in memcache, must retrieve from DB.
      request_secret = OauthRequestToken.gql("""
        WHERE
          service = :1 AND
          token = :2
        LIMIT
          1
      """, self.service_name, request_token).get()

      if not request_secret:
        msg = "The Request Secret for Request Token %s was not found in our DB" % request_token
        logging.error(msg)
        raise Exception, msg
      else:
        return request_secret.secret

  def _get_request_token(self, callback_url):
    """Retrieves an unauthorized Request Token from the Service Provider.

    The Request Token and Request Secret are stored in the DB, while the latter
    is also stored via Memcache.
    """

    response = self._make_request(self.request_url,
        additional_oauth={"oauth_callback": callback_url})
    request = self._extract_credentials(response)
    request_token, request_secret = request["token"], request["secret"]

    # Save the request token and secret in our database.
    request = OauthRequestToken(service=self.service_name,
                                token=request_token,
                                secret=request_secret)
    request.put()

    # Add the request secret to Memcache as well.
    memcache.set(self._get_memcache_request_token_key(request_token),
                 request_secret, time=20*60) # Save for 20 minutes
    return request_token

  def _get_memcache_request_token_key(self, request_token):
    """Generate Request Token key name for Memcache."""
    return "oauth_%s_%s" % (self.service_name, request_token)

  def _extract_credentials(self, result):
    """Extract the token and secret from the query string-formatted response.

    Returns an dictionary containing the token and secret (if present). Throws
    an Exception otherwise.
    """

    token = None
    secret = None
    parsed_results = parse_qs(result.content)

    if "oauth_token" in parsed_results:
      token = parsed_results["oauth_token"][0]
    if "oauth_token_secret" in parsed_results:
      secret = parsed_results["oauth_token_secret"][0]

    if not (token and secret) or result.status_code != 200:
      msg = "Could not extract token/secret from response: %s" % result.content
      logging.error(msg)
      raise Exception, msg

    return {
      "service": self.service_name,
      "token": token,
      "secret": secret
    }


class TwitterClient(OhAuthClient):
  """Twitter client.

  A client for talking to the Twitter API using OAuth as the authentication
  model.
  """

  def __init__(self, consumer_key, consumer_secret, user_agent=""):
    """Constructor."""
    self._url_prefix = "http://twitter.com"
    self._use_auth_header = True

    OhAuthClient.__init__(self,
        "twitter",
        consumer_key,
        consumer_secret,
        "/oauth/authorize",
        "/oauth/request_token",
        "/oauth/access_token",
        user_agent)
