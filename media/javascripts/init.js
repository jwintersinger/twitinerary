$(document).ready(function() {
  var new_tweet_form = $('#new-tweet');
  var notifier = new Notifier($('#notifier'));
  new Tweeter(new_tweet_form, notifier);
  new UrlShortener($('#url-shortener'), '[name=long_url]', new_tweet_form.find('[name=tweet]'), notifier);
});
