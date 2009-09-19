$(document).ready(function() {
  configure_console();
  handle_tabs_onload();
});

// Add dummy replacement for Firebug's console.log to prevent code that calls it
// from throwing an exception.
function configure_console() {
  if(!window.console) window.console = { log: function() { } };
}

function handle_tabs_onload() {
  var notifier = new Notifier('#notifier');
  var tabs = $('#tabs');

  tabs.tabs({load: function(event, ui) {
    var panel = $(ui.panel);

    var configure_tweet_editor = function() {
      var tweet_form = panel.find('.tweet-form');
      var tweet_input = tweet_form.find('[name=tweet]');
      new UrlShortener(panel, tweet_input, notifier);
      new ImageUploader(panel, tweet_input, notifier);
      return new Tweeter(panel, tweet_form, notifier);
    };

    var tabload_handlers = {
      new_tweet: function() {
        var tweeter = configure_tweet_editor();
        tweeter.add_submission_callback(function() { tweeter.reset(); });
      },

      edit_tweet: function() {
        var tweeter = configure_tweet_editor();
        tweeter.add_submission_callback(function() { tabs.tabs('remove', ui.index); });
      },

      view_tweets: function() {
        new TweetViewer(tabs, notifier);
        new DatetimeHumanizer();
      }
    };

    var tabload_handler = tabload_handlers[ui.tab.id.replace(/_tab$/, '')];
    // If tab has no ID associated with it, it must be an edit tab, since edit
    // tabs and panels are created dynamically by jQuery UI, rather than being
    // hardcoded in my markup.
    if(!tabload_handler) tabload_handler = tabload_handlers.edit_tweet;
    tabload_handler();
  }});
}
