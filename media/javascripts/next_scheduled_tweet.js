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
      if(data.error_code == 'no_tweets_scheduled') self.__clear();
      return;
    }
    self.__set_content(data.content);
  });
}

NextScheduledTweet.prototype.__set_content = function(new_content) {
  // Only change text if text is different from existing.
  if(this.__container.data('content_before_date_humanization') == new_content) return;

  var self = this;
  var update_content = function(content) {
    self.__container.html(content);
    // Necessary for "only change if text different" check to work, as we alter
    // the HTML in transforming the date.
    self.__container.data('content_before_date_humanization', content);
    self.__humanize_time_until_next_tweet();
  };

  // Skip all fading animations on first load.
  if(this.__initial_load) {
    update_content(new_content);
    this.__initial_load = false;
    return;
  }

  var fade_in_speed = 1000;
  // Set to 0 for instantaneous "fade out" when existing contents are empty.
  var fade_out_speed = this.__container.html() == '' ? 0 : fade_in_speed;
  // Fade to 1% opacity rather than fade out completely, as, if the container is
  // empty, jQuery will detect that nothing in it is visible on the page and
  // thus not fade it out. Since it is never faded out, the fade-in call
  // completes instantly without actually fading anything in, meaning that if
  // the container starts empty (i.e., no Tweets are scheduled) and then has its
  // text changed (i.e., a Tweet is scheduled), that Tweet will appear instantly
  // rather than fading in.
  this.__container.fadeTo(fade_out_speed, 0.01, function() {
    update_content(new_content);
    $(this).fadeTo(fade_in_speed, 1.0);
  });
}

NextScheduledTweet.prototype.__clear = function() {
  this.__set_content('');
}

NextScheduledTweet.prototype.__humanize_time_until_next_tweet = function() {
  var time_container = this.__container.find('.datetime');
  var next_tweet_time = new Date(1000*parseInt(time_container.text(), 10));
  time_container.text(distance_between_times(new Date(), next_tweet_time));
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
