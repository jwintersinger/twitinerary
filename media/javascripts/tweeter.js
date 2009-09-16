function Tweeter(new_tweet_form, notifier) {
  this.__new_tweet_form = $(new_tweet_form);
  this.__notifier = notifier;

  this.__update_date('today');
  this.__update_time();
  this.__configure_date_picker_onclick();

  var self = this;
  this.__new_tweet_form.submit(function() { return self.__on_new_tweet_submission(); });
}

// Day should be in ['today', 'tomorrow', 'another_day'].
Tweeter.prototype.__update_date = function(day) {
  var self = this;
  var set_today = function() {
    self.__post_at = new Date();
    // Just setting day and not time, so we want each time component to be 0.
    $.each(['Hours', 'Minutes', 'Seconds', 'Milliseconds'], function() {
      self.__post_at['set' + this](0);
    });
  };
  set_today();

  switch(day) {
    case 'today':
      break;
    case 'tomorrow':
      set_today();
      // Add 24 hours as opposed to 1 day, as this seems clearer -- adding a day
      // might result in non-existent days such as Sep. 31, but adding 24 hours
      // seems conceptually clearer. It likely doesn't matter.
      this.__post_at.setHours(self.__post_at.getHours() + 24);
      break;
    case 'another_day':
      this.__post_at.setYear(1337);
      break;
  }

  // Duplicates selector, but acceptable since this will be removed before production.
  $('#date-picker input').removeClass('active').filter('[name=' + day + ']').addClass('active');
}

Tweeter.prototype.__update_time = function() {
  var hours = this.__convert_24_based_hours_to_12_based_hours(
    parseInt(this.__new_tweet_form.find('[name=hours]').val(), 10),
    this.__new_tweet_form.find('[name=period]').val() );
  var minutes = parseInt(this.__new_tweet_form.find('[name=minutes]').val(), 10);
  if(minutes < 0 || minutes > 59) minutes = 0;

  this.__post_at.setHours(hours);
  this.__post_at.setMinutes(minutes);
}

Tweeter.prototype.__put_post_at_in_form = function() {
  this.__update_time(); // Date already updated when (or if) corresponding button clicked.
  // Set to number of seconds since Unix epoch. Divide by 0 to convert from ms to s.
  this.__new_tweet_form.find('[name=post_at]').val( this.__post_at.getTime() / 1000.0 );
  console.log(this.__post_at);
}

Tweeter.prototype.__configure_date_picker_onclick = function() {
  var self = this;
  $('#date-picker input').click(function() {
    self.__update_date(this.name);
    console.log(self.__post_at);
  });
}

Tweeter.prototype.__convert_24_based_hours_to_12_based_hours = function(hours, period) {
  if(period == 'pm' && hours < 12)  hours += 12;
  if(period == 'am' && hours == 12) hours = 0;
  if(hours < 0 || hours > 23) hours = 0;
  return hours;
}

Tweeter.prototype.__on_new_tweet_submission = function() {
  this.__put_post_at_in_form();
  var self = this;
  $.ajax({url: this.__new_tweet_form[0].action,
          type: this.__new_tweet_form[0].method,
          data: this.__new_tweet_form.serialize(),
          success: function(response, status) {
            console.log([response, status]);
            self.__notifier.notify_success(response);
          },
          error: function(xhr, status, error) {
            console.log([xhr, status, error]);
            self.__notifier.notify_failure(xhr.responseText);
          } });
  return false;
}
