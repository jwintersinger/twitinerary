function Tweeter(new_tweet_form, notifier) {
  this.__new_tweet_form = $(new_tweet_form);
  this.__notifier = notifier;

  this.__configure_date_picker_calendar();
  this.__configure_day_chooser_onclick();

  var self = this;
  this.__new_tweet_form.submit(function() { return self.__on_new_tweet_submission(); });
}

// Defaults to today. delta, if provided, indicates how many days +-today.
Tweeter.prototype.__update_date = function(delta) {
  if(!delta) delta = 0;
  this.__post_at = new Date(); // Defaults to today.
  // Just setting day and not time, so we want each time component to be 0.
  this.__post_at.setHours(this.__post_at.getHours() + 24*delta);
  this.__post_at.setMinutes(0);
  this.__post_at.setSeconds(0);
  this.__post_at.setMilliseconds(0);
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
  this.__update_time(); // Date already updated when corresponding button clicked.
  // Set to number of seconds since Unix epoch. Divide by 1000 to convert from ms to s.
  this.__new_tweet_form.find('[name=post_at]').val( this.__post_at.getTime() / 1000.0 );
}

Tweeter.prototype.__configure_day_chooser_onclick = function() {
  var self = this;
  var day_choosers = $('#day-chooser input');
  day_choosers.click(function() {
    day_choosers.removeClass('active').filter('[name=' + this.name + ']').addClass('active');
  });
  day_choosers.filter('[name!=another_day]').click(function() {
    self.__date_picker_calendar.hide();
    self.__update_date(this.name == 'tomorrow' ? 1 : 0);
    self.__date_picker_calendar.datepicker('setDate', self.__post_at);
  });
  day_choosers.filter('[name=another_day]').click(function() {
    self.__date_picker_calendar.show();
  });
  day_choosers.filter('[name=today]').click(); // Default day is today.
}

Tweeter.prototype.__configure_date_picker_calendar = function() {
  var self = this;
  var on_select = function(date) {
    date = $.datepicker.parseDate('mm/dd/yy', date);
    self.__post_at = date;
    $(this).hide();
  };
  this.__date_picker_calendar = $('#date-picker-calendar').hide().
    datepicker({onSelect: on_select});
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
