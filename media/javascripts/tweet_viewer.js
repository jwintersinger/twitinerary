function TweetViewer(tabs, notifier) {
  this.__tabs = $(tabs);
  this.__notifier = notifier;
  this.__edit_forms = $('.tweet-editor');
  this.__delete_forms = $('.tweet-deleter');

  this.__configure_edit_listeners();
  this.__configure_delete_listeners();
}

TweetViewer.prototype.__configure_edit_listeners = function() {
  var self = this;
  this.__edit_forms.submit(function(event) {
    var form = $(event.target);
    self.__tabs.tabs('add', event.target.action + '?' + form.serialize(), 'Edit tweet');
    return false;
  });
}

TweetViewer.prototype.__configure_delete_listeners = function() {
  var self = this;
  this.__delete_forms.submit(function(event) {
    var after_delete = function(success, message) {
      // Reload currently-selected tab.
      self.__tabs.tabs('load', self.__tabs.tabs('option', 'selected'));
      self.__notifier['notify_' + (success ? 'success' : 'failure')](message);
    };
    var form = event.target;
    $.ajax({
      url:  form.action,
      type: form.method,
      data: $(form).serialize(),
      success: function(response, status) { after_delete(true, response); },
      error: function(xhr, status, error) { after_delete(false, xhr.responseText); }
    });
    return false;
  });
}
