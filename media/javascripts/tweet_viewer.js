function TweetViewer(tabs, notifier) {
  this.__tabs = $(tabs);
  this.__notifier = notifier;
  this.__delete_forms = $('.tweet-deleter');

  this.__configure_deletion();
}

TweetViewer.prototype.__configure_deletion = function() {
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
