function Tweeter(container, notifier) {
  // Note that when selecting elements, we work by identifying the element by
  // its class within the container, rather than simply selecting by an ID. The
  // reason for this is that multiple such elements may be present in the DOM --
  // the contents of each tab exist within the DOM concurrently. As such,
  // multiple instances of the Tweet form may be present: the single
  // "new Tweet" tab as well as multiple possible "edit Tweet" tabs.
  this.__notifier = notifier;
  this.__submission_callbacks = [];

  this.__set_elements(container);
  this.__configure_date_picker_calendar();
  this.__configure_tweet_submission();
  this.__configure_day_choosers();
  this.__initialize_editor();
}

Tweeter.prototype.get_tweet_form = function() {
  return this.__el.tweet_form;
}

Tweeter.prototype.get_key = function() {
  return Tweeter.extract_key(this.__el.tweet_form);
}

Tweeter.extract_key = function(form) {
  return $(form).find('[name=key]').val();
}

Tweeter.prototype.get_tweet_input = function() {
  return this.__el.tweet_form.find('[name=tweet]');
}

// Callbacks called on successful submission of Tweet.
Tweeter.prototype.add_submission_callback = function(callback) {
  this.__submission_callbacks.push(callback);
}

Tweeter.prototype.reset = function() {
  this.__el.tweet_form[0].reset();
  // reset() call does not reset hidden fields, so must do so manually.
  this.__el.post_at.val('');
  this.__initialize_editor();
}

Tweeter.prototype.__initialize_editor = function() {
  this.__set_initial_datetime();
  this.__label_date_picker_activator();
  this.get_tweet_input().focus();
  this.__tweet_char_counter = new TweetCharCounter(this);
}

// Common references to elements used multiple times.
Tweeter.prototype.__set_elements = function(container) {
  this.__el = {
    container:  container,
    tweet_form: container.find('.tweet-form')
  };
  var self = this;
  $.each(['post_at', 'hours', 'period', 'minutes'], function() {
    self.__el[this] = self.__el.tweet_form.find('[name=' + this + ']');
  });
}

Tweeter.prototype.__configure_date_picker_calendar = function() {
  var self = this;
  var on_select = function(date) {
    date = $.datepicker.parseDate('mm/dd/yy', date);
    self.__post_at = date;
    self.__label_date_picker_activator();
    $(this).hide();
  };
  this.__date_picker_calendar = this.__el.container.find('.date-picker-calendar').hide().
    datepicker({onSelect: on_select});
}

Tweeter.prototype.__package_time_into_form = function() {
  this.__update_time(); // Date already updated when corresponding button clicked.
  // Set to number of seconds since Unix epoch. Divide by 1000 to convert from ms to s.
  this.__el.post_at.val( this.__post_at.getTime() / 1000.0 );
}

Tweeter.prototype.__configure_tweet_submission = function() {
  var self = this;
  this.__el.tweet_form.submit(function() {
    self.__package_time_into_form();

    if(self.__post_at < new Date()) {
      self.__notifier.notify_failure('Your Tweet is scheduled in the past.');
      return false;
    }
    if(self.__tweet_char_counter.is_tweet_too_long()) {
      self.__notifier.notify_failure('Your Tweet is too long.');
      return false;
    }

    $.ajax({url: self.__el.tweet_form[0].action,
            type: self.__el.tweet_form[0].method,
            data: self.__el.tweet_form.serialize(),
            success: function(response, status) {
              self.__notifier.notify_success(response);
              $.each(self.__submission_callbacks, function() { this(); });
            },
            error: function(xhr, status, error) {
              self.__notifier.notify_failure(xhr.responseText);
            } });
    return false;
  });
}

Tweeter.prototype.__label_date_picker_activator = function(date) {
  if(!this.__date_picker_activator_default_value)
    this.__date_picker_activator_default_value = this.__date_picker_activator.attr('value');

  if(DateCalculator.is_another_day(this.__post_at))
    var label = $.datepicker.formatDate('M. d', this.__post_at);
  else
    var label = this.__date_picker_activator_default_value;
  this.__date_picker_activator.attr('value', label);
}

Tweeter.prototype.__configure_day_choosers = function() {
  var self = this;
  this.__day_choosers = this.__el.container.find('.day-chooser input');

  this.__day_choosers.click(function() {
    self.__indicate_active_day_chooser(this.name);
  });

  this.__day_choosers.filter('[name!=another_day]').click(function() {
    self.__date_picker_calendar.hide();
    self.__date_picker_calendar.datepicker('setDate', self.__post_at);
    self.__make_time_now(this.name == 'tomorrow' ? 24 : 0);
    self.__label_date_picker_activator();
  });

  this.__date_picker_activator = this.__day_choosers.filter('[name=another_day]');
  // Only set default value on first call. Afterward, when form is being reset,
  // value of the button may already have been changed to a non-default value.
  this.__date_picker_activator.click(function() {
    self.__date_picker_calendar.show();
  });
}

