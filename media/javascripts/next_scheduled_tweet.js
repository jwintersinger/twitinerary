NextScheduledTweet = function() {
  this.__container = $('#next-scheduled-tweet');
  // Container only present when user is authenticated.
  if(!this.__container.length) return;

  this.refresh();
}

NextScheduledTweet.prototype.refresh = function() {
  var self = this;
  $.getJSON('/tweets/next_scheduled/', function(data) {
    if(data.error_code) {
      if(data.error_code == 'no_tweets_scheduled') self.__set_text('');
      return;
    }
    data.post_at = new Date(1000*data.post_at);
    self.__set_text(data.tweet + ' at ' + data.post_at);
  });
}

NextScheduledTweet.prototype.__set_text = function(new_text) {
  // Only change text if text is different from existing.
  if(this.__container.text() == new_text) return;

  var speed = 1000;
  // jQuery is smart about fading out empty elements -- if container is empty
  // (as it will be when no Tweets are scheduled), it will "fade out" instantly,
  // meaning that the fadeOut callback will be executed without any delay.
  this.__container.fadeOut(speed, function() {
    $(this).text(new_text).fadeIn(speed);
  });
}
