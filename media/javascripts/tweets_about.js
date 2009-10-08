function TweetsAbout(term, callback) {
  $.getJSON('http://search.twitter.com/search.json?callback=?', {'q': term}, callback);
}
