function Notifier(container) {
  this.__container = container;
  this.__slide_speed = 'normal';
  var self = this;
  $('#dismiss-notification').click(function() {
      self.__dismiss();
  });
}

Notifier.prototype.notify_success = function(msg) {
  this.__notify(msg, '#00ff00', true);
}

Notifier.prototype.notify_failure = function(msg) {
  this.__notify(msg, '#ff0000', false);
}

Notifier.prototype.__notify = function(msg, colour, auto_dismiss) {
  console.log('[' + colour + '] ' + msg);

  this.__container.css('backgroundColor', colour);
  var out = this.__container.find('p');
  out.text(msg);

  var self = this;
  this.__container.slideDown(this.__slide_speed, function() {
    if(auto_dismiss) window.setTimeout(function() { self.__dismiss(); }, 2000);
  });
}

Notifier.prototype.__dismiss = function() {
  this.__container.slideUp(this.__slide_speed);
}
