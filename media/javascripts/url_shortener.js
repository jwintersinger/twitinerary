function UrlShortener(form, url_input_selector, tweet_input) {
  this.__form = form;
  this.__url_input = this.__form.find(url_input_selector);
  this.__tweet_input = tweet_input;
  this.__configure_clear_on_activation();
  this.__configure_form_submission();
}

UrlShortener.prototype.__make_api_options = function(long_url) {
  return {
    version: '2.0.1',
    login:   'twitinerary',
    // If you steal my API key, I will make you feel pain.
    apiKey:  'R_d72586cf8628bb565d0521aa8b7767de',
    longUrl: long_url
  };
}

UrlShortener.prototype.__configure_clear_on_activation = function() {
  this.__default_url_input_value = this.__url_input.val();
  var self = this;
  this.__url_input.focus(function() {
    if($(this).val() == self.__default_url_input_value) $(this).val('');
  });
}

UrlShortener.prototype.__configure_form_submission = function() {
  var self = this;
  this.__form.submit(function() {
    var long_url = self.__url_input.val();
    var callback = function (data) {
      var short_url = data.results[long_url].shortUrl;
      self.__url_input.val(self.__default_url_input_value);
      self.__tweet_input.val(self.__tweet_input.val() + short_url);
      self.__tweet_input.focus();
    };
    $.getJSON('http://api.bit.ly/shorten?callback=?',
      self.__make_api_options(long_url), callback);
    return false;
  });

}
