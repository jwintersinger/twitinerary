function UnauthenticatedInitiator(initiator) {
  new TweetsAbout('bonner', function(data) {
    var num_tweets = 3;
    var container = $('#tweets-about-us');

    for(var i = 0; i < num_tweets; i++) {
      var tweet = data.results[i];
      container.append('<li><a href="http://twitter.com/"' + tweet.from_user +
        '>@' + tweet.from_user + '</a>: ' + tweet.text + ' at ' + tweet.created_at + '</li>');
    }
  });
  initiator.content_changed();
}

