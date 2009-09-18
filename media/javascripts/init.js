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
    var tabload_handlers = {
      new_tweet: function() {
        var new_tweet_form = $('#new-tweet');
        var tweet_input = new_tweet_form.find('[name=tweet]');

        new Tweeter(new_tweet_form, notifier);
        new UrlShortener(tweet_input, notifier);
        new ImageUploader(tweet_input, notifier);
      },

      edit_tweet: function() {
        console.log('In editor.');
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
