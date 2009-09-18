function ImageUploader(container, tweet_input, notifier) {
  this.__tweet_input            = $(tweet_input);
  this.__notifier               = notifier;
  this.__form                   = container.find('.image-uploader');
  this.__activator              = container.find('.image-uploader-activator');
  this.__password_form          = container.find('.twitter-password');
  this.__stored_password_cookie = 'twitter_password_stored';

  this.__configure_password_form_submit();
  this.__configure_destination();
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
    else                            self.__password_form.show();
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

ImageUploader.prototype.__configure_destination = function() {
  // iframe's name must be set *before* it is inserted into the DOM. Previously,
  // I had an iframe with no name attribute set in my template, and I set its
  // name property dynamically in this method. When I did this,
  // though everything will seem proper (this.__destination.attr('name')
  // returned the expected value, which was also the value of
  // this.__form.attr('target')), the form submission opened in a new window
  // rather than the target iframe. However, when the name attribute is set on
  // the iframe before it is inserted into the DOM, everything works as
  // expected, with the form loaded into the invisible iframe.
  //
  // 'name' attribute on target iframe must be unique, or Firefox will throw a
  // cryptic NS_ERROR_FAILURE error. As there may be multiple copies of the iframe
  // in the DOM (one for "new Tweet" tab, one for each of any "edit Tweet" tabs),
  // we can't simply have a single iframe in our template with a statically-set
  // name.

  this.__destination_class      = 'image-uploader-dest';
  var destination_prefix = this.__destination_class + '-';

  var index = 0;
  do {
    var destination_name = destination_prefix + index++;
  } while($('.' + this.__destination_class + '[name=' + destination_name + ']').length > 0);

  this.__destination = $('<iframe></iframe>').attr('class', this.__destination_class).
    attr('name', destination_name).css('display', 'none').insertBefore(this.__form);
  this.__form.attr('target', destination_name);
}