// Sets post_at to (now + hours_delta). hours_delta defaults to 0. Makes no
// effort to preserve time-related information.
Tweeter.prototype.__make_time_now = function(hours_delta) {
  if(!hours_delta) hours_delta = 0;
  this.__post_at = new Date();
  this.__post_at.setHours(this.__post_at.getHours() + hours_delta);
}

Tweeter.prototype.__calculate_initial_time = function() {
  var post_at = this.__el.post_at.val();
  if(post_at) {
    this.__post_at = new Date(1000*parseInt(post_at, 10));
  } else {
    this.__make_time_now(1); // Default time is 1 hour from now.
  } 
}

Tweeter.prototype.__set_initial_datetime = function() {
  this.__calculate_initial_time();

  // Minutes.
  var minutes = this.__post_at.getMinutes().toString();
  if(minutes.length < 2) minutes = '0' + minutes;
  this.__el.minutes.val(minutes);

  // Hours.
  var hour_components = TimeCalculator.convert_24_based_hours_to_12_based_hours(this.__post_at.getHours());
  this.__el.hours.val(hour_components.hours);
  this.__el.period.val(hour_components.period);

  // Day.
  if(DateCalculator.is_today(this.__post_at))         var day = 'today';
  else if(DateCalculator.is_tomorrow(this.__post_at)) var day = 'tomorrow';
  else                                                var day = 'another_day';
  this.__label_date_picker_activator();
  this.__indicate_active_day_chooser(day);

  // This must be done last, for the datepicker code somehow obliterates all
  // time-related information in the process of setting the calendar's date,
  // setting this._post_at's time to 00:00:00.
  this.__date_picker_calendar.datepicker('setDate', this.__post_at);
}

Tweeter.prototype.__update_time = function() {
  var hours = TimeCalculator.convert_12_based_hours_to_24_based_hours(
    parseInt(this.__el.hours.val(), 10),
    this.__el.period.val() );
  var minutes = parseInt(this.__el.minutes.val(), 10);
  if(minutes < 0 || minutes > 59) minutes = 0;

  this.__post_at.setHours(hours);
  this.__post_at.setMinutes(minutes);
}

Tweeter.prototype.__indicate_active_day_chooser = function(name) {
  this.__day_choosers.removeClass('active').filter('[name=' + name + ']').addClass('active');
}



function TweetCharCounter(tweeter) {
  this.__max_length = 140;
  this.__char_counter = tweeter.get_tweet_form().find('.tweet-char-counter');
  this.__tweet_input = tweeter.get_tweet_input();

  this.__reset();
}

TweetCharCounter.prototype.__reset = function() {
  this.__char_counter.text(this.__max_length);
  this.__char_counter.css('color', '#000');

  var self = this;
  // Trigger keyup(), as must __recalculate() on load so that character count
  // is updated appropriately if editing existing Tweet.
  this.__tweet_input.keyup(function(event) { self.__recalculate(); }).keyup();
}

TweetCharCounter.prototype.__recalculate = function() {
  var tweet_length = this.__tweet_input.val().length;
  var chars_remaining = this.__max_length - tweet_length;
  this.__char_counter.text(this.__max_length - tweet_length);
  this.__change_colour(tweet_length);
}

TweetCharCounter.prototype.__change_colour = function(tweet_length) {
  var max = 255;
  var red = max*(tweet_length / this.__max_length);
  if(red > max) red = max;

  this.__char_counter.css('color', '#' + Math.round(red).toString(16) + '0000');
}

TweetCharCounter.prototype.is_tweet_too_long = function() {
  return this.__tweet_input.val().length > this.__max_length;
}




DateCalculator = {
  are_same_day: function(a, b) {
    return a.getDate()     == b.getDate() &&
           a.getMonth()    == b.getMonth() &&
           a.getFullYear() == b.getFullYear();
  },

  is_today: function(date) {
    return this.are_same_day(new Date(), date);
  },

  is_tomorrow: function(date) {
    var tomorrow = new Date((new Date()).getTime() + 1000*24*3600);
    return this.are_same_day(tomorrow, date);
  },

  is_another_day: function(date) {
    return !(this.is_today(date) || this.is_tomorrow(date));
  }
}



TimeCalculator = {
  convert_12_based_hours_to_24_based_hours: function(hours, period) {
    if(period == 'pm' && hours < 12)       hours += 12;
    else if(period == 'am' && hours == 12) hours = 0;
    if(hours < 0 || hours > 23)            hours = 0;
    return hours;
  },

  convert_24_based_hours_to_12_based_hours: function(hours) {
    var period = 'am';
    if(hours == 0)       { hours = 12; }
    else if(hours > 12) { hours -= 12; period = 'pm'; }
    return {hours: hours, period: period};
  }
}
