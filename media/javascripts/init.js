$(document).ready(function() {
  var new_tweet_form = $('#new-tweet');
  new Tweeter( new_tweet_form, new Notifier($('#notifier')) );
  new UrlShortener($('#url-shortener'), '[name=long_url]', new_tweet_form.find('[name=tweet]'));
});
