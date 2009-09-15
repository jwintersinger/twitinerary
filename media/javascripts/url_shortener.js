function UrlShortener(form, url_input_selector, activator, tweet_input, notifier) {
  this.__form = form;
  this.__url_input = this.__form.find(url_input_selector);
  this.__activator = activator;
  this.__tweet_input = tweet_input;
  this.__notifier = notifier;

  this.__configure_activation();
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

UrlShortener.prototype.__configure_activation = function() {
  var self = this;
  this.__activator.click(function() {
    $(this).hide();
    self.__form.show();
  });
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
      // data.errorMessage will be set if a global error occurred, such as no
      // URL provided (empty input box). Otherwise, error message will be
      // provided in the results array, for it will be specific to the
      // given URL.
      // TODO: more informative error message when blank URL provided?
      if(err = (data.errorMessage || data.results[long_url].errorMessage)) {
        self.__notifier.notify_failure('Error shortening URL: ' + err);
        return;
      }

      var short_url = data.results[long_url].shortUrl;
      self.__url_input.val(self.__default_url_input_value);
      self.__form.hide();
      self.__activator.show();
      self.__tweet_input.insertAtCaret(short_url);
      self.__tweet_input.focus();
    };
    $.getJSON('http://api.bit.ly/shorten?callback=?',
      self.__make_api_options(long_url), callback);
    return false;
  });
}
