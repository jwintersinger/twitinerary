$(document).ready(function() {
  var new_tweet_form = $('#new-tweet');
  var tweet_input = new_tweet_form.find('[name=tweet]');
  var notifier = new Notifier($('#notifier'));
  new Tweeter(new_tweet_form, notifier);
  new UrlShortener($('#url-shortener'), '[name=long_url]', tweet_input, notifier);
  new ImageUploader($('#image-uploader'), $('#image-uploader-dest'), tweet_input, notifier);
});