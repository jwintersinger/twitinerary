function Notifier(container) {
  this.__container = container;
}

Notifier.prototype.notify_success = function(msg) {
  this.__notify(msg, '#00ff00');
}

Notifier.prototype.__notify = function(msg, colour) {
  console.log(msg);
  var out = this.__container.find('p');
  out.text(msg);
  this.__container.css('backgroundColor', colour);
  var speed = 'normal';
  this.__container.slideDown(speed, function() {
      var self = $(this);
      window.setTimeout(function() { self.slideUp(speed); }, 2000);
  });
}
