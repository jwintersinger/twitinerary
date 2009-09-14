function ImageUploader(form, destination, toggler, tweet_input, notifier) {
  this.__form = form;
  this.__destination = destination;
  this.__toggler = toggler;
  this.__tweet_input = tweet_input;
  this.__notifier = notifier;
  this.__configure_destination_onload();
  this.__configure_form_toggle();
}

ImageUploader.prototype.__configure_destination_onload = function() {
  var self = this;
  this.__form.submit(function() {
    var callback = function() {
      var response = $(this).contents();
      var err = response.find('err');
      if(err.length) {
        self.__notifier.notify_failure('Image upload failed: ' + err.attr('msg'));
        return;
      }
      self.__tweet_input.insertAtCaret(response.find('mediaurl').text());
      self.__form.hide();
      self.__toggler.show();
      self.__tweet_input.focus();
    };
    self.__destination.unbind().load(callback);
    return true;
  });
}

ImageUploader.prototype.__configure_form_toggle = function() {
  var self = this;
  this.__toggler.click(function() {
    self.__toggler.hide();
    self.__form.show();
  });
}
