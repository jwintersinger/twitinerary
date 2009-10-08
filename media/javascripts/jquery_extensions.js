// See:
//   * http://stackoverflow.com/questions/946534/insert-text-into-textarea-with-jquery
//   * http://laboratorium.0xab.cd/jquery/fieldselection/0.1.0/jquery-fieldselection.js
jQuery.fn.insertAtCaret = function(str) {
  var self = this[0];

  // Every browser that doesn't suck (i.e., not IE).
  //   Need additional test in condition, for self.selectionStart evaluates
  //   to false when caret is at beginning of input box, when
  //   self.selectionStart = 0.
  // Note that the StackOverflow link above contained code that would
  // supposedly work for IE, but it only inserted at caret when the focus
  // was on the textarea when this function was called -- otherwise, it
  // simply prepended the text to the contents of the textarea. As the input
  // focus will usually be on the "shorten URL" input box when I call this
  // function, not on the textarea, I have jettisoned the IE-specific code so
  // that IE simply falls back on the (not quite desireable) appending code.
  if (self.selectionStart || self.selectionStart == 0) {
    var start = self.selectionStart;
    var end = self.selectionEnd;
    var old_scroll_top = self.scrollTop;

    self.value = self.value.substring(0, start) + str + self.value.substring(end, self.value.length);
    // If selectionStart not manually set, caret is automatically  positioned to end of selection.
    self.selectionStart = start + str.length;
    self.selectionEnd = start + str.length;
    // If scrollTop not set to old value, textarea's vertical scrolling position automatically reset to its top.
    self.scrollTop = old_scroll_top;

  // Unsupported browsers -- just append str.
  } else {
    self.value += str;
  }
};

$.extend($.ui.tabs.prototype, {
  // Returns -1 if not found. Using selectors rather than internal state of
  // object to find tabs is something of a hack, but it is less likely to break
  // with jQuery UI upgrades, as selectors are less likely to change than
  // internal state, given that people theme their interface via selectors.
  _get_index: function(selector) {
    // If I call from one of the below functions, return value is as expected.
    // If I call from external code, return value is always the value of
    // tabs.tabs(). As such, if I ever make this method public rather than
    // private, I must resolve this.
    return $('.ui-tabs-panel').index($(selector));
  },

  // Included remove() only works by index.
  remove_by_selector: function(selector) {
    var index = this._get_index(selector);
    if(index != -1) return this.remove(index);
  },

  // Refresh a tab if it is the currently-selected tab.
  reload_if_selected: function(selector) {
    var index = this._get_index(selector);
    // Do nothing unless target tab is currently selected.
    if(this.option('selected') != index) return;
    this.load(index);
  }
});

// Exceedingly simple tooltip. The previously-used Simpletip did not work if one
// switched away from its containing tab, then back to that tab -- in such an
// instance, the tooltip stopped functioning.
jQuery.fn.moderatelyDampTip = function(options) {
  if(!options.className) options.className = 'tooltip';
  if(!options.content)   options.content = 'I am moderately damp.';

  this.after('<p class="' + options.className + '">' + options.content + '</p>');
  var tooltip = this.next('.' + options.className);

  this.hover(function(event) {
    tooltip.css({left: event.pageX, top: event.pageY});
    tooltip.fadeIn();
  }, function() {
    tooltip.fadeOut();
  });
}
