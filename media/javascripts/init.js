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

  $('#tabs').tabs({load: function(event, ui) {
    var onloads = {
      schedule_tweet: function() {
        var new_tweet_form = $('#new-tweet');
        var tweet_input = new_tweet_form.find('[name=tweet]');

        new Tweeter(new_tweet_form, notifier);
        new UrlShortener(tweet_input, notifier);
        new ImageUploader(tweet_input, notifier);
      },

      view_tweets: function() {
        new DatetimeHumanizer();
      }
    };
    onloads[ui.tab.id]();
  }});
}
