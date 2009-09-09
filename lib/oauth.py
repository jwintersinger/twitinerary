#!/usr/bin/env python

# Taken from http://github.com/mikeknapp/AppEngine-OAuth-Library/tree/master
# Alternative: http://github.com/tav/tweetapp/tree/master
# Others: http://apiwiki.twitter.com/OAuth-Examples
# 
# OAuth specification: http://oauth.net/core/1.0a
#
# Modifications:
#   * Ripped out all code that provided access to non-Twitter services
#     (MySpace, Yahoo). Done as other updates made by me resulted in this code
#     not functioning.
#   * Ripped out all code that dealt specifically with providing access to user
#     details.
#   * Added code to permit one to easily request arbitrary resources, rather
#     than being limited to user details.
#   * Changed nomenclature for consistency with OAuth spec:
#     "auth_token" -> "request_token"

"""
A simple OAuth implementation for authenticating users with third party
websites.

A typical use case inside an AppEngine controller would be:

1) Create the OAuth client. In this case we'll use the Twitter client,
  but you could write other clients to connect to different services.

  import oauth

  consumer_key = "LKlkj83kaio2fjiudjd9...etc"
  consumer_secret = "58kdujslkfojkjsjsdk...etc"
  callback_url = "http://www.myurl.com/callback/twitter"

  client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)

2) Send the user to Twitter in order to login:

  self.redirect(client.get_authorization_url())

3) Once the user has arrived back at your callback URL, you'll want to
  get the authenticated user information.

  auth_token = self.request.get("oauth_token")
  user_info = client.get_user_info(auth_token)

  The "user_info" variable should then contain a dictionary of various
  user information (id, picture url, etc). What you do with that data is up
  to you.

  That's it!

4) If you need to, you can also call other other API URLs using
  client.make_request() as long as you supply a valid API URL and an access
  token and secret.

@author: Mike Knapp <micknapp@gmail.com>
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


def get_oauth_client(service, key, secret, callback_url):
  """Get OAuth Client.

  A factory that will return the appropriate OAuth client.
  """

  if service == "twitter":
    return TwitterClient(key, secret, callback_url)
  else:
    raise Exception, "Unknown OAuth service %s" % service

class OauthRequestToken(db.Model):
  """Request Token.

  A temporary request token that we will use to authenticate a user with a
  third party website. (We need to store the data while the user visits
  the third party website to authenticate themselves.)

  TODO: Implement a cron to clean out old tokens periodically.
  """
  service = db.StringProperty(required=True)
  token = db.StringProperty(required=True)
  secret = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)

class OAuthClient():
  def __init__(self, service_name, consumer_key, consumer_secret, request_url,
               access_url, callback_url=None):
    """ Constructor."""

    self.service_name = service_name
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.request_url = request_url
    self.access_url = access_url
    self.callback_url = callback_url

  def make_request(self, url, token="", secret="", additional_params=None,
                   protected=False):
    """Make Request.

    Make an authenticated request to any OAuth protected resource. At present
    only GET requests are supported.

    If protected is equal to True, the Authorization: OAuth header will be set.

    A urlfetch response object is returned.
    """

    def encode(text):
      return urlquote(str(text), "")

    params = {
      "oauth_consumer_key": self.consumer_key,
      "oauth_signature_method": "HMAC-SHA1",
      "oauth_timestamp": str(int(time())),
      "oauth_nonce": str(getrandbits(64)),
      "oauth_version": "1.0"
    }

    if token:
      params["oauth_token"] = token
    elif self.callback_url:
      params["oauth_callback"] = self.callback_url

    if additional_params:
      params.update(additional_params)

    # Join all of the params together.
    params_str = "&".join(["%s=%s" % (encode(k), encode(params[k]))
                           for k in sorted(params)])

    # Join the entire message together per the OAuth specification.
    message = "&".join(["GET", encode(url), encode(params_str)])

    # Create a HMAC-SHA1 signature of the message.
    key = "%s&%s" % (self.consumer_secret, secret) # Note compulsory "&".
    signature = hmac(key, message, sha1)
    digest_base64 = signature.digest().encode("base64").strip()
    params["oauth_signature"] = digest_base64

    # Construct and fetch the URL and return the result object.
    url = "%s?%s" % (url, urlencode(params))

    headers = {}
    if protected:
      headers["Authorization"] = "OAuth"

    return urlfetch.fetch(url, headers=headers)

  def get_authorization_url(self):
    """Get Authorization URL.

    Returns a service specific URL which contains an auth token. The user
    should be redirected to this URL so that they can give consent to be
    logged in.
    """

    raise NotImplementedError, "Must be implemented by a subclass"

  def _retrieve_request_secret(self, request_token):
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

  def _retrieve_access_token(self, request_token, request_secret, verifier):
    # Exchange Request Token for Access Token.
    access_request = self.make_request(self.access_url,
                                       token=request_token,
                                       secret=request_secret,
                                       additional_params={"oauth_verifier": verifier})
    access_response = self._extract_credentials(access_request)
    return (access_response["token"], access_response["secret"])

  def fetch(self, resource_url, request_token, verifier=""):
    request_token, verifier = urlunquote(request_token), urlunquote(verifier)
    request_secret = self._retrieve_request_secret(request_token)
    access_token, access_secret = self._retrieve_access_token(request_token, request_secret, verifier)
    resource = self.make_request(resource_url, token=access_token, secret=access_secret, protected=True)
    # TODO: encoding always JSON?
    return json.loads(resource.content)

  def _get_request_token(self):
    """Get Request Token.

    Actually gets the request token and secret from the service. The
    token and secret are stored in our database, and the request token is
    returned.
    """

    response = self.make_request(self.request_url)
    request = self._extract_credentials(response)
    request_token, request_secret = request["token"], request["secret"]

    # Save the auth token and secret in our database.
    auth = OauthRequestToken(service=self.service_name,
                        token=request_token,
                        secret=request_secret)
    auth.put()

    # Add the secret to memcache as well.
    memcache.set(self._get_memcache_request_token_key(request_token),
                 request_secret, time=20*60) # Save for 20 minutes
    return request_token

  def _get_memcache_request_token_key(self, request_token):
    return "oauth_%s_%s" % (self.service_name, request_token)

  def _extract_credentials(self, result):
    """Extract Credentials.

    Returns an dictionary containing the token and secret (if present).
    Throws an Exception otherwise.
    """

    token = None
    secret = None
    parsed_results = parse_qs(result.content)

    if "oauth_token" in parsed_results:
      token = parsed_results["oauth_token"][0]

    if "oauth_token_secret" in parsed_results:
      secret = parsed_results["oauth_token_secret"][0]

    if not (token and secret) or result.status_code != 200:
      msg = "Could not extract token/secret: %s" % result.content
      logging.error(msg)
      raise Exception, msg

    return {
      "service": self.service_name,
      "token": token,
      "secret": secret
    }


class TwitterClient(OAuthClient):
  """Twitter Client.

  A client for talking to the Twitter API using OAuth as the
  authentication model.
  """

  def __init__(self, consumer_key, consumer_secret, callback_url):
    """Constructor."""

    OAuthClient.__init__(self,
        "twitter",
        consumer_key,
        consumer_secret,
        "http://twitter.com/oauth/request_token",
        "http://twitter.com/oauth/access_token",
        callback_url)

  def get_authorization_url(self):
    """Get Authorization URL."""
    return "http://twitter.com/oauth/authorize?oauth_token=%s" % self._get_request_token()
