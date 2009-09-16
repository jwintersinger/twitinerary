$(document).ready(function() {
  configure_console();
  var new_tweet_form = $('#new-tweet');
  var tweet_input = new_tweet_form.find('[name=tweet]');

  var notifier = new Notifier('#notifier');
  new Tweeter(new_tweet_form, notifier);
  new UrlShortener(tweet_input, notifier);
  new ImageUploader(tweet_input, notifier);
});

// Add dummy replacement for Firebug's console.log to prevent code that calls it
// from throwing an exception.
function configure_console() {
  if(!window.console) window.console = { log: function() { } };
}

