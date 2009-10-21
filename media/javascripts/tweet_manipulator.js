function TweetManipulator(tabs, notifier, tweet_edit_state) {
  this.__notifier = notifier;
  this.__tabs = tabs;
  this.__tweet_edit_state = tweet_edit_state;
  this.__delete_callbacks = [];
}

TweetManipulator.prototype.__on_init_edit = function(form) {
  var form = $(form);
  var key = TweetEditor.extract_key(form);
  if(this.__tweet_edit_state.is_being_edited(key)) {
    this.__tabs.tabs('select', '#' + this.__tweet_edit_state.get_edit_panel_id(key));
    return false;
  }

  this.__tabs.tabs('add', form.attr('action') + '?' + form.serialize(), 'Edit tweet');
  // Tab not automatically switched to after creation.
  this.__tabs.tabs('select', this.__tabs.tabs('length') - 1);
  return false;
}

TweetManipulator.prototype.__on_delete = function(form) {
  var form = $(form);
  var self = this;
  var after_delete = function(success, message) {
    self.__notifier['notify_' + (success ? 'success' : 'failure')](message);

    var key = TweetEditor.extract_key(form);
    self.__tabs.tabs('remove_by_selector', '#' + self.__tweet_edit_state.get_edit_panel_id(key));

    $.each(self.__delete_callbacks, function() { this(); });
  };

  $.ajax({
    url:  form.attr('action'),
    type: form.attr('method'),
    data: form.serialize(),
    success: function(response, status) { after_delete(true, response); },
    error: function(xhr, status, error) { after_delete(false, xhr.responseText); }
  });
  return false;
}

TweetManipulator.prototype.add_delete_callback = function(callback) {
  this.__delete_callbacks.push(callback);
}

TweetManipulator.prototype.configure_handlers = function() {
  var self = this;
  // Can't use jQuery's "live" manipulators, which prevent having to rebind handlers every time new
  // element created -- they don't support 'submit' events.
  // Must unbind first to remove handlers bound to elements that existed on past tab loads (i.e.,
  // the "next scheduled Tweet" widgets).
  $('.tweet-editor').unbind().submit(function(event) {
    return self.__on_init_edit(event.target);
  });
  $('.tweet-deleter').unbind().submit(function(event) {
    return self.__on_delete(event.target);
  });
}
