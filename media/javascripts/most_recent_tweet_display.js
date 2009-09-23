MostRecentTweetDisplay = function() {
  $.getJSON('/tweets/most_recent/', function(data) {
    if(data.error) return;
    data.post_at = new Date(1000*data.post_at);
    $('#most-recent-tweet').text(data.tweet + ' at ' + data.post_at);
  });
}
