$(document).ready(function() {
  new Initiator();
});

function Initiator() {
  this.__configure_console();

  if($('#authenticator').hasClass('authenticated')) new AuthenticatedInitiator(this);
  else                                              new UnauthenticatedInitiator(this);
}

// To be called by client initiators whenever a new tab (or whole new page) is loaded.
Initiator.prototype.on_tab_load = function() {
  this.__configure_explanations();
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
