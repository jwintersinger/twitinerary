$(document).ready(function() {
  var new_tweet_form = $('#new-tweet');
  new_tweet_form.submit(function() { return on_new_tweet_submission(new_tweet_form);  });
});

function set_tweet_datetime() {
  // Sets time to number of seconds since Unix epoch.
  $('#new-tweet [name=datetime]').val( calculate_tweet_datetime().getTime() / 1000.0 );
}

function calculate_tweet_datetime() {
  var form = $('#new-tweet');
  var hour = convert_24_based_hour_to_12_based_hour(
      parseInt(form.find('[name=hour]').val(), 10),
      form.find('[name=period]').val() );
  var minute = parseInt(form.find('[name=minute]').val(), 10);
  var date = parse_date(form.find('[name=date]').val());
  return new Date(date[0],     // Year.
                  date[1] - 1, // Month -- oddly, 0-based.
                  date[2],     // Date.
                  hour, minute);
}

function parse_date(date_str) {
  // Use negative indices to ensure continued operation in 8000 years or so.
  var l = date_str.length;
  var date  = parseInt(date_str.substring(l - 2, l),     10);
  var month = parseInt(date_str.substring(l - 4, l - 2), 10);
  var year  = parseInt(date_str.substring(0,     l - 4), 10);
  return [year, month, date];
}

function convert_24_based_hour_to_12_based_hour(hour, period) {
  if(period == 'pm' && hour < 12)  hour += 12;
  if(period == 'am' && hour == 12) hour = 0;
  return hour;
}

function on_new_tweet_submission(form) {
  set_tweet_datetime();
  $.ajax({url: '/tweets/new',
          type: 'POST',
          data: $(form).serialize(),
          success: function() {
            console.log('Hooray!');
          },
          error: function() {
            console.log('Oh, dear.');
          }});
  return false;
}
