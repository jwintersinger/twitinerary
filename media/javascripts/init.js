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

  tabs.tabs({
    // Cache contents of tabs so they aren't reloaded when tab is switched to.
    // Otherwise, contents of forms will be lost when switching away from and
    // then back to a tab (not to mention that an unnecessary network request
    // will be performed, too).
    cache: true,
    load: function(event, ui) {
      return on_tab_load(ui, tabs, notifier);
    },
    show: function(event, ui) {
      // "View Tweets" tab must be reloaded to reflect the latest Tweets
      // added, edited, or deleted -- don't want its contents cached.
      // TODO: when first loaded and contents aren't already cached, tab is
      // loaded twice.
      if(get_tab_name(ui.tab.id) == 'view_tweets')
        tabs.tabs('load', tabs.tabs('option', 'selected'));
    }
  });
}

function get_tab_name(tab_id) {
  return tab_id.replace(/_tab$/, '');
}

function on_tab_load(ui, tabs, notifier) {
  var tab_name = get_tab_name(ui.tab.id);
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
      var close_tab = function() { tabs.tabs('remove', ui.index); };
      tweeter.add_submission_callback(close_tab);
      tweeter.get_tweet_form().find('[name=cancel]').click(close_tab);
    },

    view_tweets: function() {
      new TweetViewer(tabs, notifier);
      new DatetimeHumanizer();
    }
  };

  var tabload_handler = tabload_handlers[tab_name];
  // If tab has no ID associated with it, it must be an edit tab, since edit
  // tabs and panels are created dynamically by jQuery UI, rather than being
  // hardcoded in my markup.
  if(!tabload_handler) tabload_handler = tabload_handlers.edit_tweet;
  tabload_handler();
}
