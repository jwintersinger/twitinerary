function UrlShortener(form, url_input_selector, toggler, tweet_input, notifier) {
  this.__form = form;
  this.__url_input = this.__form.find(url_input_selector);
  this.__toggler = toggler;
  this.__tweet_input = tweet_input;
  this.__notifier = notifier;

  this.__configure_form_toggle();
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

UrlShortener.prototype.__configure_form_toggle = function() {
  var self = this;
  this.__toggler.click(function() {
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
      self.__toggler.show();
      self.__tweet_input.insertAtCaret(short_url);
      self.__tweet_input.focus();
    };
    $.getJSON('http://api.bit.ly/shorten?callback=?',
      self.__make_api_options(long_url), callback);
    return false;
  });
}

// See:
//   * http://stackoverflow.com/questions/946534/insert-text-into-textarea-with-jquery
//   * http://laboratorium.0xab.cd/jquery/fieldselection/0.1.0/jquery-fieldselection.js
$.fn.extend({
  insertAtCaret: function(str) {
    var self = this[0];

    // Every browser that doesn't suck (i.e., not IE).
    //   Need additional test in condition, for self.selectionStart evaluates
    //   to false when caret is at beginning of input box, when
    //   self.selectionStart = 0.
    // Note that the StackOverflow link above contained code that would
    // supposedly work for IE, but it only inserted at caret when the focus
    // was on the textarea when this function was called -- otherwise, it
    // simply prepended the text to the contents of the textarea. As the input
    // focus will usually be on the "shorten URL" input box when I call this
    // function, not on the textarea, I have jettisoned the IE-specific code so
    // that IE simply falls back on the (not quite desireable) appending code.
    if (self.selectionStart || self.selectionStart == 0) {
      var start = self.selectionStart;
      var end = self.selectionEnd;
      var old_scroll_top = self.scrollTop;

      self.value = self.value.substring(0, start) + str + self.value.substring(end, self.value.length);
      // If selectionStart not manually set, caret is automatically  positioned to end of selection.
      self.selectionStart = start + str.length;
      self.selectionEnd = start + str.length;
      // If scrollTop not set to old value, textarea's vertical scrolling position automatically reset to its top.
      self.scrollTop = old_scroll_top;

    // Unsupported browsers -- just append str.
    } else {
      self.value += str;
    }
  }
});
