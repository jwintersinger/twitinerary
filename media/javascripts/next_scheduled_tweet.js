NextScheduledTweet = function() {
  var container = $('#next-scheduled-tweet');
  if(!container.length) return;

  $.getJSON('/tweets/next_scheduled/', function(data) {
    if(data.error) return;
    data.post_at = new Date(1000*data.post_at);
    container.text(data.tweet + ' at ' + data.post_at);
  });
}
