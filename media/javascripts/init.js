$(document).ready(function() {
  new Initiator();
});

function Initiator() {
  this.notifier = new Notifier('#notifier');
  this.__configure_console();

  if($('#authenticator').hasClass('authenticated')) new AuthenticatedInitiator(this);
  else                                              new UnauthenticatedInitiator(this);
}

// To be called by client initiators whenever new content requiring that event handlers be
// bound, etc. is loaded.
Initiator.prototype.content_changed = function() {
  this.__configure_explanations();
  this.__convert_submit_buttons_to_anchors();
  new DatetimeHumanizer();
}

// Add dummy replacement for Firebug's console.log to prevent code that calls it
// from throwing an exception.
Initiator.prototype.__configure_console = function() {
  if(!window.console) window.console = { log: function() { } };
}

Initiator.prototype.__configure_explanations = function() {
  $('.explanation').each(function() {
    var e = $(this);
    var tooltip_content = e.html();
    e.text('?');
    e.moderatelyDampTip({content: tooltip_content});
  });
}

Initiator.prototype.__convert_submit_buttons_to_anchors = function() {
  var submit_buttons = $('input[type=submit]');
  submit_buttons.each(function() {
    var submit_button = $(this);
    var form = submit_button.parents('form');

    var anchor = $('<a/>').attr('href', form.attr('action')).html(submit_button.val());
    anchor.click(function() {
      form.submit();
      return false;
    });
    submit_button.replaceWith(anchor);
  });
}
