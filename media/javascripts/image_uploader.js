function ImageUploader(form, destination, activator, password_form, tweet_input, notifier) {
  this.__form = form;
  this.__destination = destination;
  this.__activator = activator;
  this.__password_form = password_form;
  this.__tweet_input = tweet_input;
  this.__notifier = notifier;
  this.__stored_password_cookie = 'twitter_password_stored';

  this.__configure_password_form_submit();
  this.__configure_image_uploaded();
  this.__configure_activation();
}

ImageUploader.prototype.__configure_image_uploaded = function() {
  var self = this;
  this.__form.submit(function() {
    self.__form.find('[name=password]').val(self.__password);

    var callback = function() {
      self.__form.hide();
      self.__activator.show();
      self.__tweet_input.focus();

      var response = $(this).contents();
      if( self.__handle_upload_error(response.find('err')) ) return;
      self.__tweet_input.insertAtCaret(response.find('mediaurl').text());
    };
    // Don't bind form destination's onload callback at page load -- we want it
    // to fire only when the form is submitted, not at the initial page load.
    // Must also remove existing callbacks (if any) to prevent multiple callback
    // firings.
    self.__destination.unbind().load(callback);
    return true;
  });
}

// Returns true if error occurred, false otherwise.
ImageUploader.prototype.__handle_upload_error = function(error) {
  if(error.length == 0) return false;
  // Error 1001 == invalid username or password.
  if(error.attr('code') == '1001') this.__clear_stored_password();
  this.__notifier.notify_failure('Image upload failed: ' + error.attr('msg'));
  return true;
}

ImageUploader.prototype.__configure_activation = function() {
  var self = this;
  this.__activator.click(function() {
    self.__activator.hide();
    if(self.__is_password_stored()) self.__form.show();
    else                       self.__password_form.show();
  });
}

ImageUploader.prototype.__store_password = function() {
  this.__password = this.__password_form.find('[name=password]').val();
  // The same cookie is set in views.tweets.home, so remember to change its
  // value and name there if you do so here.
  $.cookie(this.__stored_password_cookie, 'true', {expires: 365});
}

ImageUploader.prototype.__configure_password_form_submit = function() {
  var self = this;
  this.__password_form.submit(function() {
    self.__store_password();
    self.__password_form.hide();
    self.__form.show();
    return false;
  });
}

ImageUploader.prototype.__is_password_stored = function() {
  return $.cookie(this.__stored_password_cookie) != null;
}

ImageUploader.prototype.__clear_stored_password = function() {
  this.__password = null;
  $.cookie(this.__stored_password_cookie, null); // Delete cookie.
}
