function AuthenticatedInitiator(initiator) {
  this.__initiator = initiator;
  this.__configure_tabs();
  this.__tweet_edit_state = new TweetEditState();
  this.__configure_tweet_manipulator();
  this.__next_scheduled_tweet = new NextScheduledTweet(this.__initiator, this.__tweet_manipulator);
}

AuthenticatedInitiator.prototype.__configure_tabs = function() {
  this.__tabs = $('#tabs');
  var self = this;
  this.__tabs.tabs({
    // Cache contents of tabs so they aren't reloaded when tab is switched to.
    // Otherwise, contents of forms will be lost when switching away from and
    // then back to a tab (not to mention that an unnecessary network request
    // will be performed, too).
    cache: true,
    load: function(event, ui) {
      return self.__on_tab_load(ui);
    },
    show: function(event, ui) {
      return self.__on_tab_show(ui);
    }
  });

  // Allow tabs to be dragged and dropped.
  this.__tabs.find('.ui-tabs-nav').sortable({axis: 'x'});
}

AuthenticatedInitiator.prototype.__get_tab_name = function(tab_id) {
  return tab_id.replace(/_tab$/, '');
}

AuthenticatedInitiator.prototype.__on_tab_show = function(ui) {
  // "View Tweets" tab must be reloaded to reflect the latest Tweets
  // added, edited, or deleted -- don't want its contents cached.
  // TODO: when first loaded and contents aren't already cached, tab is
  // loaded twice.
  if(this.__get_tab_name(ui.tab.id) == 'view_tweets')
    this.__tabs.tabs('load', this.__tabs.tabs('option', 'selected'));
}

AuthenticatedInitiator.prototype.__get_tabload_handlers = function(ui) {
  var self = this;
  var panel = $(ui.panel);

  var configure_tweet_editor = function() {
    var tweeter = new Tweeter(panel, self.__initiator.notifier);
    var tweet_input = tweeter.get_tweet_input();
    new UrlShortener(panel, tweet_input, self.__initiator.notifier);
    new ImageUploader(panel, tweet_input, self.__initiator.notifier);
    return tweeter;
  };

  var tabload_handlers = {
    new_tweet: function() {
      var tweeter = configure_tweet_editor();
      tweeter.add_submission_callback(function() {
        tweeter.reset();
        self.__next_scheduled_tweet.refresh();
      });
    },

    edit_tweet: function() {
      var tweeter = configure_tweet_editor();
      var key = tweeter.get_key();
      self.__tweet_edit_state.add_being_edited(key, panel.attr('id'));

      var editing_complete = function() {
        self.__tabs.tabs('remove', ui.index);
        self.__tweet_edit_state.remove_being_edited(key);
        self.__next_scheduled_tweet.refresh();
      };
      tweeter.add_submission_callback(editing_complete);
      tweeter.get_tweet_form().find('[name=cancel]').click(editing_complete);
    },

    view_tweets: function() {
      self.__tweet_manipulator.configure_handlers();
    }
  };

  // If tab has no ID associated with it, it must be an edit tab, since edit
  // tabs and panels are created dynamically by jQuery UI, rather than being
  // hardcoded in my markup.
  // Note that "default" is reserved name -- triggers error in Chrome but not Firefox. Use
  // "default_handler" instead.
  tabload_handlers.default_handler = tabload_handlers.edit_tweet;

  return tabload_handlers;
}

AuthenticatedInitiator.prototype.__configure_tweet_manipulator = function() {
  this.__tweet_manipulator = new TweetManipulator(this.__tabs,
    this.__initiator.notifier, this.__tweet_edit_state);

  var self = this;
  this.__tweet_manipulator.add_delete_callback(function() {
    // Reload "View Tweets" tab when Tweet deleted; note that this is not
    // necessary when tab is not selected, for it will be automatically
    // reloaded when it is switched to.
    self.__tabs.tabs('reload_if_selected', '#View_Tweets');
    self.__next_scheduled_tweet.refresh();
  });
}

AuthenticatedInitiator.prototype.__on_tab_load = function(ui) {
  this.__initiator.content_changed(); // Default actions for every tab.

  var tabload_handlers = this.__get_tabload_handlers(ui);
  var tab_name = this.__get_tab_name(ui.tab.id);
  (tabload_handlers[tab_name] || tabload_handlers.default_handler)();
}
