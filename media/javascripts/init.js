$(document).ready(function() {
  configure_console();
  handle_tabs_onload();
});

// Add dummy replacement for Firebug's console.log to prevent code that calls it
// from throwing an exception.
function configure_console() {
  if(!window.console) window.console = { log: function() { } };
}

function configure_tweet_manipulators(tabs, notifier, tweet_edit_state, next_scheduled_tweet) {
  var tweet_manipulator = new TweetManipulator(tabs, notifier, tweet_edit_state);

  $('.tweet-editor').live('submit', function(event) {
    return tweet_manipulator.on_init_edit(event.target);
  });
  $('.tweet-deleter').live('submit', function(event) {
    return tweet_manipulator.on_delete(event.target);
  });
  tweet_manipulator.add_delete_callback(function() {
    // Reload "View Tweets" tab when Tweet deleted; note that this is not
    // necessary when tab is not selected, for it will be automatically
    // reloaded when it is switched to.
    tabs.tabs('reload_if_selected', '#View_Tweets');
    next_scheduled_tweet.refresh();
  });
}

function handle_tabs_onload() {
  var notifier = new Notifier('#notifier');
  var tweet_edit_state = new TweetEditState();
  var tabs = $('#tabs');
  var next_scheduled_tweet = new NextScheduledTweet();
  configure_tweet_manipulators(tabs, notifier, tweet_edit_state, next_scheduled_tweet);

  tabs.tabs({
    // Cache contents of tabs so they aren't reloaded when tab is switched to.
    // Otherwise, contents of forms will be lost when switching away from and
    // then back to a tab (not to mention that an unnecessary network request
    // will be performed, too).
    cache: true,
    load: function(event, ui) {
      return on_tab_load(ui, tabs, notifier, tweet_edit_state, next_scheduled_tweet);
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
  // Allow tabs to be dragged and dropped.
  tabs.find('.ui-tabs-nav').sortable({axis: 'x'});
}

function get_tab_name(tab_id) {
  return tab_id.replace(/_tab$/, '');
}

function on_tab_load(ui, tabs, notifier, tweet_edit_state, next_scheduled_tweet) {
  var tab_name = get_tab_name(ui.tab.id);
  var panel = $(ui.panel);
  configure_explanations();
  new DatetimeHumanizer();

  var configure_tweet_editor = function() {
    var tweeter = new Tweeter(panel, notifier);
    var tweet_input = tweeter.get_tweet_input();
    new UrlShortener(panel, tweet_input, notifier);
    new ImageUploader(panel, tweet_input, notifier);
    return tweeter;
  };

  var tabload_handlers = {
    new_tweet: function() {
      var tweeter = configure_tweet_editor();
      tweeter.add_submission_callback(function() {
        tweeter.reset();
        next_scheduled_tweet.refresh();
      });
    },

    edit_tweet: function() {
      var tweeter = configure_tweet_editor();
      var key = tweeter.get_key();
      tweet_edit_state.add_being_edited(key, panel.attr('id'));

      var editing_complete = function() {
        tabs.tabs('remove', ui.index);
        tweet_edit_state.remove_being_edited(key);
        next_scheduled_tweet.refresh();
      };
      tweeter.add_submission_callback(editing_complete);
      tweeter.get_tweet_form().find('[name=cancel]').click(editing_complete);
    },

    // Must not omit, or edit_tweet will be used by default.
    view_tweets: function() { }
  };

  var tabload_handler = tabload_handlers[tab_name];
  // If tab has no ID associated with it, it must be an edit tab, since edit
  // tabs and panels are created dynamically by jQuery UI, rather than being
  // hardcoded in my markup.
  if(!tabload_handler) tabload_handler = tabload_handlers.edit_tweet;
  tabload_handler();
}

function configure_explanations() {
  $('.explanation').each(function() {
    var e = $(this);
    var tooltip_text = e.text();
    e.text('?');
    e.simpletip({
      content: tooltip_text,
      // When fixed=false, buggy behaviour regarding "flashing" tooltip is exhibited
      // if mouse is moved rapidly out of tooltip-triggering element.
      fixed: true,
      // Default class "active" conflicts with my already-defined class of same name.
      activeClass: 'active-tooltip'
    });
  });
}
