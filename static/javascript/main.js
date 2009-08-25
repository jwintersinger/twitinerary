$(document).ready(function() {
  new Twitinerary( $('#new-tweet'), new Notifier($('#notifier')) );
});

function Twitinerary(new_tweet_form, notifier) {
  this.__new_tweet_form = new_tweet_form;
  this.__notifier = notifier;
  var self = this;
  this.__new_tweet_form.submit(function() { return self.__on_new_tweet_submission(); });
}

Twitinerary.prototype.__set_tweet_datetime = function() {
  // Sets time to number of seconds since Unix epoch.
  this.__new_tweet_form.find('[name=datetime]').val( this.__calculate_tweet_datetime().getTime() / 1000.0 );
}

Twitinerary.prototype.__calculate_tweet_datetime = function() {
  var hour = this.__convert_24_based_hour_to_12_based_hour(
      parseInt(this.__new_tweet_form.find('[name=hour]').val(), 10),
      this.__new_tweet_form.find('[name=period]').val() );
  var minute = parseInt(this.__new_tweet_form.find('[name=minute]').val(), 10);
  var date = this.__parse_date(this.__new_tweet_form.find('[name=date]').val());
  return new Date(date[0],     // Year.
                  date[1] - 1, // Month -- oddly, 0-based.
                  date[2],     // Date.
                  hour, minute);
}

Twitinerary.prototype.__parse_date = function(date_str) {
  // Use negative indices to ensure continued operation in 8000 years or so.
  var l = date_str.length;
  var date  = parseInt(date_str.substring(l - 2, l),     10);
  var month = parseInt(date_str.substring(l - 4, l - 2), 10);
  var year  = parseInt(date_str.substring(0,     l - 4), 10);
  return [year, month, date];
}

Twitinerary.prototype.__convert_24_based_hour_to_12_based_hour = function(hour, period) {
  if(period == 'pm' && hour < 12)  hour += 12;
  if(period == 'am' && hour == 12) hour = 0;
  return hour;
}

Twitinerary.prototype.__on_new_tweet_submission = function() {
  this.__set_tweet_datetime();
  var self = this;
  $.ajax({url: '/tweets/new',
          type: 'POST',
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
