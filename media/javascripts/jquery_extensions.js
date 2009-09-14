// See:
//   * http://stackoverflow.com/questions/946534/insert-text-into-textarea-with-jquery
//   * http://laboratorium.0xab.cd/jquery/fieldselection/0.1.0/jquery-fieldselection.js
$.fn.extend({
  insertAtCaret: function(str) {
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
  }
});
