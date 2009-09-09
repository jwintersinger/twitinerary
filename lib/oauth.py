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
#   * Moved specification of callback URL from constructor to call for
#     authorization URL, preventing us from having to specify it when it will
#     not be used.
#   * Removed duplication of protocol and domain name from URLs by supporting
#     a URL prefix.
#   * Permit non-GET requests (e.g., POST).
#   * Added ability to send user agent string with requests.
#   * OAuth parameters can be sent in the Authorization header rather than the
#     request body or as part of the URL query string, as per the OAuth spec.
#
# TODO: add error checking, as requests to Twitter often seem to fail.
# TODO: implement a cron to clean out old tokens periodically

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


class OauthRequestToken(db.Model):
  """Request Token.

  A temporary request token that we will use to authenticate a user with a
  third party website. (We need to store the data while the user visits
  the third party website to authenticate themselves.)

  """
  service = db.StringProperty(required=True)
  token = db.StringProperty(required=True)
  secret = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)


class OAuthClient():
  def __init__(self, service_name, consumer_key, consumer_secret,
               authorization_url, request_url, access_url, user_agent=""):
    """ Constructor."""

    self.service_name = service_name
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self._authorization_url = authorization_url
    self.request_url = request_url
    self.access_url = access_url
    self._user_agent = user_agent
    self._realm = self._url_prefix

  def get_authorization_url(self, callback_url):
    return "%s%s?oauth_token=%s" % (self._url_prefix, self._authorization_url,
                                    self._get_request_token(callback_url))

  def get_access_token(self, request_token, verifier):
    """Exchange Request Token for Access Token. Returns (access_token, access_secret)."""
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
    """Must supply either request_token and verifier, or access_token and access_secret.
       If the latter, the request_token is converted to an access_token."""
    if request_token and verifier:
      access_token, access_secret = self.get_access_token(request_token, verifier)
    elif not (access_token and access_secret):
      raise Exception, "Must pass request_token and verifier, or access_token and access_secret."
    return self._make_request(resource_url, method=method, payload=payload,
                             token=access_token, secret=access_secret)

  def _request_method_name_to_constant(self, name):
    methods = {
      'GET': urlfetch.GET,
      'POST': urlfetch.POST,
      'HEAD': urlfetch.HEAD,
      'PUT': urlfetch.PUT,
      'DELETE': urlfetch.DELETE
    }
    return methods[name]

  def _encode(self, text):
    return urlquote(str(text), "")

  def _generate_signature(self, method, url, oauth_params, payload, secret):
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
    """Make Request.

    Make an authenticated request to any OAuth protected resource. At present
    only GET requests are supported.

    A urlfetch response object is returned.
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
    return urlfetch.fetch(url, payload=encoded_payload,
      method=self._request_method_name_to_constant(method), headers=headers)
    
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

  def _get_request_token(self, callback_url):
    """Get Request Token.

    Actually gets the request token and secret from the service. The
    token and secret are stored in our database, and the request token is
    returned.
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

    # Add the request secret to memcache as well.
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
      msg = "Could not extract token/secret from response: %s" % result.content
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

  def __init__(self, consumer_key, consumer_secret, user_agent=""):
    """Constructor."""
    self._url_prefix = "http://twitter.com"
    self._use_auth_header = True

    OAuthClient.__init__(self,
        "twitter",
        consumer_key,
        consumer_secret,
        "/oauth/authorize",
        "/oauth/request_token",
        "/oauth/access_token",
        user_agent)
