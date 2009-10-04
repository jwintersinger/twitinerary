NextScheduledTweet = function() {
  this.__initial_load = true;
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
    self.__set_text('Next Tweet: ' + data.tweet + ' in ' +
      distance_between_times(new Date(), data.post_at) + '.');
  });
}

NextScheduledTweet.prototype.__set_text = function(new_text) {
  // Only change text if text is different from existing.
  if(this.__container.text() == new_text) return;

  // Skip all fading animations on first load.
  if(this.__initial_load) {
    this.__container.text(new_text);
    this.__initial_load = false;
    return;
  }

  var speed = 1000;
  // Fade to 1% opacity rather than fade out completely, as, if the container is
  // empty, jQuery will detect that nothing in it is visible on the page and
  // thus not fade it out. Since it is never faded out, the fade-in call
  // completes instantly without actually fading anything in, meaning that if
  // the container starts empty (i.e., no Tweets are scheduled) and then has its
  // text changed (i.e., a Tweet is scheduled), that Tweet will appear instantly
  // rather than fading in.
  this.__container.fadeTo(speed, 0.01, function() {
    $(this).text(new_text).fadeTo(speed, 1.0);
  });
}

function distance_between_times(a, b) {
  var amounts = [
    ['month',  30*24*60*60],
    ['week',   7*24*60*60],
    ['day',    24*60*60],
    ['hour',   60*60],
    ['minute', 60],
    ['second', 1],
  ];
  var delta = (b.getTime() - a.getTime()) / 1000; // in seconds.
  for(var i = 0; i < amounts.length; i++) {
    var period = amounts[i][0], amount = amounts[i][1];
    // If on last period (seconds), define time in it -- otherwise will fall out
    // of loop without defining time.
    if(amount > Math.abs(delta) && i != amounts.length - 1) continue;
    var num_periods = Math.round(delta / amount);
    return num_periods + ' ' + period + (Math.abs(num_periods) != 1 ? 's' : '');
  }
}
