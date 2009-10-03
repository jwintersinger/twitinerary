NextScheduledTweet = function() {
  this.refresh();
}

NextScheduledTweet.prototype.refresh = function() {
  var container = $('#next-scheduled-tweet');
  // Container only present when user is authenticated.
  if(!container.length) return;

  $.getJSON('/tweets/next_scheduled/', function(data) {
    if(data.error_code) {
      if(data.error_code == 'no_tweets_scheduled') container.text('');
      return;
    }
    data.post_at = new Date(1000*data.post_at);
    container.text(data.tweet + ' at ' + data.post_at);
  });
}
